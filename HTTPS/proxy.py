import socket
import ssl
import threading
import select
from urllib.parse import urlparse
from certificate_generator import CertificateGenerator
from database.db_manager import Database
import os

class ProxyServer:
    def __init__(self, host='localhost', port=8888, db_path='requests.db', certs_dir='certs'):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)
        self.db = Database(db_path)
        self.cert_gen = CertificateGenerator()
        self.certs_dir = certs_dir

        os.makedirs(self.certs_dir, exist_ok=True)

    def start(self):
        print(f"HTTPS Proxy listening on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Accepted connection from {address}")
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        try:
            request = client_socket.recv(4096).decode()
            print(f"Received request from {address}: {request}")
            self.db.insert_request(address[0], address[1], request)

            if request.startswith("CONNECT"):
                host, port = self.parse_connect_request(request)
                print(f"Connecting to {host}:{port}")
                certfile, keyfile = self.cert_gen.create_signed_cert(host, output_dir=self.certs_dir)

                client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                context.load_cert_chain(certfile=certfile, keyfile=keyfile)

                client_socket = context.wrap_socket(client_socket, server_side=True)
                target_socket = socket.create_connection((host, port))
                target_socket = ssl.wrap_socket(target_socket)

                self.forward_ssl_data(client_socket, target_socket, address)
            else:
                self.handle_http_request(client_socket, request, address)
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def parse_connect_request(self, request):
        lines = request.split('\r\n')
        connect_line = lines[0]
        _, target, _ = connect_line.split()
        host, port = target.split(':')
        return host, int(port)

    def handle_http_request(self, client_socket, request, address):
        try:
            url = urlparse(request.split(' ')[1])
            host = url.hostname
            port = url.port if url.port else 80
            target_socket = socket.create_connection((host, port))
            target_socket.sendall(request.encode())

            self.forward_http_data(client_socket, target_socket, address, host, port)
        except Exception as e:
            print(f"Error handling HTTP request from {address}: {e}")

    def forward_ssl_data(self, client_socket, target_socket, address):
        try:
            sockets = [client_socket, target_socket]
            while True:
                readable, _, _ = select.select(sockets, [], [])
                for s in readable:
                    data = s.recv(4096)
                    if not data:
                        return
                    if s is client_socket:
                        target_socket.sendall(data)
                    else:
                        client_socket.sendall(data)

                    direction = "client" if s is client_socket else "server"
                    self.db.insert_data(address[0], address[1], direction, data)
        except Exception as e:
            print(f"SSL forwarding error: {e}")

    def forward_http_data(self, client_socket, target_socket, address, host, port):
        try:
            sockets = [client_socket, target_socket]
            while True:
                readable, _, _ = select.select(sockets, [], [])
                for s in readable:
                    data = s.recv(4096)
                    if not data:
                        return
                    if s is client_socket:
                        target_socket.sendall(data)
                    else:
                        client_socket.sendall(data)

                    direction = "client" if s is client_socket else "server"
                    self.db.insert_http_data(address[0], address[1], host, port, direction, data)
        except Exception as e:
            print(f"HTTP forwarding error: {e}")