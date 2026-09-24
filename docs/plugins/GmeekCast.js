/* GmeekCast —— asciinema 终端回放自动检测、按需加载
 * 作用域：config 的 script 注入文章页/固定页；写作者只需在正文
 *         写一个普通 markdown 链接指向 cast：
 *         [▶ 播放终端回放](/casts/x.cast)
 *         （GitHub markdown API 会剥 div 的 class/data-* 属性，
 *         但 a 的 href 一定保留。）插件扫描 #postBody 内 href
 *         形如 /casts/*.cast 的链接，把链接替换成播放器；插件
 *         未运行时链接仍是 cast 文件的下载入口，天然降级。
 *         没有这种链接立即退出，零开销。
 * 有占位才动态加载 /asciinema/ 下官方 player（css+js，约 200KB，
 * 仅含回放的文章承担），按站点明暗主题挂载；播放器主题不支持
 * 运行时切换，故点"切换主题"时 dispose 后以新主题重建。
 * 补充能力：官方 player 3.x 没有运行时倍速控件（speed 只在
 * create 时生效），本插件在控制栏注入倍速按钮，切换时记下进度
 * 与播放/暂停状态，dispose 后以新 speed 重建并 seek 回原位。
 */
(function () {
    var links = Array.prototype.filter.call(
        document.querySelectorAll('#postBody a[href]'),
        function (a) { return /^\/?casts\/.+\.cast$/.test(a.getAttribute('href')); }
    );
    if (!links.length) return;

    // 链接换成自己的容器，同时记下 cast 路径
    var holders = links.map(function (a) {
        var src = a.getAttribute('href');
        var box = document.createElement('div');
        box.className = 'asciinema-cast';
        box._castSrc = src;
        a.parentNode.replaceChild(box, a);
        return box;
    });

    var THEME = { dark: 'dracula', light: 'solarized-light' };
    var SPEEDS = [1, 1.25, 1.5, 2, 3, 0.5, 0.75];

    function mode() {
        return document.documentElement.getAttribute('data-color-mode') === 'dark'
            ? 'dark' : 'light';
    }

    var states = [];

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

    // 在官方控制栏注入倍速按钮（插在快捷键按钮前）
    function addSpeedButton(st) {
        var bar = st.player.el.querySelector('.ap-control-bar');
        if (!bar || bar.querySelector('.ap-gmeek-speed')) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'ap-button ap-gmeek-speed ap-tooltip-container';
        btn.title = 'Playback speed';
        btn.textContent = st.speed + 'x';
        btn.addEventListener('click', function () {
            var next = SPEEDS[(SPEEDS.indexOf(st.speed) + 1) % SPEEDS.length];
            rebuild(st, { speed: next });
        });
        var kbdBtn = bar.querySelector('.ap-kbd-button');
        bar.insertBefore(btn, kbdBtn);
    }

    function mount(st) {
        if (st.player) st.player.dispose();
        st.playing = false;
        st.player = window.AsciinemaPlayer.create(st.src, st.el, {
            autoPlay: false,
            loop: false,
            theme: THEME[mode()],
            speed: st.speed,
            fit: 'width',
            idleTimeLimit: 2,
            poster: 'npt:0:01'
        });
        st.player.addEventListener('play', function () { st.playing = true; });
        st.player.addEventListener('pause', function () { st.playing = false; });
        addSpeedButton(st);
        st.el._castPlayer = st.player;
        if (typeof st.resumeAt === 'number') {
            st.player.seek(st.resumeAt);
            if (st.resumePlaying) st.player.play();
            st.resumeAt = null;
        }
    }

    // 以新参数（speed 或主题）重建：先存进度与播放态
    function rebuild(st, opts) {
        st.resumeAt = st.player.getCurrentTime();
        st.resumePlaying = !!st.playing;
        if (opts.speed) st.speed = opts.speed;
        mount(st);
    }

    function boot() {
        holders.forEach(function (el) {
            states.push({
                el: el, src: el._castSrc,
                player: null, speed: 1, playing: false
            });
        });
        states.forEach(mount);

        var switchBtn = document.querySelector('[title="切换主题"]');
        if (switchBtn) switchBtn.addEventListener('click', function () {
            setTimeout(function () {
                states.forEach(function (st) { rebuild(st, {}); });
            }, 120);
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
