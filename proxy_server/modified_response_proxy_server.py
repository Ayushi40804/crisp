import socket
import threading

def modify_request(request):
    # Example modification: Change User-Agent header
    modified_request = request.replace("User-Agent: Mozilla", "User-Agent: BurpClone")
    return modified_request

def modify_response(response):
    # Example: Modify the response content
    if "origin" in response:
        response = response.replace("103.106.200.60", "127.0.0.1")  # Modify IP for testing purposes
    return response

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
    
    # Modify the request before forwarding
    modified_request = modify_request(request.decode('utf-8'))
    host, port = extract_host_port_from_request(modified_request)
    
    # Forward the modified request to the destination
    destination_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destination_socket.connect((host, port))
    destination_socket.sendall(modified_request.encode('utf-8'))
    print("Request forwarded to the destination")
    
    while True:
        response = destination_socket.recv(1024)
        if not response:
            break
        # Modify the response before sending it to the client
        modified_response = modify_response(response.decode('utf-8'))
        client_socket.sendall(modified_response.encode('utf-8'))
    
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
