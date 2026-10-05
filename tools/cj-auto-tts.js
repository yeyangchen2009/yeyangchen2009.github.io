#!/usr/bin/env node
/*
 * cj-auto-tts.js —— 蝉镜「网页试听」一键自动化（心经 cj-fill2 + cj-audition4 整合版）
 *
 * 流程：导航到 creation-audio 页 → 等编辑器 → 物理点编辑器/Ctrl+A/Delete/贴稿
 *       → 点试听（若只预热未发 create_v3，隔几秒自动补点第二次）
 *       → 轮询 audio.src 与网络请求，抓 res.chanjing.cc 的新 wav → 下载落本地。
 * 只出音频、0 蝉豆，不碰 create_video。
 *
 * 用法:
 *   node tools/cj-auto-tts.js --port 10127 \
 *     --url 'https://www.chanjing.cc/creation-audio?id=C-xxx&type=custom' \
 *     --text Temp/zhushixing-tts.txt --out Temp/zhushixing-yeyang.wav
 */
'use strict';
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

function parseArgs(argv) {
    const o = { port: 10127 };
    for (let i = 0; i < argv.length; i++) {
        const t = argv[i];
        if (t === '--port') o.port = +argv[++i];
        else if (t === '--url') o.url = argv[++i];
        else if (t === '--text') o.textFile = argv[++i];
        else if (t === '--out') o.out = argv[++i];
    }
    if (!o.url || !o.textFile || !o.out) {
        console.error('缺参数：需要 --url --text --out'); process.exit(2);
    }
    return o;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
function getJson(port, p) {
    return new Promise((res, rej) => {
        http.get({ host: '127.0.0.1', port, path: p }, r => {
            let d = ''; r.on('data', c => d += c); r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } });
        }).on('error', rej);
    });
}

async function main() {
    const opt = parseArgs(process.argv.slice(2));
    const text = fs.readFileSync(opt.textFile, 'utf8').trim();
    console.log('文本字数：%d', text.length);

    const list = await getJson(opt.port, '/json/list');
    let page = list.find(t => t.type === 'page' && /chanjing/.test(t.url)) || list.find(t => t.type === 'page');
    if (!page) throw new Error('找不到 page');
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });

    let mid = 0;
    const pend = new Map();
    const reqs = [];
    ws.addEventListener('message', e => {
        const m = JSON.parse(e.data);
        if (m.method === 'Network.requestWillBeSent') {
            const p = m.params;
            reqs.push({ url: p.request.url, method: p.request.method, type: p.type });
        }
        if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    });
    const send = (method, params = {}) => new Promise((resolve, reject) => {
        const id = ++mid;
        pend.set(id, x => x.error ? reject(new Error(method + ': ' + JSON.stringify(x.error))) : resolve(x.result));
        ws.send(JSON.stringify({ id, method, params }));
    });
    const ev = async expr => {
        const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
        if (r.exceptionDetails) throw new Error('JS: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
        return r.result.value;
    };
    const clickAt = async (x, y) => {
        await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x, y });
        await send('Input.dispatchMouseEvent', { type: 'mousePressed', x, y, button: 'left', clickCount: 1 });
        await sleep(60);
        await send('Input.dispatchMouseEvent', { type: 'mouseReleased', x, y, button: 'left', clickCount: 1 });
    };
    const clickSelector = async expr => {
        const r = await ev(expr);
        if (!r) return false;
        await clickAt(r.x, r.y);
        return true;
    };

    await send('Page.enable');
    await send('Network.enable');

    // --- 1. 导航到 creation-audio 页 ---
    console.log('导航：%s', opt.url);
    await send('Page.navigate', { url: opt.url });
    let ready = false;
    for (let i = 0; i < 20; i++) {
        await sleep(1000);
        ready = await ev(`!!document.querySelector('.ProseMirror')`);
        if (ready) break;
    }
    if (!ready) throw new Error('等待编辑器 .ProseMirror 超时（页面没加载好？）');
    console.log('编辑器已就绪');
    await sleep(800);

    // --- 2. JS 聚焦编辑器并把光标放进首行（空状态物理点击易落空，已实测 focus 有效）---
    const focusOk = await ev(`(() => {
        const el = document.querySelector('.ProseMirror'); if(!el) return false;
        el.focus();
        const p = el.querySelector('p') || el;
        const range = document.createRange();
        range.selectNodeContents(p); range.collapse(true);
        const sel = document.getSelection();
        sel.removeAllRanges(); sel.addRange(range);
        return document.activeElement === el;
    })()`);
    if (!focusOk) throw new Error('编辑器聚焦失败');
    await sleep(200);
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, modifiers: 2 });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'a', code: 'KeyA', windowsVirtualKeyCode: 65, modifiers: 2 });
    await sleep(150);
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Delete', code: 'Delete', windowsVirtualKeyCode: 46 });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Delete', code: 'Delete', windowsVirtualKeyCode: 46 });
    await sleep(200);

    // --- 3. 贴稿 ---
    await send('Input.insertText', { text });
    await sleep(700);
    const fillState = await ev(`(() => {
        const ed = document.querySelector('.ProseMirror');
        return { len: ed.innerText.length, head: ed.innerText.slice(0,24), tail: ed.innerText.slice(-20) };
    })()`);
    console.log('贴稿后：len=%d head=%j tail=%j', fillState.len, fillState.head, fillState.tail);
    if (fillState.len < text.length * 0.8) throw new Error('贴稿可能不完整，停止以防出错');

    // --- 4. 记录旧 src，定位试听按钮 ---
    const prevSrc = await ev(`(() => { const a=document.querySelector('audio'); return a&&a.src?a.src:null; })()`);
    const findBtnExpr = `(() => {
        let el = document.querySelector('.try-listen');
        if (!el) {
            const cands = [...document.querySelectorAll('button,div[role=button],span')];
            el = cands.find(b => /试听/.test(b.innerText || '') && b.getBoundingClientRect().width > 0);
        }
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { x: (r.x+r.width/2)|0, y: (r.y+r.height/2)|0, txt:(el.innerText||'').trim().slice(0,10) };
    })()`;

    const getWav = () => {
        // 优先网络里新的 res.chanjing.cc wav
        const net = reqs.find(r => /res\.chanjing\.cc/.test(r.url) && /\.(wav|mp3|m4a)(\?|$)/i.test(r.url));
        return net ? net.url : null;
    };
    const createdV3 = () => reqs.some(r => /create_v3/.test(r.url) && r.method === 'POST');

    const tryListen = async n => {
        const btn = await ev(findBtnExpr);
        if (!btn) throw new Error('找不到试听按钮');
        console.log('第 %d 次点试听（按钮 %j @%d,%d）', n, btn.txt, btn.x, btn.y);
        await clickAt(btn.x, btn.y);
    };

    // --- 5. 第一次点试听 ---
    await tryListen(1);
    // 预热：若 8 秒内没发 create_v3 也没新 wav，补点第二次
    await sleep(8000);
    if (!createdV3() && !getWav()) {
        console.log('未见 create_v3（第一次仅预热），补点第二次…');
        await tryListen(2);
    }

    // --- 6. 轮询等新 wav（最多 150 秒）---
    let wav = null;
    const t0 = Date.now();
    while (Date.now() - t0 < 150000) {
        const cur = await ev(`(() => { const a=document.querySelector('audio'); return a&&a.src?a.src:null; })()`);
        if (cur && cur !== prevSrc && /res\.chanjing\.cc/.test(cur)) wav = cur;
        if (!wav) wav = getWav();
        if (wav) break;
        await sleep(1500);
    }
    if (!wav) throw new Error('超时未拿到新 wav；create_v3=%s', createdV3());
    if (wav.startsWith('//')) wav = 'https:' + wav;
    console.log('新 wav：%s', wav);

    // --- 7. 下载 ---
    const size = await new Promise((resolve, reject) => {
        const doGet = u => https.get(u, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) { res.resume(); doGet(res.headers.location); return; }
            if (res.statusCode !== 200) { reject(new Error('HTTP ' + res.statusCode)); return; }
            fs.mkdirSync(path.dirname(opt.out), { recursive: true });
            const f = fs.createWriteStream(opt.out);
            res.pipe(f); f.on('finish', () => f.close(() => resolve(fs.statSync(opt.out).size)));
        }).on('error', reject);
        doGet(wav);
    });
    console.log('\n=== 完成：%s（%d KB）===', opt.out, Math.round(size / 1024));
    ws.close();
    await sleep(200);
    process.exit(0);
}
main().catch(e => { console.error('失败：' + (e.message || e)); process.exit(1); });
