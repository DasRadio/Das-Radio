import os
import random
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# Global Radio Stream State (Sabhi listeners ke liye ek hi live stream chalegi)
current_stream_data = bytearray()
current_song_name = ""
playlist_queue = []
played_recently = []

def update_global_stream():
    global current_stream_data, current_song_name, playlist_queue, played_recently
    
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
                
            # Agar queue khatam ho jaye, toh naya random shuffle banayein
            if not playlist_queue:
                available_songs = [s for s in songs if s not in played_recently]
                if not available_songs:
                    # Agar saare gaane baj chuke hain, toh history clear kar de taaki repeat ho sakein
                    played_recently.clear()
                    available_songs = songs
                
                random.shuffle(available_songs)
                playlist_queue = list(available_songs)
            
            song_path = playlist_queue.pop(0)
            
            # History track rakhein taaki 2 ghante tak wahi gana wapas na aaye
            played_recently.append(song_path)
            if len(played_recently) > max(1, len(songs) // 2):
                played_recently.pop(0)
                
            current_song_name = os.path.basename(song_path)
            print(f"Now Broadcasting: {current_song_name}")
            
            # Gaane ko chunk-by-chunk global stream mein read karein
            with open(song_path, 'rb') as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    
                    # Buffer ko control mein rakhein (sirf latest 64KB stream rakhein)
                    current_stream_data.extend(chunk)
                    if len(current_stream_data) > 65536:
                        del current_stream_data[:8192]
                        
                    time.sleep(0.05) # Real-time bitrate pacing
        except Exception as e:
            print(f"Stream error: {e}")
            time.sleep(2)

# Background mein live radio thread chalu kar dein
threading.Thread(target=update_global_stream, daemon=True).start()

class RadioStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")
            return

        # Live Radio Stream Headers
        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Accept-Ranges', 'none')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        
        # Jaise hi koi user connect karega, use wahi stream milegi jo us waqt live chal rahi hai
        try:
            last_idx = 0
            while True:
                if len(current_stream_data) > last_idx:
                    data_chunk = bytes(current_stream_data[last_idx:])
                    self.wfile.write(data_chunk)
                    self.wfile.flush()
                    last_idx = len(current_stream_data)
                else:
                    time.sleep(0.1)
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            return

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = ThreadingHTTPServer(("0.0.0.0", port), RadioStreamHandler)
    print(f"24/7 Global Live Radio server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
