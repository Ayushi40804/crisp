import socket
import threading

def handle_client_request(client_socket):
    print("Received request:")
    request = b''
    client_socket.setblocking(False)
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            request += data
            print(data.decode('utf-8'), end='')
        except BlockingIOError:
            break

    host, port = extract_host_port_from_request(request.decode('utf-8'))
    destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destination_socket.connect((host, port))
    destination_socket.sendall(request)
    print("Request forwarded to the destination")

    while True:
        response = destination_socket.recv(1024)
        if not response:
            break
        print(response.decode('utf-8'), end='')
        client_socket.send(response)

    destination_socket.close()
    client_socket.close()

def extract_host_port_from_request(request):
    host_string_start = request.find('Host: ') + len('Host: ')
    host_string_end = request.find('\r\n', host_string_start)
    host_string = request[host_string_start:host_string_end]
    port = 80
    if ':' in host_string:
        host, port = host_string.split(':')
        port = int(port)
    else:
        host = host_string
    return host, port

def start_proxy_server(port=8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    print(f"Proxy server running on port {port}")

    while True:
        client_socket, client_address = server.accept()
        print(f"Accepted connection from {client_address}")
        client_handler = threading.Thread(target=handle_client_request, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_proxy_server()