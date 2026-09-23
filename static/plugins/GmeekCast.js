/* GmeekCast —— asciinema 终端回放自动检测、按需加载
 * 作用域：config 的 script 注入文章页/固定页；插件先找
 *         .asciinema-cast[data-src] 占位节点（正文用原生 HTML
 *         写 <div class="asciinema-cast" data-src="/casts/x.cast"></div>），
 *         没有占位立即退出，零开销。
 * 有占位才动态加载 /asciinema/ 下官方 player（css+js，约 200KB，
 * 仅含回放的文章承担），按站点明暗主题挂载；播放器主题不支持
 * 运行时切换，故点"切换主题"时 dispose 后以新主题重建。
 */
(function () {
    var holders = document.querySelectorAll('.asciinema-cast[data-src]');
    if (!holders.length) return;

    var THEME = { dark: 'dracula', light: 'github' };
    function mode() {
        return document.documentElement.getAttribute('data-color-mode') === 'dark'
            ? 'dark' : 'light';
    }

    var instances = [];

    function loadCss(href) {
        return new Promise(function (resolve, reject) {
            var l = document.createElement('link');
            l.rel = 'stylesheet';
            l.href = href;
            l.onload = resolve;
            l.onerror = function () { reject(new Error('load fail: ' + href)); };
            document.head.appendChild(l);
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

    function mountAll() {
        instances.forEach(function (item) {
            if (item.player) {
                item.player.dispose();
                item.player = null;
            }
            item.player = window.AsciinemaPlayer.create(item.src, item.el, {
                autoPlay: false,
                loop: false,
                theme: THEME[mode()],
                fit: 'width',
                idleTimeLimit: 2,
                poster: 'npt:0:01'
            });
        });
    }

    function boot() {
        holders.forEach(function (el) {
            instances.push({ el: el, src: el.getAttribute('data-src'), player: null });
        });
        mountAll();
        var switchBtn = document.querySelector('[title="切换主题"]');
        if (switchBtn) switchBtn.addEventListener('click', function () {
            setTimeout(mountAll, 120);
        });
    }

    if (window.AsciinemaPlayer) {
        boot();
        return;
    }
    Promise.all([
        loadCss('/asciinema/asciinema-player.css'),
        loadScript('/asciinema/asciinema-player.min.js')
    ]).then(boot).catch(function (e) {
        console.error('GmeekCast: player 加载失败', e);
    });
})();
