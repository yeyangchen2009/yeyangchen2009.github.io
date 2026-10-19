# probe-seeds 复现说明

hf-07 录屏布景的三个工程种子（背景与翻转史见 ../PROBE-NOTES.md 文首勘误；
正式布景由 ../setup_scenes.py init 复制到沙盒 `F:\_hftest\hf07-frames\proj`
并冻结 backup/，不要手工往沙盒里拷）：

- `01-css-vs-gsap.html`（文件名沿用，内容已换主角）：主工程 v1。
  - 蓝块 `#good`：GSAP fromTo x:0→800/8s，注册 `__timelines`，seekable 正解；
  - 绿点 `#legal`：纯 CSS `@keyframes legalPulse` 2s alternate——合法居民，
    snapshot 经 WAAPI 把它虚拟化到时间轴（同 at 四连帧同位），体检
    `cssKeyframes` 在册；
  - 红块 `#bad`：★自掐表黑户，`setInterval` 里累加闭包自有计数器（4s 周期，
    不碰 Date.now/rAF、不注册时间轴）——check 0 error，同 at 四连帧四位置，
    keyframes 报告隐身、`--shot #bad` 硬 error；
  - 右上 `#clock`：dummy tween 写 `t=<tl.time()>`，证明截图瞬间确有 seek。
- `02-variant-x500.html`：compare 变体 B（蓝块换绿 #238636、距离缩到 500），
  其余与 v1 同构（含 #legal 与自掐表红块）。
- `03-wallclock-slow.html`：边界实验 v3。自掐表换成 **60s 一圈慢表**
  （红块字「慢表」）：截图墙钟 8–15s ⇒ translateX≤200px，`snapshot --at 10`
  真机三跑 red≈0.146 稳定贴左、blue=0.5516 在终点。旧 03-css-forwards.html
  （CSS forwards 版）已随 2026-10-19 勘误删除。

复现（仓库外沙盒；正式录屏走 setup_scenes.py，勿手动）：建 `v1/index.html`
（复制任一种子）＋同级放 `videos/projects/hf-07/gsap.min.js`（种子页引相对
路径 `gsap.min.js`，勿用 CDN——jsdelivr 在无头环境 ERR_CONNECTION_RESET，
见 PROBE-NOTES E1），然后：

```
npx hyperframes@0.8.107 check v1
npx hyperframes@0.8.107 snapshot v1 --at 2,2,2,2 --no-end --no-browser-gpu
npx hyperframes@0.8.107 keyframes v1
npx hyperframes@0.8.107 keyframes v1/index.html --shot build/onion-bad.png --selector #bad
```

预期：check pass；接触表四格蓝/绿同位、红块四格四位置；报告 3 items
（#good/#clock/legalPulse #legal）无 #bad；末条 exit 1「nothing animates
under '#bad'」。
