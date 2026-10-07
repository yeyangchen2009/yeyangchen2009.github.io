#!/usr/bin/env node
/*
 * cj-web-tts.js —— 蝉镜「网页试听」自动化（0 蝉豆，仅出音频，不碰数字人计费）
 *
 * 两种模式：
 *   UI 模式（默认，2026-10 实测）：弹出独立 profile 直接打开「音频创作」页
 *     https://www.chanjing.cc/creation-audio?id=<audio_man>&type=custom
 *     等 TipTap(ProseMirror) 编辑器就绪 → 聚焦/Ctrl+A/Delete 清空 →
 *     Input.insertText 贴稿 → 点页面上的 .try-listen「试听」→ 轮询
 *     <audio>.src（res.chanjing.cc 的 wav）→ 立即下载。
 *   --api 模式：在页面上下文用 XHR 复刻页面自身的调用链——
 *     从 localStorage.token 取 JWT 放进 Authorization 头，先调
 *     /api/project/detect_text_duration，再调
 *     /api/workspace/audio_task/create_v3，轮询 audio_task/state 取 wav。
 *
 * 关键坑（实测）：直接在首页 fetch create_v3 会返回 code=10201「用户不存在」——
 * 页面真实请求是 axios(XHR)，除登录 cookie 外还带 Authorization 头（JWT 存
 * localStorage.token）。所以要么走 UI 点击，要么自己补上该头。
 *
 * 安全：全程不读取/打印/存储 JWT 与任何凭证；网络日志只记 URL/HTTP 状态/响应体
 * （create_v3 响应不含凭证）。绝不点「立即生成」。
 *
 * 用法:
 *   node cj-web-tts.js <tts文本.txt> <out.wav> <audio_man>
 *        [--profile <dir>] [--wait-login <秒>] [--api]
 *
 * 示例:
 *   node tools/cj-web-tts.js Temp/zhushixing-wang-tts.txt Temp/out.wav \
 *        C-df5d6f1a95904a91a8e086b6f2fd8a53 --profile Temp/cj-profile
 */
'use strict';

const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

function parseArgs(argv) {
    const [textFile, outWav, audioMan] = argv;
    if (!textFile || !outWav || !audioMan) {
        console.error('用法: node cj-web-tts.js <tts文本.txt> <out.wav> <audio_man> [--profile <dir>] [--wait-login <秒>] [--api]');
        process.exit(2);
    }
    const o = { textFile, outWav, audioMan, profile: 'Temp/cj-profile', waitLogin: 300, api: false };
    for (let i = 3; i < argv.length; i++) {
        const t = argv[i];
        if (t === '--profile') o.profile = argv[++i];
        else if (t === '--wait-login') o.waitLogin = +argv[++i];
        else if (t === '--api') o.api = true;
        else { console.error('未知选项: ' + t); process.exit(2); }
    }
    return o;
}

function resolveBrowser() {
    if (process.env.CDP_BROWSER) return process.env.CDP_BROWSER;
    const wins = [
        'C:/Program Files/Google/Chrome/Application/chrome.exe',
        'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
        'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
        'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
    ];
    return wins.find(p => { try { fs.accessSync(p); return true; } catch { return false; } }) || wins[0];
}

const sleep = ms => new Promise(r => setTimeout(r, ms));
function getJson(port, urlPath) {
    return new Promise((resolve, reject) => {
        http.get({ host: '127.0.0.1', port, path: urlPath }, res => {
            let d = ''; res.on('data', c => d += c);
            res.on('end', () => { try { resolve(JSON.parse(d)); } catch (e) { reject(e); } });
        }).on('error', reject);
    });
}

async function launch(browser, profileDir, audioMan) {
    fs.mkdirSync(profileDir, { recursive: true });
    const startUrl = 'https://www.chanjing.cc/creation-audio?id=' + encodeURIComponent(audioMan) + '&type=custom';
    const args = [
        '--no-first-run', '--ignore-certificate-errors',
        '--remote-debugging-port=0', '--remote-allow-origins=*',
        '--user-data-dir=' + path.resolve(profileDir),
        startUrl,
    ];
    const child = spawn(browser, args, { stdio: ['ignore', 'ignore', 'pipe'] });
    const port = await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('等待 DevTools 端口超时（若刚关过同 profile 的浏览器，可能有残留进程，结束后重试）')), 20000);
        child.stderr.on('data', d => {
            const m = String(d).match(/DevTools listening on ws:\/\/[^\s:]+:(\d+)\//);
            if (m) { clearTimeout(timer); resolve(+m[1]); }
        });
        child.on('exit', c => { clearTimeout(timer); reject(new Error('浏览器提前退出 code=' + c + '（多为同 profile 已有 Edge/Chrome 实例占用，请先结束其进程）')); });
    });
    return { child, port };
}

function kill(child) {
    try { child.kill(); } catch { /* */ }
    try { spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore' }); } catch { /* */ }
}

// 在对象里递归找第一个形如 http(s)://res.chanjing.cc/...wav 的字符串
function findWav(x, seen) {
    seen = seen || new Set();
    if (x == null || typeof x === 'object') {
        if (!x || seen.has(x)) return null;
        seen.add(x);
        for (const k of Object.keys(x)) {
            const r = findWav(x[k], seen);
            if (r) return r;
        }
        return null;
    }
    if (typeof x === 'string' && /res\.chanjing\.cc/.test(x) && /\.wav(\?|$)/.test(x)) return x;
    return null;
}
function findTaskId(x, seen) {
    seen = seen || new Set();
    if (x && typeof x === 'object') {
        if (seen.has(x)) return null;
        seen.add(x);
        for (const k of ['task_id', 'taskId', 'id']) {
            if (typeof x[k] === 'string' && /^[0-9a-f]{16,}$/.test(x[k])) return x[k];
        }
        for (const k of Object.keys(x)) {
            const r = findTaskId(x[k], seen);
            if (r) return r;
        }
    }
    return null;
}

function download(url, dest) {
    return new Promise((resolve, reject) => {
        const mod = url.startsWith('https') ? https : http;
        const doGet = u => mod.get(u, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                res.resume(); doGet(res.headers.location); return;
            }
            if (res.statusCode !== 200) { reject(new Error('下载 HTTP ' + res.statusCode)); return; }
            const f = fs.createWriteStream(dest);
            res.pipe(f);
            f.on('finish', () => f.close(() => resolve(fs.statSync(dest).size)));
        }).on('error', reject);
        doGet(url);
    });
}

async function main() {
    const opt = parseArgs(process.argv.slice(2));
    const text = fs.readFileSync(opt.textFile, 'utf8').trim();
    console.log('文本字数：' + text.length + '　模式：' + (opt.api ? 'API（XHR+JWT）' : 'UI（点击试听）'));
    const browser = resolveBrowser();
    console.log('浏览器：' + browser);
    const { child, port } = await launch(browser, opt.profile, opt.audioMan);

    let ws;
    try {
        await sleep(4000);
        const list = await getJson(port, '/json/list');
        const page = list.find(t => t.type === 'page');
        if (!page) throw new Error('找不到 page 目标');
        ws = new WebSocket(page.webSocketDebuggerUrl);
        await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });

        let mid = 0;
        const pend = new Map();
        ws.addEventListener('message', e => {
            const m = JSON.parse(e.data);
            if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
        });
        const send = (method, params = {}) => new Promise((resolve, reject) => {
            const id = ++mid;
            pend.set(id, msg => msg.error ? reject(new Error(method + ': ' + JSON.stringify(msg.error))) : resolve(msg.result));
            ws.send(JSON.stringify({ id, method, params }));
        });
        await send('Runtime.enable');
        await send('Page.enable');
        const evalJs = async expr => {
            const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
            if (r.exceptionDetails) throw new Error('JS: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text));
            return r.result.value;
        };
        const key = (type, keyName, code, mods) => send('Input.dispatchKeyEvent', Object.assign({
            type, key: keyName, code, windowsVirtualKeyCode: code === 'Delete' ? 46 : Buffer.from(keyName)[0] || 0,
        }, mods || {}));

        // 轻量网络日志：只记 URL/状态/响应前缀，不记请求头（避免 JWT 落盘）
        await evalJs(`(()=>{
          if(window.__cjlog)return;
          window.__cjlog=[];
          const of=window.fetch;
          window.fetch=function(input,init){
            const rec={kind:'fetch',url:typeof input==='string'?input:(input&&input.url),method:(init&&init.method)||'GET'};
            window.__cjlog.push(rec);
            return of.apply(this,arguments).then(async r=>{try{rec.status=r.status;rec.resp=(await r.clone().text()).slice(0,500);}catch(e){}return r;});
          };
          const oo=XMLHttpRequest.prototype.open, os=XMLHttpRequest.prototype.send;
          XMLHttpRequest.prototype.open=function(m,u){this.__u=u;this.__m=m;return oo.apply(this,arguments);};
          XMLHttpRequest.prototype.send=function(b){
            const rec={kind:'xhr',url:this.__u,method:this.__m};
            window.__cjlog.push(rec);
            this.addEventListener('loadend',()=>{try{rec.status=this.status;rec.resp=String(this.responseText).slice(0,500);}catch(e){}});
            return os.apply(this,arguments);
          };
        })()`);

        // --- 等待登录：localStorage.token 存在 且 创作页元素可见 ---
        console.log('\n>>> 如未登录，请在弹出的窗口里登录蝉镜（最多等 ' + opt.waitLogin + ' 秒）…');
        const readyExpr = `!!localStorage.token && !!document.querySelector('.try-listen')`;
        const t0 = Date.now();
        while (!(await evalJs(readyExpr).catch(() => false))) {
            if (Date.now() - t0 > opt.waitLogin * 1000) {
                console.log('\n等待登录超时。'); process.exitCode = 1; return;
            }
            process.stdout.write('.');
            await sleep(3000);
        }
        console.log('\n登录态就绪。');

        let wav = null;

        if (opt.api) {
            // ===== API 模式：XHR 复刻 detect_text_duration → create_v3 → 轮询 state =====
            const callApi = async (api, body) => evalJs(`(async()=>{
                const tok=localStorage.token;            // 只在页面运行时使用，不取出打印
                const r=await new Promise((resolve,reject)=>{
                  const x=new XMLHttpRequest();
                  x.open('POST',${JSON.stringify(api)});
                  x.setRequestHeader('Content-Type','application/json');
                  x.setRequestHeader('Authorization',tok);
                  x.onload=()=>resolve({http:x.status,body:x.responseText});
                  x.onerror=()=>reject(new Error('XHR error'));
                  x.send(${JSON.stringify(JSON.stringify(body))});
                });
                let j=null;try{j=JSON.parse(r.body);}catch(e){}
                return {http:r.http,json:j};
              })()`);

            console.log('detect_text_duration …');
            const det = await callApi('/api/project/detect_text_duration', { text });
            if (det.json && det.json.code === 0) {
                console.log('  预计时长 ' + det.json.data.duration + ' 秒，' + det.json.data.count + ' 字');
            }

            const createBody = {
                audio_man: opt.audioMan,
                speed: 1, pitch: 1,
                model: 'volcano_mega',
                rhythm_preset_id: 0,
                slice: [{ plain_text: text }],
            };
            const cr = await callApi('/api/workspace/audio_task/create_v3', createBody);
            const taskId = cr.json ? findTaskId(cr.json) : null;
            const code = cr.json ? cr.json.code : undefined;
            if (code !== 0 || !taskId) {
                console.log('create_v3 失败，停止以防重复提交：code=' + code + ' body=' + JSON.stringify(cr.json).slice(0, 300));
                process.exitCode = 1; return;
            }
            console.log('create_v3 已提交（不重复提交），task 已受理。');

            for (let i = 0; i < 60; i++) {
                await sleep(3000);
                const st = await callApi('/api/workspace/audio_task/state', { task_id: taskId });
                wav = st.json ? findWav(st.json) : null;
                if (i % 4 === 0) console.log('轮询 state #' + i + (wav ? ' 已得wav' : ''));
                if (wav) break;
            }
        } else {
            // ===== UI 模式：填稿 → 点 .try-listen → 抓 audio.src =====
            console.log('填稿 …');
            await evalJs(`document.querySelector('.ProseMirror').focus()`);
            await sleep(200);
            await key('keyDown', 'a', 'KeyA', { modifiers: 2 });
            await key('keyUp', 'a', 'KeyA', { modifiers: 2 });
            await key('keyDown', 'Delete', 'Delete');
            await key('keyUp', 'Delete', 'Delete');
            await sleep(200);
            await send('Input.insertText', { text });
            await sleep(600);
            const filled = await evalJs(`document.querySelector('.ProseMirror').innerText`);
            console.log('  编辑器内字数 ' + filled.length + '，含外船=' + filled.includes('外船'));

            console.log('点击「试听」（绝不点立即生成）…');
            await evalJs(`document.querySelector('.try-listen').click()`);
            // 若 8 秒内未出现 create_v3 请求（个别版本首次点击只预热），再点一次
            await sleep(8000);
            const submitted = await evalJs(`(window.__cjlog||[]).some(r=>/create_v3/.test(r.url||''))`);
            if (!submitted) {
                console.log('首次点击仅预热，再点一次 …');
                await evalJs(`document.querySelector('.try-listen').click()`);
            }
            // 业务非0错误（非鉴权）：停下不重复提交
            const bad = await evalJs(`(window.__cjlog||[]).map(r=>r.resp).find(t=>t&&/"code":(?!0\\b)\\d+/.test(t)&&!/10201/.test(t))`);
            if (bad) { console.log('试听接口返回错误，停止：' + bad.slice(0, 300)); process.exitCode = 1; return; }

            for (let i = 0; i < 80; i++) {
                await sleep(3000);
                wav = await evalJs(`(()=>{
                  const s=document.querySelector('audio').src;
                  return /res\\.chanjing\\.cc/.test(s)&&/\\.wav(\\?|$)/.test(s)?s:null;
                })()`);
                if (i % 4 === 0) console.log('等待 audio.src #' + i + (wav ? ' 已得wav' : ''));
                if (wav) break;
            }
        }

        if (!wav) {
            console.log('未拿到 wav。');
            process.exitCode = 1; return;
        }
        if (wav.startsWith('//')) wav = 'https:' + wav;
        const size = await download(wav, opt.outWav);
        console.log('\n=== 完成：' + opt.outWav + '（' + Math.round(size / 1024) + ' KB）===');
    } finally {
        if (ws) { try { ws.close(); } catch { /* */ } }
        await sleep(500);
        kill(child);
        process.exit(process.exitCode || 0);
    }
}
main().catch(e => { console.error(e.message || e); process.exit(1); });
