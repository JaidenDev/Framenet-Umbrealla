import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion, QTYPE, RR, A
from http.server import BaseHTTPRequestHandler, HTTPServer
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Thread
import signal
import sys
import os
import json

BLOCK_LIST_FILE = "block_list.config"
DNS_PORT = 53
HTTP_PORT = 80
MAX_WORKERS = 10

SERVER_IP = "127.0.0.0"

stop_event = Event()

def load_block_list():
    block_dict = {}
    try:
        with open(BLOCK_LIST_FILE, 'r') as f:
            block_dict = json.load(f)  
    except FileNotFoundError:
        print(f"Block list file {BLOCK_LIST_FILE} not found. Using an empty list.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {BLOCK_LIST_FILE}. Please check the format.")
    return block_dict

block_list = load_block_list()

def dns_handler(data, addr, sock):
    try:
        request = DNSRecord.parse(data)
        qname = str(request.q.qname).rstrip('.')

        if qname in block_list:
            print(f"Blocked request: {qname}")
            response = DNSRecord(
                DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
                q=request.q,
                a=RR(qname, QTYPE.A, rdata=A(SERVER_IP), ttl=60)
            )
            sock.sendto(response.pack(), addr)
        else:
            print(f"Forwarding request: {qname}")
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            proxy_sock.sendto(data, ('8.8.8.8', 53)) 
            proxy_response, _ = proxy_sock.recvfrom(512)
            sock.sendto(proxy_response, addr)
            proxy_sock.close()
    except Exception as e:
        print(f"Error handling request: {e}")

def start_dns_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", DNS_PORT))
        print(f"DNS server listening on port {DNS_PORT}...")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            while not stop_event.is_set():
                sock.settimeout(1)
                try:
                    data, addr = sock.recvfrom(512)
                    executor.submit(dns_handler, data, addr, sock)
                except socket.timeout:
                    continue
    except OSError as e:
        print(f"Error: {e}")
    finally:
        sock.close()

class BlockedPageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve logo image if requested
        if self.path == "/logo.png":
            self.serve_image("static/logo.png", "image/png")
            return
        elif self.path == "/favicon.ico":
            self.serve_image("static/logo.png", "image/x-icon")  # Favicon uses the same logo.png file
            return

        # Otherwise, serve the blocked page
        blocked_domain = self.headers.get("Host", "Unknown")
        block_reason = block_list.get(blocked_domain, "No reason provided.")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blocked</title>
            <link rel="icon" href="logo.png" type="image/x-icon">  <!-- Use logo.png as favicon -->
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin-top: 50px;
                }}
                .container {{
                    max-width: 800px;
                    margin: auto;
                }}
                .blocked {{
                    font-size: 24px;
                    color: red;
                    font-weight: bold;
                }}
                .reason {{
                    font-size: 18px;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 50px;
                    font-size: 12px;
                    color: #555;
                }}
                .footer a {{
                    color: #555;
                    text-decoration: none;
                }}
                .footer a:hover {{
                    text-decoration: underline;
                }}
                img.logo {{
                    width: 300px;  /* Increase the width to make the logo bigger */
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="logo.png" alt="Logo" class="logo">  <!-- Display logo.png as the image -->
                <div class="blocked">The domain "{blocked_domain}" is blocked.</div>
                <div class="reason">{block_reason}</div>
            </div>
            <div class="footer">
                <p>&copy;2025 Framenet Umbrella, By FinDev</p>
                <p><a href="http://jaiden.pro">Visit my site</a> | <a href="https://github.com/JaidenDev/Framenet-Umbrella">Visit the project</a></p>
            </div>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode())

    def serve_image(self, image_file, content_type):
        # Serve the image file requested
        if os.path.exists(image_file):
            with open(image_file, "rb") as f:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File Not Found")

def start_http_server():
    server = HTTPServer(('0.0.0.0', HTTP_PORT), BlockedPageHandler)
    print(f"HTTP server listening on port {HTTP_PORT}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

def signal_handler(sig, frame):
    print("\nShutting down server...")
    stop_event.set()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    Thread(target=start_dns_server, daemon=True).start()
    Thread(target=start_http_server, daemon=True).start()

    try:
        while not stop_event.is_set():
            pass
    except KeyboardInterrupt:
        signal_handler(None, None)
