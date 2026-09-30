#!/usr/bin/env node
// mermaid-shot.js —— 用 mermaid.ink 在线渲染 mermaid 代码，直接下载高清暗色 PNG。
//
// 为什么不用本地 HTML 卡实拍：信息卡在手机端被缩到屏宽后字太小；
// mermaid.ink 渲染的图字号/图宽比大、且能用 width 参数出高分辨率，手机阅读舒服。
//
// 编码方式（与 mermaid-live-editor 一致）：
//   state = {code, mermaid:{theme,themeVariables}}
//   -> zlib.deflate(JSON) -> base64url
//   -> https://mermaid.ink/img/pako:<b64>?type=png&width=<w>&bgColor=0d1117
//
// 用法：
//   node tools/mermaid-shot.js <spec.json> <outdir>
// spec.json: [{ "name": "xxx", "code": "flowchart TD\n ...", "width": 900 }]
// 输出：<outdir>/xxx.png

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const https = require('https');

// GitHub Dark 配色；cluster* 控制 subgraph 底色（暗色）
const THEME_VARS = {
  background: '#0d1117',
  primaryColor: '#21262d',
  primaryTextColor: '#ffffff',
  primaryBorderColor: '#58a6ff',
  secondaryColor: '#30363d',
  tertiaryColor: '#161b22',
  lineColor: '#8b949e',
  textColor: '#e6edf3',
  clusterBkg: '#161b22',
  clusterBorder: '#58a6ff',
  edgeLabelBackground: '#21262d',
  fontSize: '24px',
};

function buildUrl(code, width) {
  const state = { code, mermaid: { theme: 'dark', themeVariables: THEME_VARS } };
  const b64 = zlib.deflateSync(JSON.stringify(state)).toString('base64url');
  return `https://mermaid.ink/img/pako:${b64}?type=png&width=${width}&bgColor=0d1117`;
}

function download(url, redirects) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'mermaid-shot' } }, (res) => {
      if ([301, 302, 303, 307, 308].includes(res.statusCode)) {
        if (redirects <= 0) return reject(new Error('too many redirects'));
        res.resume();
        return resolve(download(new URL(res.headers.location, url).href, redirects - 1));
      }
      if (res.statusCode !== 200) {
        let body = '';
        res.on('data', (c) => (body += c));
        res.on('end', () => reject(new Error(`HTTP ${res.statusCode}: ${body.slice(0, 200)}`)));
        return;
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', reject);
  });
}

async function main() {
  const [specPath, outdir] = process.argv.slice(2);
  if (!specPath || !outdir) {
    console.log('用法: node tools/mermaid-shot.js <spec.json> <outdir>');
    process.exit(1);
  }
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf-8'));
  fs.mkdirSync(outdir, { recursive: true });
  for (const item of spec) {
    const url = buildUrl(item.code, item.width || 900);
    const buf = await download(url, 3);
    const dest = path.join(outdir, item.name + '.png');
    fs.writeFileSync(dest, buf);
    console.log(`saved ${dest} ${buf.length} bytes`);
  }
}

main().catch((e) => {
  console.error(e.message);
  process.exit(1);
});
