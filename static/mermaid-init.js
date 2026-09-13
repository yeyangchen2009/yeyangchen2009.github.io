/* Gmeek mermaid 加载器：把 GitHub 风格的 ```mermaid 代码块转成图表，主题跟随站点明暗切换 */
(function () {
    var codes = Array.prototype.slice.call(document.querySelectorAll('code.language-mermaid'));
    if (!codes.length || typeof mermaid === 'undefined') return;

    var blocks = codes.map(function (code) {
        var pre = code.closest('pre');
        var wrap = document.createElement('div');
        wrap.className = 'mermaid-wrap';
        pre.parentNode.replaceChild(wrap, pre);
        return { wrap: wrap, src: code.textContent };
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
