/* GmeekPager —— 列表页数字分页条
 * 作用域：首页 /、/index.html 与 /pageN.html（config 的 indexScript 只注入列表页 plist）
 * 数据源：/postList.json，按 /^P\d+$/ 过滤掉 labelColorDict 等非文章键，每 15 篇一页
 * 做法：完整保留框架原生的“上一页/下一页”节点（属性、箭头、禁用态都不动），
 *       在中间插入 GitHub 风格数字页码；按钮样式、当前页蓝底、省略号与三档
 *       响应式显隐全部复用 Primer 21 内建的 .pagination 规则，零自定义 CSS：
 *       手机(<544px)只露上下页；平板(544–768px)露首尾页码与当前页；桌面全显。
 * 降级：文章不足一页时框架不渲染 nav（插件直接退出）；fetch 失败或数据异常时
 *       保持框架原生“上一页/下一页”条不动，不影响翻页。
 */
(function () {
    var m = location.pathname.match(/\/page(\d+)\.html$/);
    var isHome = /(?:^\/$)|\/index\.html$/.test(location.pathname);
    if (!m && !isHome) return;
    var current = m ? parseInt(m[1], 10) : 1;

    var box = document.querySelector('.paginate-container .pagination');
    if (!box) return;

    var ONE_PAGE = 15; // Gmeek 默认 onePageListNum；若在 config.json 改过需同步改这里

    fetch('/postList.json', { cache: 'no-cache' })
        .then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        })
        .then(function (list) {
            var count = 0;
            Object.keys(list).forEach(function (k) {
                if (/^P\d+$/.test(k) && list[k] && list[k].postUrl) count++;
            });
            var total = Math.ceil(count / ONE_PAGE);
            if (total < 2 || current > total) return; // 单页或数据异常，保留原生条

            var prev = box.querySelector('.previous_page');
            var next = box.querySelector('.next_page');
            if (!prev || !next) return;

            var nav = box.closest('nav');
            if (nav) nav.setAttribute('aria-label', '分页');
            // 可见文字已是中文，原生按钮的英文 aria-label 顺手汉化（只改可点按钮）
            if (prev.getAttribute('aria-label')) prev.setAttribute('aria-label', '上一页');
            if (next.getAttribute('aria-label')) next.setAttribute('aria-label', '下一页');

            box.textContent = '';
            box.appendChild(prev);
            buildSequence(current, total).forEach(function (item) {
                box.appendChild(renderItem(item, item === current));
            });
            box.appendChild(next);
        })
        .catch(function () { /* 网络失败：原生上一页/下一页原样保留 */ });

    // 首页、末页常驻；当前页两侧各一页；跨度大于 1 的空档用省略号折叠；
    // 总页不多（≤7）时全部铺开，省略号只在真正需要时出现
    function buildSequence(cur, total) {
        if (total <= 7) {
            var all = [];
            for (var k = 1; k <= total; k++) all.push(k);
            return all;
        }
        var nums = [];
        for (var n = 1; n <= total; n++) {
            if (n === 1 || n === total || (n >= cur - 1 && n <= cur + 1)) nums.push(n);
        }
        var out = [];
        for (var i = 0; i < nums.length; i++) {
            if (i > 0 && nums[i] - nums[i - 1] > 1) out.push('gap');
            out.push(nums[i]);
        }
        return out;
    }

    function renderItem(item, isCurrent) {
        if (item === 'gap') {
            var gap = document.createElement('span');
            gap.className = 'gap';
            gap.setAttribute('aria-hidden', 'true');
            gap.textContent = '…';
            return gap;
        }
        if (isCurrent) {
            var cur = document.createElement('em');
            cur.className = 'current';
            cur.setAttribute('aria-current', 'page');
            cur.textContent = String(item);
            return cur;
        }
        var a = document.createElement('a');
        a.href = item === 1 ? '/' : '/page' + item + '.html';
        a.setAttribute('aria-label', '第 ' + item + ' 页');
        a.textContent = String(item);
        return a;
    }
})();
