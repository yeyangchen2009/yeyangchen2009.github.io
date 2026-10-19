# probe-seeds 复现说明

hf-07 前制探针的三个事故页种子（详见 ../PROBE-NOTES.md）：

- `01-css-vs-gsap.html`：GSAP 蓝块 vs CSS animation 红块（infinite），E1–E3、E5–E8 用；
- `02-variant-x500.html`：compare 变体 B（x500 绿块），E6 用；
- `03-css-forwards.html`：CSS 动画改 8s forwards，E4 边界实验用。

复现：在仓库外沙盒建 `v1/index.html`（复制任一种子）＋同级放
`videos/projects/hf-07/gsap.min.js`（种子页引相对路径 `gsap.min.js`，
勿用 CDN——jsdelivr 在无头环境 ERR_CONNECTION_RESET，见 PROBE-NOTES E1），
然后 `npx hyperframes@0.8.107 snapshot v1 --at 2,2,2,2 --no-end -o build/p3`。
