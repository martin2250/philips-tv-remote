#!/usr/bin/env python3
import http.server
import os
import socketserver
import urllib.request

TV_IP = os.environ.get("TV_IP", "192.168.2.134")
TV_PORT = int(os.environ.get("TV_PORT", 1925))
PROXY_IP = os.environ.get("PROXY_IP", "0.0.0.0")
PROXY_PORT = int(os.environ.get("PROXY_PORT", 8081))


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/tv/"):
            self.proxy_request("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/tv/"):
            self.proxy_request("POST")
        else:
            self.send_error(405, "Method not allowed")

    def proxy_request(self, method):
        # Strip /tv prefix
        target_path = self.path[len("/tv") :]
        target_url = f"http://{TV_IP}:{TV_PORT}{target_path}"

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else None

        # Build request
        req = urllib.request.Request(target_url, data=body, method=method)
        for key, value in self.headers.items():
            # Filter out headers that could break the proxy
            if key.lower() not in ("host", "origin", "referer", "content-length"):
                req.add_header(key, value)
        if body:
            req.add_header("Content-Length", str(len(body)))

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                self.send_response(response.status)
                for header, value in response.getheaders():
                    if header.lower() == "transfer-encoding":
                        continue  # skip chunked encoding
                    self.send_header(header, value)
                # Add CORS header so browser allows it
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                data = response.read()
                self.wfile.write(data)
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")


if __name__ == "__main__":
    with socketserver.TCPServer((PROXY_IP, PROXY_PORT), ProxyHandler) as httpd:
        print(f"Serving on http://{PROXY_IP}:{PROXY_PORT}")
        print(f"Proxying /tv/* → http://{TV_IP}:{TV_PORT}/")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
