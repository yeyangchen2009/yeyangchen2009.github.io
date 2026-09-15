/* GmeekMermaid —— mermaid 图表自动检测、按需加载
 * 作用域：config 的 script 只注入文章页/固定页；插件先查
 *         div.highlight-source-mermaid（GitHub markdown API 对
 *         ```mermaid 围栏块的高亮产物），没有图表立即退出，零开销。
 * 有图表才动态加载 /mermaid.min.js（约 3.5MB，仅含图文章承担），
 * 随后提取源码、按站点明暗主题渲染；切换主题自动重绘。
 * 兼容旧的手动挂载（文章末行 JSON 自行引入 mermaid.min.js 的情形）：
 * 全局 mermaid 已存在则直接渲染、不重复加载。
 */
(function () {
    var nodes = document.querySelectorAll('div.highlight-source-mermaid');
    if (!nodes.length) return;

    injectStyle();

    // 先于任何渲染把高亮块换成自己的容器，提取纯文本图表源码
    var blocks = Array.prototype.map.call(nodes, function (node) {
        var pre = node.querySelector('pre');
        var src = (pre ? pre.textContent : node.textContent)
            .replace(/^\n+/, '').replace(/\n+$/, '');
        var wrap = document.createElement('div');
        wrap.className = 'mermaid-wrap';
        node.parentNode.replaceChild(wrap, node);
        return { wrap: wrap, src: src };
    });

    if (window.mermaid) {
        boot();
    } else {
        loadScript('/mermaid.min.js').then(boot).catch(function (e) {
            console.error('GmeekMermaid: mermaid.min.js 加载失败', e);
        });
    }

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
        if (document.getElementById('gmeek-mermaid-style')) return;
        var style = document.createElement('style');
        style.id = 'gmeek-mermaid-style';
        style.textContent = '.mermaid-wrap{margin:18px 0;overflow-x:auto;}';
        document.head.appendChild(style);
    }

    function currentTheme() {
        return document.documentElement.getAttribute('data-color-mode') === 'dark'
            ? 'dark' : 'default';
    }

    var rendering = false;
    async function draw() {
        if (rendering) return;
        rendering = true;
        blocks.forEach(function (b) {
            b.wrap.innerHTML = '<pre class="mermaid"></pre>';
            b.wrap.firstChild.textContent = b.src;
        });
        mermaid.initialize({
            startOnLoad: false,
            theme: currentTheme(),
            securityLevel: 'loose',
            flowchart: { htmlLabels: true, useMaxWidth: true }
        });
        try {
            await mermaid.run({ nodes: document.querySelectorAll('.mermaid-wrap .mermaid') });
        } catch (e) {
            console.error('GmeekMermaid render error:', e);
        }
        rendering = false;
    }

    function boot() {
        draw();
        var switchBtn = document.querySelector('[title="切换主题"]');
        if (switchBtn) switchBtn.addEventListener('click', function () { setTimeout(draw, 100); });
    }
})();
