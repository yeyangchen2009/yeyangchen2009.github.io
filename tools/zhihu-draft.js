#!/usr/bin/env node
/*
 * zhihu-draft.js —— 借已登录 Edge（CDP 9222）把知乎稿填成草稿
 *
 * 安全边界：只填内容、存草稿，绝不点「发布」。发布由用户亲自操作。
 *
 * 用法:
 *   node tools/zhihu-draft.js probe
 *       打开/复用知乎写文章页，探查标题框与正文编辑器，整页截图
 *   node tools/zhihu-draft.js drafts
 *       列出知乎草稿箱全部草稿（id / 标题 / 字数 / 图片数）
 *   node tools/zhihu-draft.js fill <md文件> <标题>
 *       新开草稿页注入标题与正文（md paste → 点「确认并解析」→ 等图上传），
 *       随后核对草稿箱：若自动化过程产生多份草稿，保留图片完整的一份，
 *       其余按真实 ID 调 DELETE 清理，最后截图并关闭工作标签。
 *
 * 背景：知乎草稿箱前端把 19 位长 ID 当 Number 处理，末位舍入（>2^53），
 * 列表项自带的删除/编辑链接全部指向错误 ID（404）。本脚本一律从
 * /api/articles/my_drafts 的原始 JSON 文本中正则提取 ID（不经 JSON.parse），
 * 删除直接 fetch /api/articles/<真实id>/draft。
 */
'use strict';

const fs = require('fs');
const path = require('path');
const http = require('http');

const ROOT = path.dirname(path.dirname(__filename));
const WRITE_URL = 'https://zhuanlan.zhihu.com/write';
const sleep = ms => new Promise(r => setTimeout(r, ms));

function getJson(pathname) {
    return new Promise((resolve, reject) => {
        http.get({ host: '127.0.0.1', port: 9222, path: pathname }, res => {
            let d = '';
            res.on('data', c => { d += c; });
            res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { reject(e); } });
        }).on('error', reject);
    });
}

// /json/close/* 返回的是纯文本（"Target is closing"），不能按 JSON 解析
function getText(pathname) {
    return new Promise((resolve, reject) => {
        http.get({ host: '127.0.0.1', port: 9222, path: pathname }, res => {
            let d = '';
            res.on('data', c => { d += c; });
            res.on('end', () => resolve(d.trim()));
        }).on('error', reject);
    });
}

// 新版 Edge/Chrome 开标签走 PUT /json/new?<url>
function newTab(url) {
    return new Promise((resolve, reject) => {
        const req = http.request({
            host: '127.0.0.1', port: 9222,
            path: '/json/new?' + encodeURIComponent(url), method: 'PUT',
        }, res => {
            let d = '';
            res.on('data', c => { d += c; });
            res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { reject(e); } });
        });
        req.on('error', reject);
        req.end();
    });
}

async function connect({ fresh = false } = {}) {
    let version;
    try {
        version = await getJson('/json/version');
    } catch {
        console.error('连不上 127.0.0.1:9222，请先用调试端口启动 Edge');
        process.exit(1);
    }
    // fresh=true：总是新开 write 标签（每篇一个独立草稿）；否则复用已有 write 标签
    let target = null;
    if (!fresh) {
        const list = await getJson('/json/list');
        target = list.find(t => t.type === 'page' && t.url.includes('zhuanlan.zhihu.com/write'));
    }
    if (!target) target = await newTab(WRITE_URL);

    return await attach(target);
}

async function attach(target) {
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((res, rej) => {
        ws.addEventListener('open', res);
        ws.addEventListener('error', rej);
    });

    let mid = 0;
    const pend = new Map();
    ws.addEventListener('message', e => {
        const m = JSON.parse(e.data);
        if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    });
    const send = (method, params = {}) => new Promise((resolve, reject) => {
        const id = ++mid;
        pend.set(id, msg => (msg.error ? reject(new Error(method + ': ' + JSON.stringify(msg.error))) : resolve(msg.result)));
        ws.send(JSON.stringify({ id, method, params }));
    });
    const evalJs = async expr => {
        const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
        if (r.exceptionDetails) throw new Error('JS: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
        return r.result.value;
    };

    await send('Page.enable');
    await send('Runtime.enable');

    return {
        target,
        async navigate(url) {
            await send('Page.navigate', { url });
            await sleep(6000);
        },
        eval: evalJs,
        async shot(outPath) {
            const r = await send('Page.captureScreenshot', { format: 'png' });
            fs.writeFileSync(outPath, Buffer.from(r.data, 'base64'));
        },
        close() { try { ws.close(); } catch { /* ignore */ } },
    };
}

// ---- 草稿箱 API -----------------------------------------------------------------

// 分页拉 my_drafts 的原始 JSON 文本，正则提取（不 JSON.parse，避免长 ID 丢精度）
const LIST_DRAFTS_EXPR = `(async () => {
    const out = [];
    for (let off = 0; off < 200; off += 10) {
        const u = 'https://zhuanlan.zhihu.com/api/articles/my_drafts?limit=10&offset=' + off
                + '&include=' + encodeURIComponent('$.data[*].schedule');
        const t = await (await fetch(u, { credentials: 'include' })).text();
        // 每个草稿对象以 "content_length" 开头，按此切块（id 在对象后部）
        const marks = [...t.matchAll(/"content_length"\\s*:\\s*(\\d+)/g)]
            .map(m => ({ start: m.index, len: +m[1] }));
        for (let i = 0; i < marks.length; i++) {
            const seg = t.slice(marks[i].start, marks[i + 1] ? marks[i + 1].start : t.length);
            const pick = re => { const m = seg.match(re); return m ? m[1] : ''; };
            const id = pick(/"id"\\s*:\\s*(\\d+)/);
            if (!id) continue; // 非草稿对象（嵌套 schedule 等）
            let title = pick(/"title"\\s*:\\s*"((?:[^"\\\\]|\\\\.)*)"/);
            try { title = JSON.parse('"' + title + '"'); } catch { /* 解码失败保留原文 */ }
            out.push({
                id,
                title,
                len: marks[i].len,
                updated: +pick(/"updated"\\s*:\\s*(\\d+)/) || 0,
                imgs: (seg.match(/zhimg\\.com/g) || []).length,
            });
        }
        if (/"is_end"\\s*:\\s*true/.test(t)) break;
    }
    return out;
})()`;

async function listDrafts(c) {
    return await c.eval(LIST_DRAFTS_EXPR);
}

// 按真实 ID 删除草稿（200=成功）
async function deleteDraft(c, id) {
    return await c.eval(`(async () => {
        const m = document.cookie.match(/(?:^|;\\s*)_xsrf=([^;]+)/);
        const xsrf = m ? decodeURIComponent(m[1]) : '';
        const r = await fetch('https://zhuanlan.zhihu.com/api/articles/${id}/draft', {
            method: 'DELETE',
            headers: { 'x-xsrftoken': xsrf },
            credentials: 'include',
        });
        return r.status;
    })()`);
}

// 找到带「确认并解析」浮条的草稿（倒序＝最新草稿优先），点解析，等图片上传
async function cmdParse() {
    const list = await getJson('/json/list');
    const writes = list.filter(t => t.type === 'page' && t.url.includes('zhuanlan.zhihu.com/write'));

    let chosen = null;
    const opened = [];
    for (const t of writes.slice().reverse()) {
        const a = await attach(t);
        opened.push(a);
        if (await a.eval(`document.body.innerText.includes('确认并解析')`)) { chosen = a; break; }
    }
    for (const a of opened) if (a !== chosen) a.close();
    if (!chosen) { console.error('没找到带「确认并解析」的草稿标签'); process.exit(1); }

    const click = await chosen.eval(`(() => {
        const els = [...document.querySelectorAll('button,span,a,div')]
            .filter(e => e.textContent.trim() === '确认并解析' && e.children.length === 0);
        if (!els.length) return { found: false };
        const el = els[els.length - 1];
        el.scrollIntoView({ block: 'center' });
        el.click();
        return { found: true, tag: el.tagName, cls: (el.className || '').toString().slice(0, 60) };
    })()`);
    console.log('点击结果：' + JSON.stringify(click));
    if (!click.found) process.exit(1);

    // 等 md 解析＋图片插入：图片数连续 5 次稳定即收尾（最多 45s）
    let last = -1, stable = 0, nimg = 0;
    for (let i = 0; i < 45; i++) {
        nimg = await chosen.eval(
            `document.querySelector('.public-DraftEditor-content').querySelectorAll('img').length`);
        if (nimg === last && nimg > 0) stable++;
        else stable = 0;
        last = nimg;
        if (stable >= 5) break;
        await sleep(1000);
    }
    console.log('解析后正文图片数：' + nimg);
    await sleep(2000);
    const out = path.join(ROOT, 'Temp', 'zhihu-parsed.png');
    await chosen.shot(out);
    console.log('解析后截图 -> ' + out);
    chosen.close();
}

async function cmdProbe() {
    const c = await connect();
    if (!c.target.url.includes('/write')) await c.navigate(WRITE_URL);
    else await sleep(2000);

    const info = await c.eval(`(() => {
        const desc = el => ({
            tag: el.tagName,
            cls: (el.className && el.className.toString().slice(0, 80)) || '',
            role: el.getAttribute('role') || '',
            placeholder: el.getAttribute('placeholder') || '',
            editable: el.isContentEditable,
            text: (el.textContent || '').slice(0, 30),
        });
        return {
            url: location.href,
            title: document.title,
            textareas: [...document.querySelectorAll('textarea')].map(desc),
            inputs: [...document.querySelectorAll('input[type=text]')].map(desc),
            editables: [...document.querySelectorAll('[contenteditable=""],[contenteditable=true]')].map(desc),
            draftHint: (document.body.innerText.match(/[^。\\n]*(草稿|保存)[^。\\n]*/g) || []).slice(0, 5),
        };
    })()`);
    console.log(JSON.stringify(info, null, 2));

    const out = path.join(ROOT, 'Temp', 'zhihu-write.png');
    await c.shot(out);
    console.log('布局截图 -> ' + out);
}

async function cmdDrafts() {
    const c = await connect();
    const drafts = await listDrafts(c);
    for (const d of drafts) {
        console.log(`${d.id}  ${d.imgs}图 ${String(d.len).padStart(6)}字  ${d.title.slice(0, 50)}`);
    }
    console.log('共 ' + drafts.length + ' 份');
    c.close();
}

async function cmdFill(file, title) {
    const raw = fs.readFileSync(file, 'utf-8');
    const isMd = /\.md$/i.test(file);
    const c = await connect({ fresh: true });
    await sleep(3500); // 等新草稿页加载、初始草稿落盘

    // 先探查，拿到标题框与正文框选择器
    const probe = await c.eval(`(() => {
        const titleEl = document.querySelector('textarea') ;
        const bodyEl = document.querySelector('[contenteditable=true],[contenteditable=""]');
        return {
            hasTitle: !!titleEl, titleCls: titleEl?.className || '',
            hasBody: !!bodyEl, bodyCls: bodyEl?.className || '',
        };
    })()`);
    console.log('编辑器探查：', JSON.stringify(probe));
    if (!probe.hasTitle || !probe.hasBody) {
        console.error('没找到标题框或正文框，先跑 probe 看结构');
        process.exit(1);
    }

    // 注入前的草稿箱快照（新标签的初始草稿此刻应已在列表中）
    const before = await listDrafts(c);
    const beforeIds = new Set(before.map(d => d.id));
    console.log('注入前草稿数：' + before.length);

    // 注入正文：合成 paste。
    //  .md -> 只带 text/plain（Markdown 模式自行解析，含图片 URL 上传，同手动粘贴）
    //  .html -> 带 text/html（格式完美，但 Draft.js 丢弃外链图片）
    const bodyExpr = `(async () => {
        const editor = document.querySelector('[contenteditable=true],[contenteditable=""]');
        editor.focus();
        const isMd = ${isMd};
        const content = ${JSON.stringify(raw)};
        const dt = new DataTransfer();
        if (isMd) dt.setData('text/plain', content);
        else { dt.setData('text/html', content); dt.setData('text/plain', ''); }
        const ev = new ClipboardEvent('paste', { bubbles: true, cancelable: true });
        // ClipboardEvent 的 clipboardData 只读，靠 defineProperty 塞进 DataTransfer
        Object.defineProperty(ev, 'clipboardData', { value: dt });
        editor.dispatchEvent(ev);
        await new Promise(r => setTimeout(r, 2000));
        return { len: editor.innerText.length, imgs: editor.querySelectorAll('img').length };
    })()`;
    const bodyRes = await c.eval(bodyExpr);
    console.log('正文注入结果：', JSON.stringify(bodyRes));

    // 标题：聚焦标题框后用原生 setter + input 事件
    const titleExpr = `(() => {
        const ta = document.querySelector('textarea');
        ta.focus();
        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, ${JSON.stringify(title)});
        ta.dispatchEvent(new Event('input', { bubbles: true }));
        return ta.value;
    })()`;
    const titleRes = await c.eval(titleExpr);
    console.log('标题注入：' + titleRes);

    // md 模式：浮条「确认并解析」是临时的，注入后立刻点，再等图片插入
    let nimg = 0;
    if (isMd) {
        await sleep(800);
        const click = await c.eval(`(() => {
            const els = [...document.querySelectorAll('button,span,a,div')]
                .filter(e => e.textContent.trim() === '确认并解析' && e.children.length === 0);
            if (!els.length) return { found: false };
            const el = els[els.length - 1];
            el.scrollIntoView({ block: 'center' });
            el.click();
            return { found: true };
        })()`);
        console.log('确认并解析：' + JSON.stringify(click));
        if (click.found) {
            let last = -1, stable = 0;
            for (let i = 0; i < 60; i++) {
                nimg = await c.eval(
                    `document.querySelector('.public-DraftEditor-content').querySelectorAll('img').length`);
                if (nimg === last && nimg > 0) stable++;
                else stable = 0;
                last = nimg;
                if (stable >= 5) break;
                await sleep(1000);
            }
            console.log('解析后正文图片数：' + nimg);
        }
    }

    // 等所有新草稿保存落盘，再核对草稿箱
    await sleep(6000);
    const after = await listDrafts(c);
    const freshOnes = after.filter(d => !beforeIds.has(d.id) && d.title === title);
    console.log('本次新增草稿：' + JSON.stringify(
        freshOnes.map(d => ({ id: d.id, len: d.len, imgs: d.imgs }))));

    // 保留稿：新增稿中图片最多的（半成品 0 图）；没有新增则取同标题最新稿
    let keeper;
    if (freshOnes.length) {
        keeper = freshOnes.slice().sort((a, b) => b.imgs - a.imgs || b.updated - a.updated)[0];
        for (const d of freshOnes) {
            if (d.id === keeper.id) continue;
            const st = await deleteDraft(c, d.id);
            console.log('清理重复草稿 ' + d.id + ' -> ' + st);
        }
    } else {
        keeper = after.filter(d => d.title === title).sort((a, b) => b.updated - a.updated)[0];
    }
    console.log('保留草稿：' + JSON.stringify(
        { id: keeper && keeper.id, len: keeper && keeper.len, imgs: keeper && keeper.imgs }));

    await sleep(2000);
    const out = path.join(ROOT, 'Temp', 'zhihu-draft.png');
    await c.shot(out);
    console.log('草稿截图 -> ' + out);

    // 关闭工作标签（草稿已自动保存；保留稿在草稿箱中）
    const closed = await getText('/json/close/' + c.target.id);
    console.log('工作标签：' + closed);
}

async function main() {
    const [cmd, a, b] = process.argv.slice(2);
    if (cmd === 'probe') await cmdProbe();
    else if (cmd === 'parse') await cmdParse();
    else if (cmd === 'drafts') await cmdDrafts();
    else if (cmd === 'fill') {
        if (!a || !b) { console.error('用法: fill <md文件> <标题>'); process.exit(2); }
        await cmdFill(a, b);
    } else {
        console.error('未知命令：' + cmd + '（probe | parse | drafts | fill）');
        process.exit(2);
    }
    process.exit(0); // WebSocket 保持事件循环，主动退出
}

main().catch(e => { console.error(String(e.stack || e)); process.exit(1); });
