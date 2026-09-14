/* articletoc —— 小屏文章目录浮层
 * 原作者：Tiengming（Gmeek 官方仓库收录），本站在原版基础上做了四处适配：
 *   1. 类名隔离 .toc-mobile / .toc-mobile-icon（原版与 GmeekTOC 同名 .toc，
 *      两个插件同时加载时 CSS 互相污染——opacity:0 会把桌面常驻目录藏掉）；
 *   2. 配色全部换 Primer CSS 变量，跟随站点三态主题（原版 prefers-color-scheme
 *      在“手动暗色 + 系统亮色”时失配，见官方 issue #196）；
 *   3. 桌面（>1249px）隐藏圆形按钮交给 GmeekTOC；小屏（≤1249px）才显示按钮，
 *      同时隐藏 GmeekTOC 在小屏退化出的文首静态目录块，二者只留一个；
 *   4. 无正文/无标题时静默退出；点目录链接、点外部、按 Esc 都会收起浮层。
 * 锚点 id 算法与 GmeekTOC 完全一致，两个插件同页运行时复用同一批标题锚点。
 */
(function () {
    var body = document.querySelector('.markdown-body');
    if (!body) return;
    var headings = body.querySelectorAll('h1, h2, h3, h4, h5, h6');
    if (!headings.length || document.getElementById('tocMobilePanel')) return;

    injectStyle();

    var panel = document.createElement('div');
    panel.className = 'toc-mobile';
    panel.id = 'tocMobilePanel';
    Array.prototype.forEach.call(headings, function (h) {
        if (!h.id) h.id = h.textContent.trim().replace(/\s+/g, '-').toLowerCase();
        var a = document.createElement('a');
        a.href = '#' + h.id;
        a.textContent = h.textContent;
        a.style.paddingLeft = (parseInt(h.tagName.charAt(1), 10) - 1) * 10 + 'px';
        a.addEventListener('click', closePanel);
        panel.appendChild(a);
    });
    document.body.appendChild(panel);

    var icon = document.createElement('div');
    icon.className = 'toc-mobile-icon';
    icon.setAttribute('role', 'button');
    icon.setAttribute('tabindex', '0');
    icon.setAttribute('aria-label', '文章目录');
    icon.setAttribute('aria-expanded', 'false');
    icon.textContent = '☰';
    icon.addEventListener('click', function (e) {
        e.stopPropagation();
        togglePanel();
    });
    icon.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); togglePanel(); }
    });
    document.body.appendChild(icon);

    document.addEventListener('click', function (e) {
        if (panel.classList.contains('is-show') &&
            !panel.contains(e.target) && !icon.contains(e.target)) {
            closePanel();
        }
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closePanel();
    });

    function openPanel() {
        panel.classList.add('is-show');
        icon.classList.add('is-active');
        icon.textContent = '✖';
        icon.setAttribute('aria-expanded', 'true');
    }
    function closePanel() {
        panel.classList.remove('is-show');
        icon.classList.remove('is-active');
        icon.textContent = '☰';
        icon.setAttribute('aria-expanded', 'false');
    }
    function togglePanel() {
        if (panel.classList.contains('is-show')) closePanel();
        else openPanel();
    }

    function injectStyle() {
        var css = [
            '.toc-mobile{position:fixed;bottom:64px;right:20px;z-index:1000;',
            'width:250px;max-width:calc(100vw - 40px);max-height:70vh;overflow-y:auto;',
            'padding:10px;border-radius:8px;',
            'background:var(--color-canvas-overlay,var(--color-canvas-default));',
            'border:1px solid var(--color-border-default);',
            'box-shadow:var(--color-shadow-large);',
            'opacity:0;visibility:hidden;transform:translateY(12px) scale(.98);',
            'transition:opacity .25s ease,transform .25s ease,visibility .25s;}',
            '.toc-mobile.is-show{opacity:1;visibility:visible;transform:translateY(0) scale(1);}',
            '.toc-mobile a{display:block;color:var(--color-fg-default);text-decoration:none;',
            'font-size:14px;line-height:1.5;padding:5px 4px;',
            'border-bottom:1px solid var(--color-border-muted);}',
            '.toc-mobile a:last-child{border-bottom:0;}',
            '.toc-mobile a:hover{background:var(--color-accent-subtle);border-radius:4px;}',
            '.toc-mobile-icon{position:fixed;bottom:20px;right:20px;z-index:1001;',
            'width:42px;height:42px;border-radius:50%;display:none;',
            'align-items:center;justify-content:center;font-size:20px;cursor:pointer;',
            'user-select:none;-webkit-tap-highlight-color:transparent;',
            'color:var(--color-accent-fg);background:var(--color-canvas-default);',
            'border:1px solid var(--color-border-default);',
            'box-shadow:var(--color-shadow-medium);',
            'transition:transform .25s ease,background .2s ease,color .2s ease,border-color .2s ease;}',
            '.toc-mobile-icon:hover{transform:scale(1.08);}',
            '.toc-mobile-icon:active{transform:scale(.92);}',
            '.toc-mobile-icon.is-active{color:#ffffff;',
            'background:var(--color-accent-emphasis);border-color:var(--color-accent-emphasis);}',
            /* 断点与 GmeekTOC 的 @media(max-width:1249px) 完全对齐：
               小屏隐藏它退化出的文首静态目录块，改由右下角浮层接管 */
            '@media (max-width:1249px){',
            '.toc{display:none;}',
            '.toc-mobile-icon{display:flex;}}'
        ].join('');
        var style = document.createElement('style');
        style.id = 'tocMobileStyle';
        style.textContent = css;
        document.head.appendChild(style);
    }
})();
