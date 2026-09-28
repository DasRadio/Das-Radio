import os
import random
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# ==============================
# SETTINGS
# ==============================

MUSIC_FOLDER = os.path.join(os.path.dirname(__file__), "Music")
PORT = int(os.environ.get("PORT", 10000))

# Live stream buffer
STREAM_BUFFER_SIZE = 512 * 1024  # 512 KB

# ==============================
# MUSIC FOLDER
# ==============================

if not os.path.exists(MUSIC_FOLDER):
    os.makedirs(MUSIC_FOLDER)

# ==============================
# GLOBAL STREAM DATA
# ==============================

current_stream_data = bytearray()
buffer_lock = threading.Lock()


# ==============================
# RADIO BROADCASTER
# ==============================

def global_radio_broadcaster():

    global current_stream_data

    played_history = []

    while True:

        try:

            # Find all MP3 files
            songs = [
                os.path.join(MUSIC_FOLDER, filename)
                for filename in os.listdir(MUSIC_FOLDER)
                if filename.lower().endswith(".mp3")
            ]

            if not songs:
                print("Music folder mein koi MP3 nahi mila.")
                time.sleep(3)
                continue

            # Recent songs ko immediately repeat na kare
            available = [
                song for song in songs
                if song not in played_history
            ]

            if not available:
                played_history.clear()
                available = songs.copy()

            # Random song
            current_song = random.choice(available)

            played_history.append(current_song)

            # Recent history limit
            history_limit = max(1, len(songs) // 2)

            while len(played_history) > history_limit:
                played_history.pop(0)

            print("--------------------------------")
            print("Now Playing:", os.path.basename(current_song))
            print("--------------------------------")

            # --------------------------------
            # READ SONG
            # --------------------------------

            with open(current_song, "rb") as audio_file:

                while True:

                    chunk = audio_file.read(4096)

                    if not chunk:
                        break

                    with buffer_lock:

                        current_stream_data.extend(chunk)

                        # Buffer ko controlled size mein rakho
                        if len(current_stream_data) > STREAM_BUFFER_SIZE:

                            remove_bytes = (
                                len(current_stream_data)
                                - STREAM_BUFFER_SIZE
                            )

                            del current_stream_data[:remove_bytes]

                    # 128 kbps ke aas-paas pacing
                    #
                    # 128 kbps = 16 KB/sec
                    # 4096 bytes / 16384 bytes/sec
                    # ≈ 0.25 sec
                    #
                    time.sleep(0.25)

        except Exception as error:

            print("Radio Error:", error)

            time.sleep(2)


# ==============================
# START BROADCAST THREAD
# ==============================

radio_thread = threading.Thread(
    target=global_radio_broadcaster,
    daemon=True
)

radio_thread.start()


# ==============================
# HTTP STREAM SERVER
# ==============================

class RadioStreamHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # ------------------------------
        # HEALTH CHECK
        # ------------------------------

        if self.path == "/health":

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/plain"
            )

            self.send_header(
                "Cache-Control",
                "no-cache"
            )

            self.end_headers()

            self.wfile.write(b"OK")

            return

        # ------------------------------
        # AUDIO STREAM
        # ------------------------------

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "audio/mpeg"
        )

        self.send_header(
            "Cache-Control",
            "no-cache, no-store, must-revalidate"
        )

        self.send_header(
            "Pragma",
            "no-cache"
        )

        self.send_header(
            "Expires",
            "0"
        )

        self.send_header(
            "Accept-Ranges",
            "none"
        )

        self.send_header(
            "Connection",
            "keep-alive"
        )

        self.end_headers()

        # --------------------------------
        # Start position
        # --------------------------------
        #
        # Listener ko current live position
        # ke aas-paas se start karna hai.
        #

        with buffer_lock:

            sent_index = len(current_stream_data)

        try:

            while True:

                with buffer_lock:

                    current_len = len(current_stream_data)

                    # Agar broadcaster ne purana data delete
                    # kar diya hai to index adjust karo.
                    if sent_index > current_len:

                        sent_index = current_len

                    if current_len > sent_index:

                        data = bytes(
                            current_stream_data[
                                sent_index:current_len
                            ]
                        )

                        sent_index = current_len

                    else:

                        data = b""

                # ------------------------------
                # Send audio
                # ------------------------------

                if data:

                    self.wfile.write(data)
                    self.wfile.flush()

                else:

                    # New audio ka wait
                    time.sleep(0.05)

        except (
            BrokenPipeError,
            ConnectionResetError,
            ConnectionAbortedError
        ):

            return

        except Exception as error:

            print("Client disconnected:", error)

            return

    # Disable HTTP request logs
    def log_message(self, format, *args):

        return


# ==============================
# START SERVER
# ==============================

def run_server():

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        RadioStreamHandler
    )

    print("================================")
    print("      GLOBAL RADIO SERVER")
    print("================================")
    print("Port:", PORT)
    print("Stream: http://0.0.0.0:" + str(PORT))
    print("================================")

    server.serve_forever()


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    run_server()
