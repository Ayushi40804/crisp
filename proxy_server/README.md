# Python Proxy Server

This project implements a simple proxy server that listens on port 8080 and forwards incoming requests to the appropriate destination, returning the responses to the clients. The server also allows modification of HTTP requests and responses before they are forwarded.

## Requirements

- Python 3.x

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd python-proxy-server
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the proxy server, execute the following command:

```
python src/proxy.py
```

The server will start listening on `http://localhost:8080`.

now open another python environment and run the following command to test the proxy server:

```
Invoke-WebRequest -Uri "http:/example.com" -Proxy "http://127.0.0.1:8080"
```