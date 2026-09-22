/* GmeekPagefind.js  全站静态搜索（Pagefind）
 * 索引由构建流程在 Generate 之后生成到 /pagefind/，纯静态、无后端。
 * 入口：列表页劫持 #buttonSearch（保留原图标）；其余页面在 .title-right 注入同款按钮。
 */
(function () {
    'use strict';

    var SEARCH_ICON = 'M10.68 11.74a5.5 5.5 0 1 1 1.06-1.06l3.04 3.04a.75.75 0 1 1-1.06 1.06l-3.04-3.04ZM11.5 7a4.5 4.5 0 1 0-9 0 4.5 4.5 0 0 0 9 0Z';

    function injectStyle() {
        var style = document.createElement('style');
        style.textContent = [
            '#pf-modal{position:fixed;inset:0;z-index:100;display:none;}',
            '#pf-modal.open{display:block;}',
            '#pf-backdrop{position:absolute;inset:0;background:rgba(1,4,9,.55);}',
            '#pf-panel{position:relative;max-width:720px;margin:8vh auto 0;max-height:80vh;overflow:auto;',
            '  background:var(--color-canvas-default,#fff);border:1px solid var(--color-border-default,#d0d7de);',
            '  border-radius:12px;box-shadow:0 16px 48px rgba(1,4,9,.3);padding:12px 16px;}',
            '#pf-panel .pagefind-ui{margin:0;}',
            '.pagefind-ui .pagefind-ui__search-input{font-family:inherit;}',
            // 暗色：Pagefind UI 自带浅色变量，按 GitHub Dark 覆写
            '[data-color-mode="dark"] .pagefind-ui{--pagefind-ui-text:#e6edf3;--pagefind-ui-background:#161b22;',
            '  --pagefind-ui-border:#30363d;--pagefind-ui-primary:#58a6ff;--pagefind-ui-tag:#21262d;}',
            '[data-color-mode="dark"] .pagefind-ui mark{background:rgba(56,139,253,.4);color:#e6edf3;}',
            '@media (max-width:600px){#pf-panel{margin:0;max-height:100vh;border-radius:0;border:0;}}'
        ].join('\n');
        document.head.appendChild(style);
    }

    function buildModal() {
        var modal = document.createElement('div');
        modal.id = 'pf-modal';
        modal.innerHTML = '<div id="pf-backdrop"></div>' +
            '<div id="pf-panel" role="dialog" aria-modal="true" aria-label="站内搜索"><div id="pf-search"></div></div>';
        document.body.appendChild(modal);
        modal.querySelector('#pf-backdrop').addEventListener('click', closeSearch);
        return modal;
    }

    function addEntryButton() {
        var bar = document.querySelector('#header .title-right');
        if (!bar || bar.querySelector('#pfButton')) return;
        var btn = document.createElement('a');
        btn.id = 'pfButton';
        btn.className = 'btn btn-invisible circle';
        btn.title = '搜索';
        btn.href = '#';
        btn.innerHTML = '<svg class="octicon" width="16" height="16"><path fill-rule="evenodd"></path></svg>';
        btn.querySelector('path').setAttribute('d', SEARCH_ICON);
        btn.addEventListener('click', function (e) { e.preventDefault(); openSearch(); });
        bar.insertBefore(btn, bar.firstChild);
    }

    function bindExistingSearch() {
        var old = document.getElementById('buttonSearch'); // 列表页原标签页搜索入口
        if (old) {
            old.addEventListener('click', function (e) { e.preventDefault(); openSearch(); });
            return true;
        }
        return false;
    }

    var loading = null;
    function loadAssets() {
        if (window.PagefindUI) return Promise.resolve();
        if (loading) return loading;
        loading = new Promise(function (resolve, reject) {
            var css = document.createElement('link');
            css.rel = 'stylesheet';
            css.href = '/pagefind/pagefind-ui.css';
            document.head.appendChild(css);
            var js = document.createElement('script');
            js.src = '/pagefind/pagefind-ui.js';
            js.onload = resolve;
            js.onerror = function () { loading = null; reject(new Error('Pagefind UI 加载失败')); };
            document.head.appendChild(js);
        });
        return loading;
    }

    var inited = false, modal;
    function openSearch() {
        var t = document.activeElement;
        if (t && /^(A|BUTTON)$/.test(t.tagName)) lastTrigger = t;
        loadAssets().then(function () {
            if (!inited) {
                new PagefindUI({
                    element: '#pf-search',
                    showSubResults: true,
                    excerptLength: 22,
                    translations: {
                        placeholder: '搜索文章…',
                        clear_search: '清空',
                        load_more: '加载更多结果',
                        search_label: '站内搜索',
                        zero_results: '找不到和 “[SEARCH_TERM]” 相关的文章',
                        many_results: '找到 [COUNT] 篇和 “[SEARCH_TERM]” 相关的文章',
                        one_result: '找到 [COUNT] 篇和 “[SEARCH_TERM]” 相关的文章',
                        total_zero_results: '无结果',
                        total_one_result: '[COUNT] 篇结果',
                        total_many_results: '[COUNT] 篇结果',
                        alt_search: '找不到和 “[SEARCH_TERM]” 相关的文章。改为显示 “[DIFFERENT_TERM]” 的结果',
                        search_suggestion: '找不到和 “[SEARCH_TERM]” 相关的文章。请尝试以下搜索。',
                        searching: '正在搜索 “[SEARCH_TERM]”…',
                        results_label: '搜索结果',
                        keyboard_navigate: '导航',
                        keyboard_select: '选择',
                        keyboard_clear: '清空',
                        keyboard_close: '关闭',
                        keyboard_search: '搜索',
                        error_search: '搜索失败',
                        filter_selected_one: '已选择 [COUNT] 个',
                        filter_selected_many: '已选择 [COUNT] 个',
                        input_hint: '输入时将显示结果',
                        loading: '加载中'
                    }
                });
                inited = true;
            }
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
            var input = modal.querySelector('.pagefind-ui__search-input');
            if (input) { input.focus(); input.select(); }
        }).catch(function (e) {
            console.error(e);
            alert('搜索资源加载失败，请稍后再试');
        });
    }

    var lastTrigger = null;
    function closeSearch() {
        modal.classList.remove('open');
        document.body.style.overflow = '';
        if (lastTrigger) { lastTrigger.focus(); lastTrigger = null; }
    }

    document.addEventListener('DOMContentLoaded', function () {
        injectStyle();
        modal = buildModal();
        if (!bindExistingSearch()) addEntryButton();
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeSearch();
            if (e.key === '/' && !/^(INPUT|TEXTAREA|IFRAME)$/.test(document.activeElement.tagName)) {
                e.preventDefault();
                openSearch();
            }
        });
    });
})();
