import os
import random
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# Global Live Broadcast Engine
clients = []
clients_lock = threading.Lock()

def get_song_list():
    try:
        return [
            os.path.join(MUSIC_FOLDER, f)
            for f in os.listdir(MUSIC_FOLDER)
            if f.lower().endswith(".mp3")
        ]
    except Exception:
        return []

def continuous_broadcaster():
    recent_history = []
    
    while True:
        songs = get_song_list()
        if not songs:
            time.sleep(2)
            continue

        available = [s for s in songs if s not in recent_history]
        if not available:
            recent_history.clear()
            available = songs

        random.shuffle(available)
        song_path = available.pop(0)

        recent_history.append(song_path)
        if len(recent_history) > max(1, len(songs) // 2):
            recent_history.pop(0)

        try:
            with open(song_path, 'rb') as f:
                # 128kbps standard stream: 16000 bytes per second (~1600 bytes har 0.1s)
                chunk_size = 3200
                delay = 0.2
                
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    
                    with clients_lock:
                        dead_clients = []
                        for client_wfile in clients:
                            try:
                                client_wfile.write(data)
                                client_wfile.flush()
                            except Exception:
                                dead_clients.append(client_wfile)
                        for d in dead_clients:
                            clients.remove(d)
                            
                    time.sleep(delay)
        except Exception:
            time.sleep(1)

threading.Thread(target=continuous_broadcaster, daemon=True).start()

class RadioStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            return

        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Connection', 'close')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()

        with clients_lock:
            clients.append(self.wfile)

        # Jab tak user sun raha hai connection zinda rakho
        try:
            while True:
                time.sleep(5)
        except Exception:
            pass
        finally:
            with clients_lock:
                if self.wfile in clients:
                    clients.remove(self.wfile)

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = ThreadingHTTPServer(("0.0.0.0", port), RadioStreamHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
