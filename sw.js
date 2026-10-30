/* Python 学习课程包 · Service Worker
 *
 * 缓存策略：
 *   - HTML 导航请求：network-first，失败回退缓存（保证内容新鲜）
 *   - 静态资源（css/js/webp/png）：cache-first，未命中走网络并入库（保证离线可用）
 *   - 安装时预缓存「核心 shell」（入口页 + 公共 CSS + 搜索索引 + 图标），
 *    课件 webp 体积大（约 10MB），按访问惰性入库，不拖慢首次安装
 *
 * 注意：
 *   - 仅在 http(s) 下注册生效；file:// 直接打开便携版时注册会失败，属预期行为
 *   - 站点内容更新后必须升 V（缓存名），否则老用户拿不到新静态资源
 */
var V = 'pycourse-v42';

var SHELL = [
  './',
  './index.html',
  './python-course-syllabus.html',
  './python-learning-roadmap.html',
  './web/lessons/index.html',
  './web/lessons/lessons.css',
  './web/css/unit.css',
  './web/site.js',
  './web/searchdata.js',
  './web/review.html',
  './web/terms.html',
  './web/coverage.html',
  './web/plan.html',
  './web/bank.html',
  './web/bank-ans.js',
  './fluent/index.html',
  './fluent/web/css/site.css',
  './fluent/web/lessons/index.html',
  './fluent/web/ppt/u/index.html',
  './fluent/web/coverage.html',
  './fluent/web/terms.html',
  './fluent/web/review.html',
  './fluent/web/bench.html',
  './fluent/web/syllabus.html',
  './fluent/web/ch/index.html',
  './fluent/web/walk/index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-192.png',
  './icon-maskable-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(V).then(function (c) {
      // 逐个入库，单个失败不拖垮整个安装
      return Promise.all(SHELL.map(function (u) {
        return c.add(u).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k.indexOf(V) !== 0) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;

  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(function (res) {
        var cp = res.clone();
        caches.open(V).then(function (c) { c.put(req, cp); });
        return res;
      }).catch(function () {
        return caches.match(req).then(function (hit) {
          if (hit) return hit;
          // 进阶课页面回退到进阶课首页，别把用户丢回入门课
          var fallback = url.pathname.indexOf('/fluent/') >= 0
            ? './fluent/index.html' : './index.html';
          return caches.match(fallback);
        });
      })
    );
    return;
  }

  e.respondWith(
    caches.match(req).then(function (hit) {
      if (hit) return hit;
      return fetch(req).then(function (res) {
        if (res && res.ok && res.type === 'basic') {
          var cp = res.clone();
          caches.open(V).then(function (c) { c.put(req, cp); });
        }
        return res;
      });
    })
  );
});
