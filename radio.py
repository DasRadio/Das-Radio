import os
import random
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Render ke liye chhota HTTP server taaki port error na aaye
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Radio Server is Live!")

def start_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Background mein web server start kar rahe hain
threading.Thread(target=start_web_server, daemon=True).start()

# Music folder ka rasta
MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")

if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

songs = [
    os.path.join(MUSIC_FOLDER, file)
    for file in os.listdir(MUSIC_FOLDER)
    if file.lower().endswith(".mp3")
]

print("================================")
print("      RADIO SERVER STARTED")
print("================================")
print(f"Songs found: {len(songs)}")

while True:
    if not songs:
        # Agar gaane nahi milte toh thodi der wait karega
        import time
        time.sleep(5)
        songs = [
            os.path.join(MUSIC_FOLDER, file)
            for file in os.listdir(MUSIC_FOLDER)
            if file.lower().endswith(".mp3")
        ]
        continue

    current_song = random.choice(songs)
    song_name = os.path.basename(current_song)
    print(f"Now Playing: {song_name}")
    
    # Simulate playing loop for cloud stability
    import time
    time.sleep(10)
