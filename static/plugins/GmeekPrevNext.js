/* GmeekPrevNext —— 文章底部"上一篇/下一篇"导航
 * 数据源：/postList.json（Gmeek 每次构建自动生成，含全部普通文章）
 * 排序：createdDate 优先、issue 编号兜底（兼容 timestamp 补发旧文）
 * 边界：非 /post/N.html 页面直接退出；首篇/末篇显示禁用占位
 * 布局：clear:both 避开框架 bottomText 的 float:right（否则 BFC 收缩把卡片压窄）；
 *       标签与日期合并到 meta 行；小屏给浮动小字打 class 还原为整行右对齐
 */
(function () {
    var match = location.pathname.match(/\/post\/(\d+)\.html/);
    if (!match) return; // 首页、/about.html 等固定页不生成导航

    var currentNum = parseInt(match[1], 10);

    injectStyle();

    fetch('/postList.json', { cache: 'no-cache' })
        .then(function (r) {
            if (!r.ok) throw new Error('postList fetch failed');
            return r.json();
        })
        .then(function (list) {
            var posts = Object.keys(list).map(function (key) {
                var item = list[key];
                return {
                    num: parseInt(key.replace(/^P/, ''), 10),
                    title: item.postTitle,
                    url: item.postUrl ? '/' + item.postUrl : '',
                    date: item.createdDate || ''
                };
            }).filter(function (p) { return p.url && p.num; })
              .sort(function (a, b) {
                  if (a.date !== b.date) return a.date < b.date ? -1 : 1;
                  return a.num - b.num;
              });

            var idx = posts.findIndex ? posts.findIndex(function (p) { return p.num === currentNum; })
                                      : posts.map(function (p) { return p.num; }).indexOf(currentNum);
            if (idx < 0) return;

            var older = posts[idx - 1] || null; // 时间线上更早
            var newer = posts[idx + 1] || null; // 更新

            var nav = document.createElement('nav');
            nav.className = 'gmeek-pn';
            nav.setAttribute('aria-label', '文章导航');
            nav.innerHTML = cell('上一篇', older, true) + cell('下一篇', newer, false);

            var anchor = document.getElementById('cmButton') || document.getElementById('comments');
            if (anchor && anchor.parentNode) {
                // 框架 post.html 的版权小字是 float:right 的裸 div，小屏长中文会被挤成竖排，
                // 还会把 flex 导航（BFC）压窄。打个 class，交给 CSS 在小屏还原为整行右对齐。
                var kids = anchor.parentNode.children;
                for (var i = 0; i < kids.length; i++) {
                    var cs = kids[i].style && kids[i].style.cssText || '';
                    if (/float\s*:\s*right/.test(cs)) kids[i].classList.add('gmeek-pn-bottomtext');
                }
                anchor.parentNode.insertBefore(nav, anchor);
            } else {
                document.getElementById('content').appendChild(nav);
            }
        })
        .catch(function (e) { console.warn('GmeekPrevNext:', e && e.message); });

    function cell(label, post, isLeft) {
        var cls = 'gmeek-pn-item' + (isLeft ? '' : ' gmeek-pn-next') + (post ? '' : ' is-disabled');
        if (post) {
            return '<a class="' + cls + '" href="' + post.url + '">'
                + '<span class="gmeek-pn-meta"><span class="gmeek-pn-label">' + label
                + '</span><span class="gmeek-pn-date">' + post.date + '</span></span>'
                + '<span class="gmeek-pn-title">' + escapeHtml(post.title) + '</span></a>';
        }
        return '<div class="' + cls + '">'
            + '<span class="gmeek-pn-meta"><span class="gmeek-pn-label">' + label
            + '</span></span>'
            + '<span class="gmeek-pn-title">已经到尽头啦</span></div>';
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"]/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
        });
    }

    function injectStyle() {
        var style = document.createElement('style');
        style.textContent = ''
            // clear:both 是关键：框架的版权小字 float:right，flex 容器建立 BFC 会主动
            // 收缩避让浮动元素，不声明 clear 两张卡片会被整体压窄（手机端只剩 60% 宽）
            + '.gmeek-pn{display:flex;gap:10px;clear:both;margin:28px 0 10px;}'
            + '.gmeek-pn-item{flex:1 1 0;min-width:0;display:flex;flex-direction:column;gap:7px;'
            + 'padding:12px 14px;border:1px solid var(--color-border-muted,#d0d7de);border-radius:12px;'
            + 'color:var(--color-fg-default,#1f2328);text-decoration:none;'
            + 'transition:border-color .15s ease,background-color .15s ease,transform .15s ease;}'
            + '.gmeek-pn-item:hover{border-color:var(--color-accent-fg,#0969da);'
            + 'background:var(--color-accent-subtle,#ddf4ff);transform:translateY(-1px);text-decoration:none;}'
            + '.gmeek-pn-next{align-items:flex-end;text-align:right;}'
            + '.gmeek-pn-meta{display:flex;align-items:baseline;justify-content:space-between;'
            + 'gap:10px;width:100%;font-size:12px;color:var(--color-fg-muted,#656d76);}'
            + '.gmeek-pn-next .gmeek-pn-meta{flex-direction:row-reverse;}'
            + '.gmeek-pn-label{white-space:nowrap;}'
            + '.gmeek-pn-item:not(.is-disabled) .gmeek-pn-label::before{content:"\\2190  ";}'
            + '.gmeek-pn-next:not(.is-disabled) .gmeek-pn-label::before{content:"";}'
            + '.gmeek-pn-next:not(.is-disabled) .gmeek-pn-label::after{content:"  \\2192";}'
            + '.gmeek-pn-title{font-weight:600;line-height:1.4;display:-webkit-box;-webkit-box-orient:vertical;'
            + '-webkit-line-clamp:2;overflow:hidden;}'
            + '.gmeek-pn-date{font-size:12px;color:var(--color-fg-muted,#656d76);white-space:nowrap;}'
            + '.gmeek-pn-item.is-disabled{opacity:.45;pointer-events:none;}'
            + '@media (max-width:600px){'
            + '.gmeek-pn-bottomtext{float:none !important;display:block;text-align:right;margin:0 2px 2px;}'
            + '.gmeek-pn{flex-direction:column;gap:8px;margin:14px 0 8px;}'
            + '.gmeek-pn-item{flex:0 0 auto;padding:11px 14px;border-radius:10px;gap:5px;}'
            + '.gmeek-pn-next{align-items:flex-start;text-align:left;}'
            + '.gmeek-pn-next .gmeek-pn-meta{flex-direction:row;}'
            + '.gmeek-pn-meta{font-size:11px;}'
            + '.gmeek-pn-date{font-size:11px;}'
            + '.gmeek-pn-title{font-size:15px;line-height:1.45;-webkit-line-clamp:2;}}';
        document.head.appendChild(style);
    }
})();
