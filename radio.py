import os
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

def get_songs():
    return [
        os.path.join(MUSIC_FOLDER, f)
        for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith(".mp3")
    ]

class RadioStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        
        while True:
            songs = get_songs()
            if not songs:
                time.sleep(2)
                continue
            current_song = random.choice(songs)
            try:
                with open(current_song, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
            except Exception:
                break

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), RadioStreamHandler)
    print(f"Radio streaming server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
