#!/usr/bin/env node
/*
 * mermaid-to-png.js —— 把 markdown 里的 mermaid 代码块批量渲染成暗色 PNG
 *
 * 渲染用博客线上同款 mermaid 库（static/mermaid.min.js）；源块自带的
 * %%{init}%% 指令原样保留，出图与博客页面一致。图片自带深色底，
 * 适配知乎等白底平台。
 *
 * 用法:
 *   node tools/mermaid-to-png.js drafts/post-70.md
 *   node tools/mermaid-to-png.js drafts/post-69.md drafts/post-70.md --rewrite-dir Temp/zhihu-work
 *
 * 图片输出: static/screenshots/zhihu-mermaid/post-<N>-<K>.png
 * --rewrite-dir <dir>: 同时输出替换后的 md 副本（mermaid 块 -> 图片引用）
 */
'use strict';

const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');

const ROOT = path.dirname(path.dirname(__filename));
const MERMAID_JS = path.join(ROOT, 'static', 'mermaid.min.js');
const IMG_DIR = path.join(ROOT, 'static', 'screenshots', 'zhihu-mermaid');
const IMG_URL_PREFIX = '/screenshots/zhihu-mermaid';
const HTML_TMP = path.join(ROOT, 'Temp', 'mermaid-pages');

const sleep = ms => new Promise(r => setTimeout(r, ms));

function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function resolveBrowser() {
    if (process.env.CDP_BROWSER) return process.env.CDP_BROWSER;
    const wins = [
        'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
        'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
        'C:/Program Files/Google/Chrome/Application/chrome.exe',
        'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
    ];
    return wins.find(p => { try { fs.accessSync(p); return true; } catch { return false; } }) || wins[0];
}

async function launchBrowser() {
    const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'mermaid-render-'));
    const args = [
        '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
        '--no-proxy-server', '--ignore-certificate-errors',
        '--remote-debugging-port=0', '--remote-allow-origins=*',
        '--user-data-dir=' + profile, 'about:blank',
    ];
    const child = spawn(resolveBrowser(), args, { stdio: ['ignore', 'ignore', 'pipe'] });
    const port = await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('等待 DevTools 端口超时')), 20000);
        child.stderr.on('data', d => {
            const m = String(d).match(/DevTools listening on ws:\/\/[^\s:]+:(\d+)\//);
            if (m) { clearTimeout(timer); resolve(+m[1]); }
        });
        child.on('exit', code => { clearTimeout(timer); reject(new Error('浏览器提前退出，code=' + code)); });
    });
    return { child, port, profile };
}

function killBrowser(child) {
    try { child.kill(); } catch { /* ignore */ }
    try { spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' }); } catch { /* ignore */ }
}

function getJson(port, urlPath) {
    return new Promise((resolve, reject) => {
        http.get({ host: '127.0.0.1', port, path: urlPath }, res => {
            let d = '';
            res.on('data', c => { d += c; });
            res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { reject(e); } });
        }).on('error', reject);
    });
}

// 从 md 提取 mermaid 块；返回 [{code, start, end}]
function extractMermaid(text) {
    const out = [];
    const re = /^```mermaid\s*\n([\s\S]*?)\n```\s*$/gm;
    let m;
    while ((m = re.exec(text))) {
        out.push({ code: m[1], start: m.index, end: m.index + m[0].length });
    }
    return out;
}

function buildHtml(blocks) {
    const charts = blocks.map(b =>
        '<div class="chart"><pre class="mermaid">' + escapeHtml(b.code) + '</pre></div>').join('\n');
    return `<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html,body{margin:0;padding:0;background:#0d1117;}
  .chart{background:#0d1117;padding:26px 30px;width:1040px;box-sizing:content-box;}
</style></head>
<body>
${charts}
<script src="file:///${MERMAID_JS.replace(/\\/g, '/')}"><\/script>
<script>
  mermaid.initialize({ startOnLoad: false, theme: 'dark' });
  (async () => {
    try {
      await mermaid.run({ querySelector: '.mermaid' });
    } catch (e) { document.title = 'RENDER_ERROR:' + String(e); }
  })();
<\/script>
</body></html>`;
}

async function processFile(file, rewriteDir, api) {
    const number = path.basename(file).match(/post-(\d+)\.md$/)?.[1];
    if (!number) throw new Error('文件名需为 post-N.md：' + file);
    const text = fs.readFileSync(file, 'utf-8');
    const blocks = extractMermaid(text);
    if (!blocks.length) {
        console.log('#' + number + ' 无 mermaid 块，跳过');
        return 0;
    }

    const htmlPath = path.join(HTML_TMP, 'post-' + number + '.html');
    fs.mkdirSync(HTML_TMP, { recursive: true });
    fs.writeFileSync(htmlPath, buildHtml(blocks), 'utf-8');

    await api.navigate('file:///' + htmlPath.replace(/\\/g, '/'));
    // 轮询：每个容器都有 svg
    const ready = await api.waitFor(
        `(() => {
           const charts = document.querySelectorAll('.chart');
           const svgs = document.querySelectorAll('.chart svg');
           if (document.title.startsWith('RENDER_ERROR')) throw new Error(document.title);
           return svgs.length === charts.length && charts.length === ${blocks.length};
         })()`, 90000);
    if (!ready) throw new Error('#' + number + ' mermaid 渲染超时');
    await sleep(400);

    const rects = await api.eval(
        `[...document.querySelectorAll('.chart')].map(c => {
           const r = c.getBoundingClientRect();
           return { x: Math.round(r.left), y: Math.round(r.top + window.scrollY),
                    width: Math.round(r.width), height: Math.round(r.height) };
         })`);

    fs.mkdirSync(IMG_DIR, { recursive: true });
    const urls = [];
    for (let i = 0; i < rects.length; i++) {
        const r = rects[i];
        const imgName = 'post-' + number + '-' + (i + 1) + '.png';
        await api.shot(path.join(IMG_DIR, imgName), r);
        urls.push(IMG_URL_PREFIX + '/' + imgName);
        console.log('  #' + number + ' 图' + (i + 1) + ' -> ' + imgName + '（' + r.width + '×' + r.height + '）');
    }

    if (rewriteDir) {
        fs.mkdirSync(rewriteDir, { recursive: true });
        let out = text, offset = 0;
        blocks.forEach((b, i) => {
            const repl = '\n![图示' + (i + 1) + '](' + urls[i] + ')\n';
            out = out.slice(0, b.start + offset) + repl + out.slice(b.end + offset);
            offset += repl.length - (b.end - b.start);
        });
        fs.writeFileSync(path.join(rewriteDir, path.basename(file)), out, 'utf-8');
        console.log('  改写副本 -> ' + path.relative(ROOT, path.join(rewriteDir, path.basename(file))));
    }
    return blocks.length;
}

async function makeApi(port) {
    const list = await getJson(port, '/json/list');
    const page = list.find(t => t.type === 'page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
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
        if (r.exceptionDetails) throw new Error('JS 执行失败: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
        return r.result.value;
    };

    await send('Page.enable');
    await send('Runtime.enable');
    await send('Emulation.setDeviceMetricsOverride', {
        width: 1200, height: 900, deviceScaleFactor: 2, mobile: false,
    });

    let navigated;
    send('Page.enable').then(() => {});
    ws.addEventListener('message', e => {
        const m = JSON.parse(e.data);
        if (m.method === 'Page.loadEventFired' && navigated) navigated();
    });

    return {
        async navigate(url) {
            await new Promise(resolve => { navigated = resolve; send('Page.navigate', { url }); });
            navigated = null;
        },
        eval: evalJs,
        async waitFor(expr, timeoutMs) {
            const deadline = Date.now() + timeoutMs;
            while (Date.now() < deadline) {
                if (await evalJs(expr)) return true;
                await sleep(300);
            }
            return false;
        },
        async shot(outPath, clip) {
            const r = await send('Page.captureScreenshot', {
                format: 'png', captureBeyondViewport: true,
                clip: { x: clip.x, y: clip.y, width: clip.width, height: clip.height, scale: 1 },
            });
            fs.writeFileSync(outPath, Buffer.from(r.data, 'base64'));
        },
    };
}

async function main() {
    const argv = process.argv.slice(2);
    const files = [];
    let rewriteDir = null;
    for (let i = 0; i < argv.length; i++) {
        if (argv[i] === '--rewrite-dir') rewriteDir = path.resolve(argv[++i]);
        else files.push(path.resolve(argv[i]));
    }
    if (!files.length) { console.error('用法: node tools/mermaid-to-png.js <md...> [--rewrite-dir <dir>]'); process.exit(2); }
    if (!fs.existsSync(MERMAID_JS)) { console.error('找不到 mermaid 库：' + MERMAID_JS); process.exit(2); }

    const { child, port } = await launchBrowser();
    let total = 0;
    try {
        const api = await makeApi(port);
        for (const f of files) {
            console.log('处理 ' + path.relative(ROOT, f) + '：');
            total += await processFile(f, rewriteDir, api);
        }
    } finally {
        killBrowser(child);
    }
    console.log('完成，共渲染 ' + total + ' 张图');
}

main().catch(e => { console.error(String(e.stack || e)); process.exit(1); });
