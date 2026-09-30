#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Markdown 草稿同步到飞书知识库（手机端审稿）。

封装已登录的 lark-cli，每篇文章：
  确保知识库存在 → 删除同名旧节点 → 导入为在线文档(docx) → 挂到知识库
  → 把导入产生的"失效图片块"替换为本地实拍图
  → 把 mermaid 代码块替换为飞书画板（自动渲染）。
同名替换、内容始终最新（幂等）。

为什么需要后处理：飞书 md 导入不会内嵌本地图（生成的是占位图块），
也不会渲染 mermaid（保留成代码块）。所以导入后用块级替换补齐。

认证由 lark-cli 统一管理：先 `lark-cli auth status`，未登录则 `lark-cli auth login`。

源稿图片约定：正文写  ![alt](/screenshots/x.png)，本地对应 static/screenshots/x.png。

用法：
  python tools/feishu-sync.py <a.md> [b.md ...]
  python tools/feishu-sync.py --space "知识库名" <a.md>
"""

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ENV_FILE = os.path.join(HERE, '.feishu.env')
STATE_FILE = os.path.join(HERE, '.feishu-state.json')
DEFAULT_SPACE = '中国佛教史·审稿'
IMG_WIDTH = '620'


def load_env():
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):
        with io.open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                env.setdefault(k.strip(), v.strip())
    return env


ENV = load_env()
SPACE_NAME = ENV.get('FEISHU_SPACE_NAME', DEFAULT_SPACE)


def _find_node_runner():
    """定位 node.exe 与 lark-cli 的 JS 入口（绕过 .cmd，避免特殊字符被 cmd 解析）。"""
    lark_cmd = shutil.which('lark-cli.cmd') or shutil.which('lark-cli')
    node_dir = os.path.dirname(lark_cmd) if lark_cmd else ''
    node = os.path.join(node_dir, 'node.exe')
    if not os.path.exists(node):
        node = shutil.which('node')
    runjs = os.path.join(node_dir, 'node_modules', '@larksuite', 'cli', 'scripts', 'run.js')
    return node, runjs


NODE, RUNJS = _find_node_runner()


def lark(*args, expect_ok=True):
    """在仓库根目录调用 lark-cli（node 直跑 JS 入口），返回 data。

    expect_ok=False 时不要求顶层 ok 字段（用于 auth status），返回整个 payload。
    """
    if not NODE or not os.path.exists(RUNJS):
        raise RuntimeError('找不到 node 或 lark-cli JS 入口，请确认 lark-cli 已正确安装')
    p = subprocess.run([NODE, RUNJS, *args], capture_output=True, text=True,
                       encoding='utf-8', cwd=REPO)
    out = (p.stdout or '').strip()
    try:
        payload = json.loads(out)
    except ValueError:
        raise RuntimeError('lark-cli 输出非 JSON：%s %s' % (out[:300], (p.stderr or '')[:300]))
    if not expect_ok:
        return payload
    if not payload.get('ok'):
        raise RuntimeError('lark-cli 失败：%s' % json.dumps(payload.get('error', payload), ensure_ascii=False)[:400])
    return payload.get('data', {})


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(io.open(STATE_FILE, encoding='utf-8'))
        except ValueError:
            pass
    return {}


def save_state(state):
    with io.open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def ensure_space():
    state = load_state()
    if state.get('space_name') == SPACE_NAME and state.get('space_id'):
        return state['space_id']
    data = lark('wiki', '+space-list')
    sid = None
    for sp in data.get('spaces', []):
        if sp.get('name') == SPACE_NAME:
            sid = sp['space_id']
            break
    if not sid:
        data = lark('wiki', '+space-create', '--name', SPACE_NAME,
                    '--description', '中国佛教史系列草稿·手机端审稿')
        sid = data['space_id']
        print('  已创建知识库：%s' % sid)
    save_state({'space_name': SPACE_NAME, 'space_id': sid})
    return sid


# --- 源稿解析：图片本地路径顺序、mermaid 源码顺序 ---

RE_SRC_IMG = re.compile(r'!\[[^\]]*\]\((/screenshots/[^)]+)\)')
RE_MMD_FENCE = re.compile(r'```mermaid\s*\n(.*?)```', re.S)


def parse_source_assets(body):
    imgs = [m.group(1) for m in RE_SRC_IMG.finditer(body)]
    mmds = [m.group(1).strip('\n') for m in RE_MMD_FENCE.finditer(body)]
    return imgs, mmds


def split_frontmatter(text):
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            meta = {}
            for line in text[3:end].strip().splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
            return meta, text[end + 4:].lstrip('\n')
    return {}, text


# --- 导入后文档块解析 ---

# 按文档顺序匹配：导入产生的占位图块 / mermaid 生成的 pre 块
# pre 带 lang：飞书不认识 mermaid 语言，```mermaid 围栏被映射成 lang="Plaintext"；
# 而正文里讲解白板用的 HTML 示例围栏是 lang="HTML"，借此区分、避免误抓示例块。
RE_DOC_BLOCK = re.compile(
    r'<img id="([^"]+)"[^>]*?name="default\.png"[^>]*?/>'
    r'|<pre id="([^"]+)"[^>]*lang="([^"]*)"[^>]*><code>(.*?)</code></pre>', re.S)


def parse_doc_blocks(content):
    """返回 (img_ids 顺序, mmd_pre_ids 顺序)。"""
    img_ids, pre_ids = [], []
    for m in RE_DOC_BLOCK.finditer(content):
        if m.group(1):
            img_ids.append(m.group(1))
        else:
            lang, code = m.group(3), m.group(4)
            # 只认被飞书降级成 Plaintext 的 mermaid 块（含 init 或 flowchart 关键字）
            if lang == 'Plaintext' and (
                    '%%{init' in code or re.search(r'flowchart\s+(TD|LR|TB)', code)):
                pre_ids.append(m.group(2))
    return img_ids, pre_ids


def check_whiteboard_compat(code):
    """飞书白板兼容性检查：实测其解析器不支持边连接 subgraph（进入或出发皆报
    Whiteboard content parse failed）。发现即打印明确警告，提示改连子图内节点。"""
    sub_ids = re.findall(r'^\s*subgraph\s+([A-Za-z0-9_]+)', code, re.M)
    if not sub_ids:
        return
    for i, line in enumerate(code.splitlines(), 1):
        if line.lstrip().startswith('subgraph'):
            continue
        if not re.search(r'(--?>|==>)', line):
            continue
        # 去掉节点标签与边标签后，剩余的裸 id 即端点
        bare = re.sub(r'\[.*?\]|".*?"', '', line)
        tokens = set(re.findall(r'[A-Za-z0-9_]+', bare))
        bad = [s for s in sub_ids if s in tokens]
        if bad:
            print('  ! 第 %d 行边连接了 subgraph（%s）：飞书白板不支持，'
                  '请改连子图内的具体节点' % (i, ', '.join(bad)))


def mmd_to_whiteboard(code):
    """mermaid 源码 → 飞书画板 XML：去 init 指令、把 <br/> 换成空格。"""
    check_whiteboard_compat(code)
    lines = [l for l in code.splitlines() if not l.strip().startswith('%%{')]
    s = '\n'.join(lines).strip()
    s = s.replace('<br />', ' ').replace('<br/>', ' ').replace('<br>', ' ')
    return '<whiteboard type="mermaid">\n%s\n</whiteboard>' % s


def block_replace(doc, block_id, xml):
    lark('docs', '+update', '--doc', doc, '--command', 'block_replace',
         '--block-id', block_id, '--content', xml)


def sync_file(sid, path):
    text = io.open(path, 'r', encoding='utf-8').read()
    meta, body = split_frontmatter(text)
    title = meta.get('title') or os.path.splitext(os.path.basename(path))[0]
    src_imgs, src_mmds = parse_source_assets(body)
    print('● 同步：%s（图 %d 张，mermaid %d 个）' % (title, len(src_imgs), len(src_mmds)))

    for n in lark('wiki', '+node-list', '--space-id', sid, '--page-all').get('nodes', []):
        if n.get('title') == title:
            lark('wiki', '+node-delete', '--node-token', n['node_token'],
                 '--obj-type', 'docx', '--space-id', sid, '--yes')
            print('  已删除同名旧节点：%s' % n['node_token'])

    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False,
                                     dir=os.path.join(REPO, 'Temp'),
                                     encoding='utf-8') as tf:
        tf.write(body)
        tmp = tf.name
    try:
        data = lark('drive', '+import', '--file', os.path.relpath(tmp, REPO),
                    '--type', 'docx', '--name', title)
        doc = data['token']
        url = data.get('url', '')
        lark('wiki', '+move', '--obj-type', 'docx', '--obj-token', doc,
             '--target-space-id', sid)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

    # 后处理：替换图片块、mermaid 块
    content = lark('docs', '+fetch', '--doc', doc,
                   '--detail', 'with-ids')['document']['content']
    img_ids, pre_ids = parse_doc_blocks(content)

    if len(img_ids) != len(src_imgs):
        print('  ! 图片块数(%d)与源稿(%d)不一致，按可配对数替换' % (len(img_ids), len(src_imgs)))
    for bid, src in zip(img_ids, src_imgs):
        local = os.path.join('static', src.lstrip('/'))
        block_replace(doc, bid, '<img path="@./%s" width="%s"/>' % (local.replace('\\', '/'), IMG_WIDTH))
    print('  已替换图片 %d 张' % min(len(img_ids), len(src_imgs)))

    if len(pre_ids) != len(src_mmds):
        print('  ! mermaid 块数(%d)与源稿(%d)不一致，按可配对数替换' % (len(pre_ids), len(src_mmds)))
    for bid, code in zip(pre_ids, src_mmds):
        block_replace(doc, bid, mmd_to_whiteboard(code))
    print('  已替换 mermaid 画板 %d 个' % min(len(pre_ids), len(src_mmds)))

    print('  已入库：%s' % url)
    return title, url


def main(argv):
    args = argv[1:]
    global SPACE_NAME
    if '--space' in args:
        i = args.index('--space')
        SPACE_NAME = args[i + 1]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 1
    status = lark('auth', 'status', expect_ok=False)
    user = status.get('identities', {}).get('user', {})
    # token 状态：valid/ready 正常；needs_refresh 仍 available，
    # lark-cli 会在下一次用户 API 调用时自动刷新，同样放行。
    utoken = user.get('tokenStatus') or user.get('status')
    if not user.get('available') or utoken not in ('valid', 'ready', 'needs_refresh'):
        print('lark-cli 用户身份无效，请先运行 lark-cli auth login')
        return 2
    sid = ensure_space()
    done = []
    for p in args:
        done.append(sync_file(sid, p))
    print('\n完成 %d 篇 → 知识库「%s」，手机飞书「知识库」查看。' % (len(done), SPACE_NAME))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
