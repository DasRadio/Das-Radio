import os
import random
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# Global buffer sabhi listeners ke liye live stream sync rakhne ke liye
stream_buffer = bytearray()
buffer_lock = threading.Lock()

def global_radio_broadcaster():
    global stream_buffer
    played_history = []
    
    while True:
        try:
            songs = [
                os.path.join(MUSIC_FOLDER, f)
                for f in os.listdir(MUSIC_FOLDER)
                if f.lower().endswith(".mp3")
            ]
            
            if not songs:
                time.sleep(2)
                continue
            
            # Random shuffle aur recent gano ko repeat hone se rokne ke liye logic
            available = [s for s in songs if s not in played_history]
            if not available:
                played_history.clear()
                available = songs
            
            random.shuffle(available)
            current_song = available.pop(0)
            
            played_history.append(current_song)
            if len(played_history) > max(1, len(songs) // 2):
                played_history.pop(0)
            
            print(f"Broadcasting: {os.path.basename(current_song)}")
            
            with open(current_song, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    with buffer_lock:
                        stream_buffer.extend(chunk)
                        # Buffer size control mein rakhne ke liye purana data hata dein
                        if len(stream_buffer) > 262144:
                            del stream_buffer[:4096]
                    # Real-time smooth streaming ke liye pacing
                    time.sleep(0.012)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

# Background mein live radio thread chalu kar dein
threading.Thread(target=global_radio_broadcaster, daemon=True).start()

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
        
        with buffer_lock:
            sent_index = max(0, len(stream_buffer) - 32768)
        
        try:
            while True:
                with buffer_lock:
                    current_len = len(stream_buffer)
                    if current_len > sent_index:
                        data = bytes(stream_buffer[sent_index:current_len])
                        sent_index = current_len
                    else:
                        data = b""
                
                if data:
                    self.wfile.write(data)
                    self.wfile.flush()
                else:
                    time.sleep(0.05)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            return

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = ThreadingHTTPServer(("0.0.0.0", port), RadioStreamHandler)
    print(f"Global Live Radio server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
