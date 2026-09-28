import os
import random
import subprocess

MUSIC_FOLDER = os.path.expanduser("~/Documents/RadioServer/Music")
ICECAST_URL = "icecast://source:akashdas%408906@127.0.0.1:8000/radio"

songs = [
    os.path.join(MUSIC_FOLDER, file)
    for file in os.listdir(MUSIC_FOLDER)
    if file.lower().endswith(".mp3")
]

if not songs:
    print("Music folder mein koi MP3 nahi mila.")
    exit()

print("================================")
print("      RADIO SERVER STARTED")
print("================================")
print(f"Songs found: {len(songs)}")
print()

last_song = None

while True:
    available_songs = [song for song in songs if song != last_song]
    current_song = random.choice(available_songs)
    song_name = os.path.basename(current_song)

    print(f"Now Playing: {song_name}")

    command = [
        "ffmpeg",
        "-re",
        "-i", current_song,
        "-c:a", "libmp3lame",
        "-b:a", "128k",
        "-content_type", "audio/mpeg",
        "-f", "mp3",
        ICECAST_URL
    ]

    try:
        subprocess.run(command)
    except KeyboardInterrupt:
        print("\nRadio stopped.")
        break

    last_song = current_song
