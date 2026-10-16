# hf-05《check 门控》正音表（TTS 借音依据）

> 配套稿件：`hf-05-src.txt`（口播定稿 v1，2026-10-16 用户过审）。
> 体例沿 hf-03/hf-04：借音稿 `hf-05-tts.txt` 由 `oneoffs/make_tts.py` 从正字稿
> 机械派生（预期次数闸＋逆变换逐字相等闸＋残留扫描闸）；正字稿给字幕，借音稿给
> 蝉镜试听 TTS（0 蝉豆，绝不点「立即生成」）。英文标识符原样保留英文读音。
> 蝉镜合成后逐句试听核，F2 阶段成片全量复查。2026-10-16 初扫。

## 一、高危多音字

| 字 | 音 | 位置与处理 |
|---|---|---|
| 行 | háng | 全篇 9 处行列义：①「几百行 HTML」**借「航」**（hf-03/04 已验证）；其余 8 处一律改写避音——「一行黄字」→一条黄字；「就这一行」→就这一处；「三行警告」→三条警告；「一行点了名」→头一条点了名；「还有两行」→还有两条；「一行红字」→蹦出红字；「这行红」→这句红；「另起一行」→另敲一句 |
| 行 | xíng | 运行时（seg A 1 处）、放行（2 处）、行动件（1 处），本音保留 |
| 量 | liáng | 3 处测量义 TTS 易读 liàng，全改写：量布局→**测**布局；量文字和底色的对比度→**测**……；量得出→**测**得出 |
| 数 | shǔ | 「数拍子」1 处，改写「算节拍」；其余 shù：计数器、不同的数、凑数、元数据、函数、参数 |
| 待 | dāi | 「待五秒」停留口语音，改写「停五秒」（dài/等待义不混） |
| 得 | děi | 3 处需要/必须义：「它**得**到第十三秒才走」「都**得** Chrome 真把像素画出来」「黄字**得**逐条读完」。借本字（hf-04 经验 TTS 常读对），试听若读 de 再改写「要/必须」 |
| 得 | de | 没觉**得**、照它递**的**修法，轻声 |
| 重 | chóng | 「时间还重叠」1 处；常用词 TTS 一般读对，试听核（本集无 zhòng） |
| 长 | cháng | 总长、时长（多处）；本集**无 zhǎng**，不用借字 |
| 还 | hái | 还有/还是/还成立/还真去……全篇仅此音，无 huán |
| 处 | chù | 同一处拼错（名词）；本集无 chǔ |
| 间 | jiān | 时间轴、瞬间、中间态，全 jiān |
| 着 | zhe | 盯着、叠着、躺着，全轻声 |
| 地 | de | 静悄悄地没了，结构助词 |
| 藏 | cáng | 文字藏在不透明元素底下 |
| 挑 | tiāo | 挑了个深蓝灰（阴平） |

## 二、易错单音字

| 字 | 音 | 位置 |
|---|---|---|
| 帧 | zhēn | 帧帧可复现、海报帧、末帧、首帧尾帧（高频） |
| 暂 | zàn | 暂停的时间轴 |
| 碍 | ài | 无障碍标准 WCAG |
| 糊弄 | hù nong | 别以为它好糊弄 |
| 洋葱 | yáng cōng | 洋葱皮图 |
| 束 | shù | 在第十秒前结束 |
| 悄悄 | qiāo qiāo | 静悄悄地 |
| 连坐 | lián zuò | 后面的关卡连坐 |

## 三、英文与符号念法

- 代码/命令标识符原样念英文：`check`、`npx`（逐字母 n-p-x）、`hyperframes`、`Lint`、`Runtime`、`Layout`、`Motion`、`Contrast`、`Snapshots`、`Chrome`、`CI`、`cmd`、`echo`、`repeat`、`disabled`、`passed`、`failed`、`GSAP target not found`、`page error`、`keyframes`、`inspect`、`beats`、`visual`、`fromTo`、`percent`、`audio`、`id`。
- `@0.8.107`：借音稿写 `at 0.8.107`；版本数字保留半角（hf-02 已验证蝉镜念「零点八点一零七」）。
- 连字符属性改空格：`data duration`、`data track index`、`track index`、`data timeline role`。
- 点号：`index 点 html`。
- 蛇形规则名下划线改空格，按英文单词念：
  - `timeline_element_missing_timing` → timeline element missing timing
  - `clip_ends_past_root_duration` → clip ends past root duration
  - `text_occluded` → text occluded
  - `page_error` → page error
- 井号选择器稿中已写汉字「井号」：井号 sub／井号 sut／井号 title。
- 色值 `#1a1f26` 借音稿逐字符：井号一 a 一 f 二六（字母听蝉镜念字母名，试听核；别扭再借音）。
- `rgb(93,97,102)` 去括号：r g b 九三，九七，一零二。
- `--shot`：横杠横杠 shot。
- `%ERRORLEVEL%` 稿中已写「百分号 ERRORLEVEL 百分号」，借音稿 ERRORLEVEL 拆 `error level` 防逐字母。
- `0%/100%` 稿中已写「零 percent／一百 percent」。
- WCAG 逐字母；bgm／soundtrack／music 英文词。
- 数字口语稿已写中文：一点一四比一、三比一、四点五、零点五六秒、九点四四秒、一点六六七秒、十分之十。

## 四、合成后试听＋F2 复查清单

- 3 处 děi vs 2 处 de；9 处 háng 改写/借「航」后听感是否自然（生硬再调整句改写）。
- 重叠 chóng；挑 tiāo；待→停、量→测、数→算三处改写与字幕 src 的对齐缺口（align 拼音/单字 gap 可吞）。
- 三组蛇形规则名是否按英文词念而不是逐字母；色值 1a1f26 与 rgb 三个数。
- n p x／at／横杠横杠 shot／error level 四类首次出现的符号念法。
- 帧 zhēn、暂 zàn、碍 ài。
