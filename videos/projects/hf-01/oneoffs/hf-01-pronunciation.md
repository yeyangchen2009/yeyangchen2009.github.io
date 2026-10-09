# hf-01 发音 / 借音记录

技术教程第一集，英文术语密集。先用蝉镜试听（0 豆）合成一句测试稿，再以
faster-whisper 反转录验证克隆音色「叶扬」(`C-df5d6f1a95904a91a8e086b6f2fd8a53`)
的英文发音，确认可辨后才合成整篇。

## 结论：英文术语直接保留，不做中文谐音

反转录能逐音节还原，说明克隆音色按正确英文发音念出（带中式口音，但程序员人设下真实可接受）：

| 术语 | whisper 还原 | 处理 |
|------|-------------|------|
| HyperFrames | Hy-per-Fr-ames | 保留 |
| HTML | H-T-ML（逐字母） | 保留 |
| Node | N-ode | 保留 |
| FFmpeg | FF-M-PE-G | 保留 |
| Chrome | Chr-ome | 保留 |
| MP4 | MP-4 | 保留 |
| agent | A-gent | 保留 |

Remotion / React / whisper / docker / lint / init / preview / check / render / help
同样保留英文；合成后整篇反转录核对，若个别词念崩再在 tts 稿针对性替换（src 不动）。

## tts 稿相对 src 的两处中文避音

1. 「你**给**它一个网页，它**还**给你一个 MP4」
   →「你给它一个网页，**拿到的**是一个 MP4」——避「还」hái/huán 歧义。
2. 「你**得**按 React 那套来」
   →「你**要**按 React 那套来」——避「得」děi/de。

其余中文实词在技术语境下读音无歧义（渲染 xuàn、帧 zhēn、撒手 sā、压根 yà、复现…），
未做替换。
