/* GmeekTocBot —— 桌面端文章目录（tocbot 4.27.4 本地化 + Primer 适配）
 * 基于官方 GmeekTocBot.js（Meekdai/Gmeek/plugins/）改造，替代 GmeekTOC：
 *   1. 资产本地化：tocbot 引擎（约 11KB）放 /tocbot/tocbot.min.js，
 *      CDN 改本地路径，零第三方请求；tocbot.css 不单独加载，六条规则
 *      内联在下方并全部换 Primer 变量（原版竖线色 #eee/#54bc4b 不适配暗色）；
 *   2. tocbot 4.27.4 只读 heading.id、不自己生成，插件先用本站统一算法
 *      （trim→空白转连字符→toLowerCase，与 GmeekTOC/articletoc 逐字一致）
 *      幂等建 id；
 *   3. tocbot 每次刷新会 innerHTML="" 清空 tocSelector，故「文章目录」标题
 *      与 Top 回顶按钮放在外层卡片，.toc-nav 容器单独交给 tocbot；
 *   4. 补 GmeekTOC 有而 tocbot 不自带的标题与 Top 按钮；滚动监听用
 *      addEventListener（原版 window.onscroll 赋值会覆盖其他插件的监听）；
 *   5. 删掉官方插件结尾给 body 硬塞 100vh 空白 div 的写法（会把评论区
 *      推走一整屏）；代价：最后一个标题在页面过短时可能无法滚到激活线，
 *      本站文章后有评论区，实际影响可忽略；
 *   6. 无 .markdown-body 或正文无标题时静默退出（archive 等固定页）；
 *   7. 桌面（>1249px）固定右侧 200px；≤1249px 退化为文首静态块——与
 *      articletoc 同装时，其小屏规则 .toc{display:none} 会藏掉本卡片，
 *      手机端由右下角 ☰ 浮层当班（G14 的分工原封不动）。
 */
(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var body = document.querySelector('.markdown-body');
        var contentContainer = document.getElementById('content');
        if (!body || !contentContainer) return;

        var headings = body.querySelectorAll('h1, h2, h3, h4, h5, h6');
        if (!headings.length) return;

        // 统一标题 id（幂等，与 GmeekTOC/articletoc 同一算法）
        Array.prototype.forEach.call(headings, function (h) {
            if (!h.id) h.id = h.textContent.trim().replace(/\s+/g, '-').toLowerCase();
        });

        injectStyle();

        // 外层卡片：标题 + tocbot 专用容器 + Top 按钮
        var card = document.createElement('div');
        card.className = 'toc';
        card.innerHTML =
            '<div class="toc-title">文章目录</div>' +
            '<div class="toc-nav"></div>' +
            '<a class="toc-end" role="button" tabindex="0" aria-label="回到顶部">Top</a>';
        contentContainer.insertBefore(card, contentContainer.firstChild);

        var topBtn = card.querySelector('.toc-end');
        function toggleTop() {
            var y = window.pageYOffset || document.documentElement.scrollTop;
            topBtn.classList.toggle('is-visible', y > 20);
        }
        window.addEventListener('scroll', toggleTop, { passive: true });
        toggleTop();
        topBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        loadScript('/tocbot/tocbot.min.js').then(function () {
            window.tocbot.init({
                tocSelector: '.toc-nav',
                contentSelector: '.markdown-body',
                headingSelector: 'h1, h2, h3, h4, h5, h6',
                scrollSmooth: true,
                scrollSmoothOffset: -10,
                headingsOffset: 10
            });
        }).catch(function (e) {
            console.error('GmeekTocBot: tocbot.min.js 加载失败', e);
        });

        console.log('\n %c GmeekTocBot(local) Plugins https://github.com/Meekdai/Gmeek \n',
            'padding:5px 0;background:#C333D0;color:#fff');
    });

    function loadScript(src) {
        return new Promise(function (resolve, reject) {
            var s = document.createElement('script');
            s.src = src;
            s.onload = resolve;
            s.onerror = function () { reject(new Error('load fail: ' + src)); };
            document.head.appendChild(s);
        });
    }

    function injectStyle() {
        if (document.getElementById('gmeek-tocbot-style')) return;
        var style = document.createElement('style');
        style.id = 'gmeek-tocbot-style';
        style.textContent = [
            /* 卡片定位（沿用 GmeekTOC 的视觉坐标） */
            '.toc{position:fixed;top:130px;left:50%;',
            'transform:translateX(50%) translateX(320px);',
            'width:200px;max-height:70vh;overflow-y:auto;padding:10px;',
            'border:1px solid var(--color-border-default);border-radius:6px;',
            'background:var(--color-canvas-overlay,var(--color-canvas-default));',
            'box-shadow:var(--color-shadow-medium,0 2px 10px rgba(0,0,0,.1));',
            'font-size:14px;line-height:1.5;z-index:200;}',
            '.toc-title{font-weight:600;text-align:center;color:var(--color-fg-default);',
            'padding-bottom:8px;margin-bottom:6px;border-bottom:1px solid var(--color-border-muted);}',
            /* tocbot 列表结构（tocbot.css 六条规则的 Primer 化版本） */
            '.toc-nav>.toc-list{overflow:hidden;position:relative;margin:0;padding:0;}',
            '.toc-list{margin:0;padding-left:12px;}',
            '.toc-list li{list-style:none;}',
            /* 折叠过渡期间放开原版 max-height:1000px 的裁切，交给卡片滚动条 */
            '.is-collapsible{max-height:none;overflow:visible;}',
            '.is-collapsed{max-height:0;overflow:hidden;}',
            'a.toc-link{display:block;position:relative;box-sizing:border-box;',
            'color:var(--color-fg-muted);text-decoration:none;',
            'padding:3px 6px 3px 10px;border-radius:4px;}',
            'a.toc-link:hover{background:var(--color-accent-subtle);}',
            /* 左侧层级竖线：默认灰，当前章节蓝 */
            '.toc-link::before{content:" ";position:absolute;left:0;top:0;bottom:0;',
            'width:2px;background-color:var(--color-border-muted);}',
            'a.toc-link.is-active-link{font-weight:700;color:var(--color-accent-fg);}',
            '.is-active-link::before{background-color:var(--color-accent-fg);}',
            /* Top 按钮 */
            '.toc-end{display:none;margin-top:6px;padding-top:8px;text-align:center;',
            'font-weight:700;color:var(--color-fg-muted);cursor:pointer;',
            'border-top:1px solid var(--color-border-muted);}',
            '.toc-end:hover{color:var(--color-accent-fg);}',
            '.toc-end.is-visible{display:block;}',
            /* 小屏：退化为文首静态块（与 articletoc 同装时被其 display:none 接管） */
            '@media (max-width:1249px){',
            '.toc{position:static;top:auto;left:auto;transform:none;',
            'width:auto;max-height:none;margin:0 0 20px;',
            'background:var(--color-canvas-subtle);box-shadow:none;}}'
        ].join('');
        document.head.appendChild(style);
    }
})();
