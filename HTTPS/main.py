from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from proxy import ProxyServer
from database.db_manager import Database
import threading
import requests as http_requests
import json
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app)
db = Database('requests.db')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/requests')
def get_requests():
    requests = db.get_all_requests()
    return jsonify(requests)

@app.route('/modify_request', methods=['POST'])
#modify not workign rn
def modify_request():
    data = request.form
    for key, value in data.items():
        if key.startswith('request_'):
            request_id = key.split('_')[1]
            modified_body = value
            db.update_request(request_id, modified_headers=None, modified_body=modified_body)
            original_request = db.get_request(request_id)
            url = original_request['url']
            headers = json.loads(original_request['headers'])
            response = http_requests.post(url, headers=headers, data=modified_body)
            db.update_response(request_id, response.text)
    return jsonify({'status': 'success'})

def start_proxy_server():
    proxy = ProxyServer('localhost', 8888, 'requests.db')
    proxy.start()

if __name__ == '__main__':
    proxy_thread = threading.Thread(target=start_proxy_server)
    proxy_thread.daemon = True
    proxy_thread.start()
    socketio.run(app, debug=True, port=5000)