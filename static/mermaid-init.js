/* Gmeek mermaid 加载器：把 mermaid 代码块（GitHub API 会高亮成 div.highlight-source-mermaid）转成图表，主题跟随站点明暗切换 */
(function () {
    var nodes = Array.prototype.slice.call(document.querySelectorAll('div.highlight-source-mermaid, code.language-mermaid'));
    if (!nodes.length || typeof mermaid === 'undefined') return;

    var blocks = nodes.map(function (node) {
        var pre = node.querySelector ? node.querySelector('pre') : node.closest('pre');
        var holder = node.classList.contains('highlight-source-mermaid') ? node : pre;
        var src = (pre ? pre.textContent : node.textContent).replace(/\n+$/g, '').replace(/^\n+/, '');

        var wrap = document.createElement('div');
        wrap.className = 'mermaid-wrap';
        holder.parentNode.replaceChild(wrap, holder);
        return { wrap: wrap, src: src };
    });

    function currentTheme() {
        return document.documentElement.getAttribute('data-color-mode') === 'dark' ? 'dark' : 'default';
    }

    var running = false;
    async function draw() {
        if (running) return;
        running = true;
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
            console.error('mermaid render error:', e);
        }
        running = false;
    }

    draw();

    var switchBtn = document.querySelector('[title="切换主题"]');
    if (switchBtn) switchBtn.addEventListener('click', function () { setTimeout(draw, 100); });
})();
