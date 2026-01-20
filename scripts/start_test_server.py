#!/usr/bin/env python3
"""
简单的 HTTP 服务器，用于提供测试聊天页面
"""

import http.server
import socketserver
import os

# 配置
PORT = 8888
DIRECTORY = '/workspace/projects/assets'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # 添加 CORS 头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 测试聊天服务器已启动！")
        print(f"📝 访问地址: http://localhost:{PORT}/test_chat.html")
        print(f"🔄 按 Ctrl+C 停止服务器")
        print("-" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✅ 服务器已停止")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
