# -*- coding: utf-8 -*-
"""启动本地静态服务器，让课程站点能被正常浏览（相对链接全部生效）。

为什么需要它：内置预览面板会把每个目录映射成 /static-html/<hash>/，
只在同一目录内解析路径——所以讲义、课件、题库这类跨目录的 ../ 链接会 404。
用真正的 HTTP 服务器打开则一切正常。

用法：
  python tools/serve.py            # 默认 127.0.0.1:8090
  python tools/serve.py 9000       # 指定端口
"""
import http.server
import os
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, *a):
        pass          # 安静模式

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    with Server(("127.0.0.1", PORT), Handler) as httpd:
        print(f"课程站点已启动： http://127.0.0.1:{PORT}/index.html", flush=True)
        print(f"根目录： {ROOT}", flush=True)
        httpd.serve_forever()
