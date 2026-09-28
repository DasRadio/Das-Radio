import os
import random
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

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
        self.send_header('Accept-Ranges', 'none')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        
        try:
            songs = [
                os.path.join(MUSIC_FOLDER, f)
                for f in os.listdir(MUSIC_FOLDER)
                if f.lower().endswith(".mp3")
            ]
            if not songs:
                return
            
            while True:
                random.shuffle(songs)
                for song in songs:
                    try:
                        with open(song, 'rb') as f:
                            while True:
                                chunk = f.read(16384)
                                if not chunk:
                                    break
                                self.wfile.write(chunk)
                                self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError):
                        return
                    except Exception:
                        break
        except Exception:
            return

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = ThreadingHTTPServer(("0.0.0.0", port), RadioStreamHandler)
    print(f"Radio server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
