/* GmeekArchive —— 固定页 archive.html 的时间线归档
 * 仅在 /archive.html 生效（config singlePage 机制生成的固定页）
 * 数据源 postList.json：框架保证固定页只进 singeListJson，不在此文件中
 * 按年分组，组内日期倒序（同日按 issue 编号倒序），发新文自动出现
 * 挂载点由正文 Gmeek-html 彩蛋生成：<div id="archiveTimeline"></div>
 */
(function () {
    if (!/^\/archive\.html(\?.*)?$/.test(location.pathname)) return;

    var box = document.getElementById('archiveTimeline');
    if (!box) return;

    fetch('/postList.json', { cache: 'no-cache' })
        .then(function (r) {
            if (!r.ok) throw new Error('postList fetch failed');
            return r.json();
        })
        .then(render)
        .catch(function (e) {
            console.warn('GmeekArchive:', e && e.message);
            box.className = 'gmeek-ar gmeek-ar-error';
            box.textContent = '文章列表加载失败，请稍后刷新页面再试。';
        });

    function render(list) {
        var posts = Object.keys(list).map(function (key) {
            var item = list[key];
            return {
                num: parseInt(key.replace(/^P/, ''), 10),
                title: item.postTitle,
                url: item.postUrl ? '/' + item.postUrl : '',
                date: item.createdDate || ''
            };
        }).filter(function (p) {
            return p.url && p.num && p.date;
        }).sort(function (a, b) {
            if (a.date !== b.date) return a.date < b.date ? 1 : -1; // 最新在前
            return b.num - a.num;
        });

        var groups = {};
        var years = [];
        posts.forEach(function (p) {
            var y = p.date.slice(0, 4);
            if (!groups[y]) { groups[y] = []; years.push(y); }
            groups[y].push(p);
        });

        injectStyle();

        if (!posts.length) {
            box.className = 'gmeek-ar';
            box.textContent = '还没有文章。';
            return;
        }

        var html = '<div class="gmeek-ar-head">共 <b>' + posts.length.toLocaleString('en-US')
            + '</b> 篇文章 · 始于 <b>' + years[years.length - 1] + '</b> 年</div>';
        years.forEach(function (y) {
            html += '<section class="gmeek-ar-year"><h2 class="gmeek-ar-h">' + y
                + '<span class="gmeek-ar-count">' + groups[y].length + '</span></h2>'
                + '<ul class="gmeek-ar-list">';
            groups[y].forEach(function (p) {
                html += '<li class="gmeek-ar-item"><span class="gmeek-ar-date">' + p.date.slice(5)
                    + '</span><a class="gmeek-ar-title" href="' + p.url + '">'
                    + escapeHtml(p.title) + '</a></li>';
            });
            html += '</ul></section>';
        });
        box.className = 'gmeek-ar';
        box.innerHTML = html;
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }

    function injectStyle() {
        if (document.getElementById('gmeek-ar-style')) return;
        var style = document.createElement('style');
        style.id = 'gmeek-ar-style';
        style.textContent =
            '.gmeek-ar{margin:4px 0 24px;}'
            + '.gmeek-ar-head{font-size:13px;color:var(--color-fg-muted,#656d76);margin:14px 0 18px;}'
            + '.gmeek-ar-head b{color:var(--color-fg-default,#1f2328);font-weight:600;}'
            + '.gmeek-ar-year{margin-bottom:24px;}'
            + '.gmeek-ar-h{display:flex;align-items:center;gap:8px;position:sticky;top:0;'
            + 'background:var(--color-canvas-default,#ffffff);padding:8px 0;margin:0 0 4px;z-index:1;'
            + 'font-size:18px;font-weight:700;border-bottom:1px solid var(--color-border-muted,#d0d7de);}'
            + '.gmeek-ar-count{font-size:12px;font-weight:600;color:var(--color-accent-fg,#0969da);'
            + 'background:var(--color-accent-subtle,#ddf4ff);border-radius:20px;padding:1px 9px;}'
            + '.gmeek-ar-list{list-style:none;margin:0;padding:0 0 0 24px;'
            + 'border-left:2px solid var(--color-border-muted,#d0d7de);}'
            + '.gmeek-ar-item{position:relative;display:flex;align-items:baseline;gap:12px;padding:7px 0;}'
            + '.gmeek-ar-item::before{content:"";position:absolute;left:-29px;top:15px;width:8px;height:8px;'
            + 'border-radius:50%;background:var(--color-accent-fg,#0969da);'
            + 'box-shadow:0 0 0 3px var(--color-canvas-default,#ffffff);}'
            + '.gmeek-ar-date{flex:0 0 46px;font-size:12px;color:var(--color-fg-muted,#656d76);'
            + 'font-variant-numeric:tabular-nums;}'
            + '.gmeek-ar-title{min-width:0;color:var(--color-fg-default,#1f2328);'
            + 'text-decoration:none;line-height:1.5;}'
            + '.gmeek-ar-title:hover{color:var(--color-accent-fg,#0969da);text-decoration:underline;}'
            + '.gmeek-ar-error{color:var(--color-danger-fg,#cf222e);font-size:14px;}'
            + '@media (max-width:600px){'
            + '.gmeek-ar-list{padding-left:20px;}'
            + '.gmeek-ar-item::before{left:-25px;top:14px;}'
            + '.gmeek-ar-date{flex-basis:42px;font-size:11px;}'
            + '.gmeek-ar-title{font-size:14px;}'
            + '.gmeek-ar-h{font-size:16px;}'
            + '.gmeek-ar-year{margin-bottom:18px;}}';
        document.head.appendChild(style);
    }
})();
