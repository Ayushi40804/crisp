import sqlite3
import json

class Database:
    def __init__(self, db_path='requests.db'):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                method TEXT,
                url TEXT,
                headers TEXT,
                body TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER,
                response_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(request_id) REFERENCES requests(id)
            )
        ''')
        conn.commit()
        conn.close()

    def store_request(self, method, url, headers, body):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (method, url, headers, body)
            VALUES (?, ?, ?, ?)
        ''', (method, url, json.dumps(headers), body))
        conn.commit()
        request_id = cursor.lastrowid
        conn.close()
        return request_id

    def store_response(self, request_id, response_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO responses (request_id, response_data)
            VALUES (?, ?)
        ''', (request_id, response_data))
        conn.commit()
        conn.close()

    def get_all_requests(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT requests.*, responses.response_data 
            FROM requests 
            LEFT JOIN responses ON requests.id = responses.request_id
        ''')
        rows = cursor.fetchall()
        conn.close()

        result = []
        for row in rows:
            try:
                headers = json.loads(row[3]) if row[3] and row[3].strip() else {}
            except json.JSONDecodeError:
                headers = {} 

            result.append({
                'id': row[0],
                'method': row[1],
                'url': row[2],
                'headers': headers,
                'body': row[4],
                'timestamp': row[5],
                'response': row[6] if len(row) > 6 else None
            })
        return result

    def insert_request(self, client_ip, client_port, request_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (method, url, headers, body)
            VALUES (?, ?, ?, ?)
        ''', ('-', '-', '-', request_data))
        conn.commit()
        conn.close()

    def insert_data(self, client_ip, client_port, direction, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (method, url, headers, body)
            VALUES (?, ?, ?, ?)
        ''', (direction, f"{client_ip}:{client_port}", '-', data.decode('utf-8', 'ignore')))
        conn.commit()
        conn.close()

    def insert_http_data(self, client_ip, client_port, host, port, direction, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (method, url, headers, body)
            VALUES (?, ?, ?, ?)
        ''', (direction, f"http://{host}:{port}", '-', data.decode('utf-8', 'ignore')))
        conn.commit()
        conn.close()