import os
import random
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

def get_songs():
    try:
        return [
            os.path.join(MUSIC_FOLDER, f)
            for f in os.listdir(MUSIC_FOLDER)
            if f.lower().endswith(".mp3")
        ]
    except Exception:
        return []

class RadioStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Render health check
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # Live Radio Stream Headers (Seeking disable karne ke liye)
        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Accept-Ranges', 'none')  # Yeh browser ko aage-piche karne se rogega
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        
        try:
            while True:
                songs = get_songs()
                if not songs:
                    time.sleep(2)
                    continue
                
                current_song = random.choice(songs)
                try:
                    with open(current_song, 'rb') as f:
                        while True:
                            chunk = f.read(8192)
                            if not chunk:
                                break
                            self.wfile.write(chunk)
                            self.wfile.flush()
                except Exception:
                    break
        except Exception:
            return

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = ThreadingHTTPServer(("0.0.0.0", port), RadioStreamHandler)
    print(f"Radio stream server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
