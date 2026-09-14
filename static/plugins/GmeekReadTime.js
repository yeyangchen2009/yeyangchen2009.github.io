/* GmeekReadTime —— 文章标题下的"字数 · 阅读时长"
 * 数据源：#postBody 渲染后正文（构建期 GitHub gfm 渲染，运行时统计）
 * 计数规则：CJK 汉字按字计；连续拉丁字母/数字串按 1 个词计；标点空白不计
 * 估算速度：中文约 400 字/分钟，不足 1 分钟按 1 分钟
 * 边界：仅 /post/N.html 生效；about 等固定页虽注入脚本但正则自退
 */
(function () {
    var match = location.pathname.match(/\/post\/(\d+)\.html/);
    if (!match) return;

    var body = document.getElementById('postBody');
    if (!body) return;

    var text = body.textContent || '';
    var count = 0;

    // CJK 统一表意文字：基本区 4E00-9FFF、扩展A 3400-4DBF、兼容区 F900-FAFF
    var cjk = text.match(/[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]/g);
    if (cjk) count += cjk.length;

    // 拉丁单词：连续字母/数字，允许词内撇号与连字符（don't / well-known）
    var words = text.match(/[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*/g);
    if (words) count += words.length;

    if (count < 10) return; // 正文异常短（错误页/占位页）时不出手

    var minutes = Math.max(1, Math.round(count / 400));

    // count/minutes 均为程序算出的数字，无 XSS 面
    var meta = document.createElement('div');
    meta.className = 'gmeek-rt';
    meta.setAttribute('aria-label', '字数与阅读时长');
    meta.innerHTML =
        '<span class="gmeek-rt-item">📖 全文约 ' + count.toLocaleString('en-US') + ' 字</span>'
        + '<span class="gmeek-rt-sep" aria-hidden="true">·</span>'
        + '<span class="gmeek-rt-item">阅读约 <b>' + minutes + '</b> 分钟</span>';

    injectStyle();

    // 插在 #content 最前（标题区 #header 之下、正文 #postBody 之上）
    var content = document.getElementById('content');
    if (content) content.insertBefore(meta, content.firstChild);

    function injectStyle() {
        if (document.getElementById('gmeek-rt-style')) return;
        var style = document.createElement('style');
        style.id = 'gmeek-rt-style';
        style.textContent =
            '.gmeek-rt{display:flex;align-items:center;gap:8px;flex-wrap:wrap;'
            + 'margin:0 0 14px;font-size:13px;line-height:1.6;'
            + 'color:var(--color-fg-muted,#656d76);}'
            + '.gmeek-rt b{font-weight:600;color:var(--color-fg-default,#1f2328);}'
            + '.gmeek-rt-sep{opacity:.55;}'
            + '@media (max-width:600px){.gmeek-rt{font-size:12px;margin-bottom:12px;}}';
        document.head.appendChild(style);
    }
})();
