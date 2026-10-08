#!/usr/bin/env node
/*
 * screen-rec.js —— 零依赖屏幕录制器（FFmpeg gdigrab，Node >= 18）
 * 与 cdp-shot.js 配套：cdp-shot 录浏览器/HyperFrames 动画（确定性逐帧），
 * screen-rec 录真人操作演示（终端 / 编辑器 / 浏览器点击，实时抓屏）。
 *
 * 用法:
 *   node screen-rec.js <out.mp4> [选项]
 *
 * 选项:
 *   --width <px> --height <px>  只录指定区域（两者须同时给；默认整屏）
 *   --x <px> --y <px>           区域左上角偏移（默认 0,0；需配合 --width/--height）
 *   --fps <n>                   帧率（默认 30）
 *   --duration <秒> / -t <秒>   录制时长；不给则录到按 Ctrl+C（优雅收尾）
 *   --audio <设备名>            同时用 dshow 录制麦克风（设备名用 --list-audio 查）
 *   --no-mouse                  不显示鼠标光标（默认显示）
 *   --preset <p>                x264 preset（默认 veryfast）
 *   --crf <n>                   x264 crf（默认 20）
 *   --list-audio                列出本机 dshow 音视频输入设备后退出
 *   -h, --help                  显示帮助
 *
 * 示例:
 *   node screen-rec.js demo.mp4 --duration 10
 *   node screen-rec.js demo.mp4 --width 1280 --height 720 --x 100 --y 80 -t 20
 *   node screen-rec.js demo.mp4 --audio "麦克风 (Realtek Audio)" --duration 30
 *
 * 说明: gdigrab 走 GDI 抓屏，录终端/编辑器/浏览器/普通桌面毫无问题；
 * 对硬件加速或独占全屏内容（部分游戏、DRM 视频）可能抓到黑屏。
 */
'use strict';

const { spawn } = require('child_process');
const fs = require('fs');

const REC_USAGE = `screen-rec.js —— 零依赖屏幕录制器（FFmpeg gdigrab）

用法:
  node screen-rec.js <out.mp4> [选项]

常用选项:
  --duration <秒> / -t <秒>   录制时长；不给则录到按 Ctrl+C
  --width <px> --height <px>  只录指定区域（默认整屏）
  --x <px> --y <px>           区域左上角偏移（默认 0,0）
  --fps <n>                   帧率（默认 30）
  --audio <设备名>            同时录麦克风（设备名用 --list-audio 查）
  --no-mouse                  不显示鼠标光标（默认显示）
  --preset <p>                x264 preset（默认 veryfast）
  --crf <n>                   x264 crf（默认 20）
  --list-audio                列出 dshow 音视频输入设备后退出
  -h, --help                  显示本帮助

示例:
  node screen-rec.js demo.mp4 --duration 10
  node screen-rec.js demo.mp4 --width 1280 --height 720 -t 20
  node screen-rec.js demo.mp4 --audio "麦克风 (Realtek Audio)" -t 30`;

function parseArgs(argv) {
    if (argv.some(a => a === '-h' || a === '--help')) {
        console.log(REC_USAGE);
        process.exit(0);
    }
    const withValue = new Set(['width', 'height', 'x', 'y', 'fps',
        'duration', 'audio', 'preset', 'crf']);
    const o = {
        out: '', fps: 30, duration: 0, width: 0, height: 0,
        x: 0, y: 0, audio: '', preset: 'veryfast', crf: 20,
        mouse: true, listAudio: false,
    };
    const positionals = [];
    for (let i = 0; i < argv.length; i++) {
        const tok = argv[i];
        if (tok === '-t') {
            if (argv[i + 1] === undefined) {
                console.error('-t 需要一个值');
                process.exit(2);
            }
            o.duration = argv[++i];
            continue;
        }
        if (tok.startsWith('--')) {
            const key = tok.slice(2);
            if (withValue.has(key)) {
                if (argv[i + 1] === undefined) {
                    console.error('选项 ' + tok + ' 需要一个值');
                    process.exit(2);
                }
                o[key] = argv[++i];
            } else if (key === 'no-mouse') {
                o.mouse = false;
            } else if (key === 'list-audio') {
                o.listAudio = true;
            } else {
                console.error('未知选项: --' + key);
                process.exit(2);
            }
        } else {
            positionals.push(tok);
        }
    }
    o.out = positionals[0];
    o.fps = +o.fps;
    o.duration = +o.duration;
    o.width = +o.width;
    o.height = +o.height;
    o.x = +o.x;
    o.y = +o.y;
    o.crf = +o.crf;
    return o;
}

// ffmpeg 把 dshow 设备清单输出到 stderr，解析出 [video]/[audio] 设备名。
function listDshowDevices() {
    return new Promise((resolve, reject) => {
        const proc = spawn('ffmpeg',
            ['-hide_banner', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']);
        let err = '';
        proc.stderr.on('data', d => { err += String(d); });
        proc.on('error', reject);
        proc.on('exit', () => {
            const rows = [];
            for (const ln of err.split(/\r?\n/)) {
                // 形如: [dshow @ ...] "麦克风阵列 (...)" (audio)
                const m = ln.match(/\]\s+"([^"]+)"\s*\((video|audio)\)/);
                if (m) rows.push('[' + m[2] + '] ' + m[1]);
            }
            resolve(rows);
        });
    });
}

function buildArgs(o) {
    const args = ['-y', '-hide_banner',
        '-f', 'gdigrab', '-framerate', String(o.fps),
        '-draw_mouse', o.mouse ? '1' : '0'];
    if (o.width && o.height) {
        args.push('-video_size', o.width + 'x' + o.height,
            '-offset_x', String(o.x), '-offset_y', String(o.y));
    }
    args.push('-i', 'desktop');
    if (o.audio) args.push('-f', 'dshow', '-i', 'audio=' + o.audio);
    if (o.duration) args.push('-t', String(o.duration));
    args.push('-c:v', 'libx264', '-preset', o.preset,
        '-crf', String(o.crf), '-pix_fmt', 'yuv420p');
    if (o.audio) args.push('-c:a', 'aac', '-b:a', '192k');
    args.push('-movflags', '+faststart', o.out);
    return args;
}

async function main() {
    const o = parseArgs(process.argv.slice(2));

    if (o.listAudio) {
        const rows = await listDshowDevices();
        if (!rows.length) console.log('未发现 dshow 输入设备（或 ffmpeg 不可用）。');
        else console.log(rows.join('\n'));
        return;
    }
    if (!o.out) {
        console.error('用法: node screen-rec.js <out.mp4> [选项]');
        process.exit(2);
    }
    if ((o.width && !o.height) || (!o.width && o.height)) {
        console.error('--width 与 --height 必须同时提供。');
        process.exit(2);
    }
    if ((o.x || o.y) && !(o.width && o.height)) {
        console.error('--x/--y 偏移需配合 --width/--height 指定区域。');
        process.exit(2);
    }

    const proc = spawn('ffmpeg', buildArgs(o),
        { stdio: ['pipe', 'pipe', 'pipe'] });
    let tail = '';
    proc.stderr.on('data', d => { tail = (tail + String(d)).slice(-4000); });
    proc.stdin.on('error', () => { /* 结束时的 EPIPE，按退出码处理 */ });
    proc.on('error', e => {
        console.error('无法启动 ffmpeg（是否已安装并在 PATH？）：' + e.message);
        process.exit(1);
    });

    const t0 = Date.now();
    let stopping = false;
    const stop = () => {
        if (stopping) return;
        stopping = true;
        console.log('\n正在结束录制、写入文件…');
        try { proc.stdin.write('q'); } catch { /* 已关闭 */ }
    };
    // 不定时长：按 Ctrl+C 时给 ffmpeg 发 'q'，让它干净收尾（写好 moov）。
    if (!o.duration) process.on('SIGINT', stop);

    proc.on('exit', code => {
        if (code === 0) {
            const size = fs.existsSync(o.out) ? fs.statSync(o.out).size : 0;
            console.log(`已录制 ${o.out}  ${size} bytes  耗时 ${((Date.now() - t0) / 1000).toFixed(1)}s`);
        } else {
            console.error('ffmpeg 退出码 ' + code + '\n' + tail.slice(-1500));
            process.exitCode = 1;
        }
    });
}

main();
