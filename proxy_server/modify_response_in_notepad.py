import socket
import threading
import tempfile
import os
import subprocess

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

    # Receiving the response
    response = b""
    while True:
        data = destination_socket.recv(1024)
        if not data:
            break
        response += data
        print(f"Original response: {data.decode('utf-8')}", end='')

    # Save response to a temporary file and open it in an editor (Notepad)
    with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file.write(response.decode('utf-8'))
        temp_filename = temp_file.name
        print(f"Response saved to {temp_filename}")

    # Open the file in Notepad for user editing
    subprocess.run(['notepad.exe', temp_filename])

    # Read the modified response from the file
    with open(temp_filename, 'r', encoding='utf-8') as temp_file:
        modified_response = temp_file.read()

    # Forward the modified response to the client
    print(f"Modified response: {modified_response}")
    client_socket.sendall(modified_response.encode('utf-8'))

    # Clean up the temporary file
    os.remove(temp_filename)

    destination_socket.close()
    client_socket.close()

def modify_request(request):
    # Modify the request (e.g., change headers)
    modified_request = request.replace("User-Agent: Mozilla", "User-Agent: BurpClone")
    return modified_request

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
