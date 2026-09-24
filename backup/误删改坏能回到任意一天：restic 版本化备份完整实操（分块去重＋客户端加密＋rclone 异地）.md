上一篇用 rclone，解决的是「把数据多搬一份到别处」。但有一种倒霉，rclone 救不了。

文件没丢，是被自己改坏了，或者误删了——而同步恰好发生在改坏之后。`copy` 忠实，`sync` 更忠实，连坏的带删的一起给你镜像过去。等发现不对，哪一份副本里都没有上周那个能用的版本了。

这时候缺的不是「副本」，是「历史版本」。该换一个思路的工具上场了：restic。

## 一、先说 restic 是什么

restic 是一个用 Go 写的备份程序，单个可执行文件，当前版本 0.19.1，`winget install restic.restic` 就能装。它干的事可以概括成三句：

- **每次备份生成一个快照（snapshot）**，历史版本全部留着，想回到哪天就回到哪天；
- **内容分块去重**，同一个块不管在多少个版本里出现，仓库里只存一次；
- **客户端加密**，仓库整个是密文，存到哪儿都不怕被人看。

跟 rclone 的分工一句话说清：**rclone 管「搬到哪」，restic 管「备份的版本和完整性」。** 这俩还能合体——后面专门讲。

## 二、仓库里到底有什么：四个名词

要看懂后面的输出，先认识四个词：仓库、快照、块、包。

- **repository（仓库）**：备份的目的地，可以是本地文件夹，也可以是对象存储、rclone 远端。
- **snapshot（快照）**：一次备份的时间点，记下当时的目录树。
- **blob（块）**：仓库里最小的数据单元，分两种——data blob 装文件内容，tree blob 装目录结构。
- **pack（包）**：blob 攒起来打成一个带加密的文件，存在磁盘上。

这套结构对程序员来说有个现成的类比：**Git**。Git 也是内容寻址——文件内容算个哈希当指纹存成 object，commit 指向 tree、tree 指向 blob。restic 几乎一一对应：snapshot 约等于 commit，tree blob 约等于 tree object，data blob 约等于 blob，pack 约等于 packfile。白话版：数据不是按「文件名＋路径」存的，是按「内容指纹」存的，内容一样，就是同一个块。

所以仓库的物理目录长这样：`data/` 下面是 00 到 ff 共 256 个哈希桶，桶里是 pack 文件；另外四个目录各司其职——`snapshots/` 存快照、`index/` 存索引、`keys/` 存密钥、`locks/` 存锁。`init` 之后整个仓库只有 50K，配置文件里写明仓库版本号 version 2 和一个分块多项式 `chunker_polynomial`——这两个东西后面都会讲到。

## 三、第一次备份

初始化和备份各一条命令，`-r` 指定仓库路径，`--tag` 给快照贴个标签：

```bash
restic init -r repo
restic backup -r repo data --tag demo
```

第一次备份的输出，逐行都值得看：

```text
no parent snapshot found, will read all files
Files:           5 new,     0 changed,     0 unmodified
Added to the repository: 5.292 MiB (5.290 MiB stored)
snapshot ee6ed6fd saved
```

仓库密码通过环境变量 `RESTIC_PASSWORD` 给，写脚本时也可以用 `--password-file` 指定一个文件，免得密码出现在命令行历史里。第一次没有「父快照」做参照，restic 老老实实把所有文件读了一遍，5 个文件全是新的，存进去 5.292 MiB。注意括号里的 5.290 MiB stored——压缩后实际写入比逻辑值还略少一点，省的主要是元数据；那 5MB 随机文件本身压不动。

![restic init 与三次备份的增量输出](/screenshots/restic-backup.png)

## 四、去重：四份数据，为什么只占一份多一点

光看一次备份不稀奇，连着备四次才看得出这套设计的厉害。叶扬拿同一个目录做了四轮：

**第二轮，一个字没改，又备一次。** restic 自动找到上一个快照当 parent，逐个文件比对，结果是「5 unmodified，Added 0 B」——快照照样存了，但没往仓库里加一个字节。

**第三轮，改 1 个小文件、新增 1 个文件。** 输出「1 new, 1 changed，Added 5.095 KiB」，只存变化的那点东西。

**第四轮最能说明问题：只改了一个 5MB 大文件中间的 1KB。** 如果按传统「整文件增量」备份，这一下至少得再存一个 5MB；restic 的输出是「Added 760.498 KiB」——只有受影响的那部分块重新存了，文件的其余大块原样复用。

把四个快照列出来，再用 stats 算总账：

```text
ID        Time                 Tags   Size
ee6ed6fd  2026-09-24 15:14:55  demo   5.286 MiB
293aaf58  2026-09-24 15:14:57  demo   5.286 MiB
241c539e  2026-09-24 15:14:58  demo   5.286 MiB
245a9769  2026-09-24 15:15:03  demo   5.286 MiB

Stats in restore-size mode:
     Total File Count:  34
           Total Size:  21.145 MiB
```

逻辑上，四个快照展开是 21.145 MiB、34 个文件；物理仓库呢？**5.4M。**

![4 个快照展开 21MiB，物理仓库只占 5.4M](/screenshots/restic-dedup.png)

这中间的魔法就是前面配置文件里那个分块多项式，学名 **CDC（Content-Defined Chunking，内容定义分块）**。restic 不按固定长度切文件，而是拿一个滚动哈希窗口在字节流上滑，哈希满足某个条件的地方才下刀切块。于是文件中间插入或修改一点内容，只有附近一两个块的边界会变，前后的块指纹纹丝不动，直接复用。这个思路跟 rsync 传增量、跟编译器「只重编译改动过的 .c 文件」是一个道理——把昂贵操作限制在真正变化的那一小块。

## 五、恢复：备份唯一的验收标准，是真的能恢复

备份圈有句不好笑的实话：没做过恢复演练的备份，等于没有备份。restic 给了几种取数据的姿势。

整份还原，用 restore，`--target` 指定落地目录：

```bash
restic restore 241c539e -r repo --target restored/v3
# Summary: Restored 9 files/dirs (5.286 MiB) in 0:00
```

只想捞一个文件，不必整份恢复，dump 直接吐到标准输出，可以重定向存档：

```bash
restic dump 241c539e data/docs/todo.txt -r repo
```

这里有个 **Windows 专属的坑**：路径不能加前导斜杠。写成 `/data/docs/todo.txt`，restic 会把它当成 Windows 盘符路径，报 `path "\D:" not found`。去掉前导斜杠写 `data/docs/todo.txt`，或者写成 `//data/docs/todo.txt`，才正常。配合 `find`（全仓库搜文件在哪些快照里）和 `ls`（列出某个快照的目录树），定位东西很方便。

![restore、dump、forget、prune 全流程实拍](/screenshots/restic-restore.png)

叶扬的习惯是每开一个新仓库，第一次备份完立刻 restore 到临时目录，跟源文件比对一遍。这一步花两分钟，省的是灾难来临时才发现「备份是坏的」那种绝望。

## 六、密码、密钥和锁

安全相关的几件事，一次说清。

**一把仓库可以挂多个密码。** `restic key list` 看现有密钥，`restic key add` 加一把新的。这在轮换密码、或者多人共用仓库时有用——新密码告知相关方、旧密码随后移除，中间不会断档。实测用新密码能正常打开仓库，输错密码则干脆利落地回一句 `wrong password or no key found`，没有任何可钻的空子。

密钥派生用的是 scrypt，参数写在每个 key 文件里：N=32768、r=8、p=1，专门用来把「人脑记得住的密码」慢哈希成加密密钥，扛得住暴力穷举；数据本身用 AES-256 加密、Poly1305 做完整性认证。老规矩必须再说一遍：**密码丢了没有后门，仓库里的数据永久不可恢复。**

**仓库是靠锁协作的。** 备份、清理这类写操作会在 `locks/` 里加锁，防止两个进程同时把仓库改坏。如果进程被强杀、留下没清掉的 stale lock，后续操作会报错，`restic unlock` 清掉即可。

另外提一个退出码：备份时有些文件读不到（Windows 上最常见，比如正被别的程序打开的文件），restic 不会装作成功，它会记下无法读取的文件，快照照样存，但**退出码是 3**。写自动化脚本时别只判断「非零即失败」，要认得这个「部分成功」。

## 七、快照也要定期清扫：forget 加 prune

快照一直留着当然安全，可仓库不会自己变小。restic 把「删快照」和「清数据」刻意拆成两步。

**forget 只删快照引用**，并且支持一套保留策略，按时间梯度留底：`--keep-last N`（留最近 N 个）、`--keep-daily`、`--keep-weekly`、`--keep-monthly`、`--keep-yearly` 分别按日、周、月、年保留。强烈建议先加 `--dry-run` 预演，看清楚「keep 哪些、remove 哪些」再真跑。也可以直接指定快照 ID 精确删除。

但 forget 之后，那些没人引用的块还在 pack 里躺着——**prune 才真正回收磁盘**，它会重写 pack、剔掉无引用数据。叶扬删掉第四轮快照和随后的零增量快照再 prune，账面对得严丝合缝：

```text
to delete:   5 blobs / 758.800 KiB
remaining:  19 blobs / 5.291 MiB
仓库体积      6.2M → 5.4M
```

日常自动化可以一条 `restic forget --prune` 连着做，再挂到计划任务上，备份和清理就都不用人管了。`restic tag` 还能事后给快照补标签——和 Git 改历史一样，这会重写快照、生成新的快照 ID，是内容寻址的必然结果。

## 八、和 rclone 合体：异地容灾

备份只放在一块硬盘上不叫容灾。restic 和 rclone 这对搭档有三种合体姿势，叶扬全部实测过。

**姿势一，restic 的原生 rclone 后端。** 仓库路径写成 `rclone:远端名:路径`，restic 会在后台自动拉起 rclone 与远端通信：

```bash
restic -r rclone:offsite:offsite-disk/restic-repo init
restic -r rclone:offsite:offsite-disk/restic-repo backup data
```

init、backup、check 一路通过，check 在远端仓库上照样报 no errors found。这意味着 restic 能直接把版本化备份落到 rclone 支持的七十多种存储上。

**姿势二，用 rclone 搬运整个仓库。** restic 仓库是自包含的，`rclone copy repo offsite:repo-copy` 整体搬过去，副本可以直接当仓库用——snapshots、check 全部正常。这特别适合「本地一份高速仓库，定期往异地推一份镜像」。

**姿势三，restic copy 跨仓库智能复制。** 它不是搬文件，而是按快照复制，而且去重也保持在 pack 级别——四个快照同步过去，实际只复制了 2 个 pack。这里有个实打实的坑：copy 涉及两个仓库，**源仓库的密码要用 `--from-password-file` 单独给**，漏了它会报一个看着摸不着头脑的错：`an empty password is not allowed`。

三条路组合起来的最佳实践很清晰：本地或常连的仓库负责日常高频备份，rclone 后端放异地，再用 copy 定期把快照推过去——本地可秒级恢复，异地能扛火灾和勒索。

## 九、Windows 上的两个「没有」

跨平台工具在 Windows 上总有边界，restic 这两条提前知道，能省掉翻文档的时间：

- **没有 mount 命令。** Linux 上可以把快照挂成一个目录，像浏览普通文件夹一样翻看历史版本；Windows 构建里干脆没有这个命令。要取数据，用 restore、dump、ls 替代。
- **没有 VSS 卷影副本。** restic 在 Windows 上不会去拍系统卷快照，所以正被应用独占打开的文件读不到，备份会以退出码 3 收场。要么先关掉相关应用，要么先把数据导出到普通文件再备。

至于压缩，version 2 仓库默认 auto 策略：文本和元数据正常压，已经是压缩格式的内容不白费力气。前面那 5MB 随机数据，5.292 MiB 进去、5.290 MiB 存储，几乎没变化，就是因为随机数据本就压不动。

## 十、什么时候值得用，什么时候别用

值得 restic 上场的场景很明确：文档、代码、照片这类要长期保存、又怕误删改坏的东西，想要一条能回到任意历史版本的退路。它的快照、去重、加密和校验，正好补齐 rclone 不做版本化的那块。

但也别拿它干所有活。**整机系统盘、要还原到「能开机」的裸机备份**，restic 不擅长，那种场景该选磁盘映像类工具。restic 管的是文件层面的数据资产。

最后还是那句最朴素的话：备份软件再靠谱，也请亲手 restore 一次。能存进去不算本事，能取回来、取回来的东西一字不差，才算这条备份链路真正通了。

## 术语表

- **repository（仓库）**：备份的存储目的地，本地或远端皆可，整体加密。
- **snapshot（快照）**：一次备份的时间点，记录当时的目录树与文件版本。
- **blob（块）**：最小数据单元，data blob 装文件内容，tree blob 装目录结构。
- **pack（包）**：若干 blob 打包加密后的物理文件。
- **CDC 内容定义分块**：用滚动哈希按内容决定切块边界，局部修改只影响局部块，是去重高效的根源。
- **parent snapshot（父快照）**：本次备份参照的上一个快照，用来快速识别哪些文件没变。
- **forget / prune**：前者删除快照引用，后者真正清理无引用数据、回收空间。
- **rclone 后端**：restic 仓库写成 `rclone:远端:路径`，底层借 rclone 访问七十多种存储。
- **restic copy**：跨仓库复制快照，按 pack 去重传输；源仓库密码需用 `--from-password-file` 单独提供。
