import cv2
import simpleaudio as sa
import wave
import os
import time
import random
from tkinter import *
from tkinter.ttk import Progressbar

# Set the directory where your audio files are stored
audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookclips")

# GUI setup
root = Tk()
root.geometry("400x300")

# Track current audio file
current_file = None

# Track file duration and position
duration = 0
start_time = 0

# Track previous files played
previous_files = []

# Define play and stop audio functions
def play_audio(file_path, manual=False):
    global current_file, duration, start_time

    # Stop previous audio if playing
    stop_audio()

    # Load new audio file
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()

    # Update current file
    current_file = file_path

    # Update duration
    duration = get_wave_duration(file_path)

    # Update progress bar and labels during playback
    start_time = time.time()
    while play_obj.is_playing():
        elapsed = time.time() - start_time
        if duration > 0:
            progress.configure(value=elapsed / duration * 100)
        elapsed_var.set(format_time(elapsed))
        remaining_var.set(format_time(duration - elapsed))
        root.update()

    progress.configure(value=0)
    elapsed_var.set("")
    remaining_var.set("")

    if not manual:
        now_playing_label.config(text="Now playing: nothing")

def stop_audio():
    global current_file, duration, start_time

    if current_file is not None:
        sa.stop_all()
        current_file = None
        duration = 0
        start_time = 0

def handle_code(data):
    file_path = os.path.join(audio_dir, f"{data.lower().replace('.wav', '')}.wav")
    if not os.path.isfile(file_path):
        status_label.config(text=f"Code does not match audio file: {data}")
        return

    if data not in previous_files:
        if len(previous_files) >= 2:
            previous_files.pop(0)
        previous_files.append(data)
        previous_files_label.config(text=f"Previously played: {', '.join(previous_files)}")

    play_audio(file_path)
    status_label.config(text=f"Now playing: {data}")

def handle_idle():
    idle_files = os.listdir(audio_dir)
    idle_file = random.choice(idle_files)
    play_audio(os.path.join(audio_dir, idle_file))
    status_label.config(text=f"Now playing idle audio: {idle_file}")

def button_click(file_path):
    stop_audio()
    play_audio(file_path, manual=True)
    file_name = os.path.basename(file_path)
    status_label.config(text=f"Manually playing: {file_name}")
    previous_files_label.config(text="Previously played: none")

# Format time in MM:SS format
def format_time(seconds):
    if seconds < 0:
        seconds = 0
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

# Update progress bar and labels periodically
def update_progress():
    global current_file, duration, start_time

    if current_file is not None:
        elapsed = time.time() - start_time
        elapsed_var.set(format_time(elapsed))
        remaining_var.set(format_time(duration - elapsed))
        if duration > 0:
            progress.configure(value=elapsed / duration * 100)
        else:
            elapsed_var.set("")
            remaining_var.set("")
            progress.configure(value=0)

    root.after(500, update_progress)

# Get duration of wave file
def get_wave_duration(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    return duration

# Set up camera object
cap = cv2.VideoCapture(1)  # Select webcam 1

# Set up QRCodeDetector
qcd = cv2.QRCodeDetector()

# Create play buttons for each audio file
audio_files = os.listdir(audio_dir)
for audio_file in audio_files:
    file_path = os.path.join(audio_dir, audio_file)
    button = Button(root, text=audio_file, command=lambda file_path=file_path: button_click(file_path))
    button.pack()

# Progress bar and time labels
progress_frame = Frame(root)
progress_frame.pack()

progress = Progressbar(progress_frame, length=200, mode='determinate')
progress.pack(side=LEFT)

time_labels_frame = Frame(progress_frame)
time_labels_frame.pack(side=LEFT, padx=10)

elapsed_var = StringVar()
elapsed_var.set("")
elapsed_label = Label(time_labels_frame, textvariable=elapsed_var)
elapsed_label.pack()

remaining_var = StringVar()
remaining_var.set("")
remaining_label = Label(time_labels_frame, textvariable=remaining_var)
remaining_label.pack()

# Now playing label
now_playing_label = Label(root, text="Now playing: nothing")
now_playing_label.pack()

# Previous files label
previous_files_label = Label(root, text="Previously played: none")
previous_files_label.pack()

# Status label
status_label = Label(root, text="Error: none")
status_label.pack()

# Initialize progress update
update_progress()

while True:
    _, frame = cap.read()

    cv2.imshow("Video Preview", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    ret_qr, decoded_info, _, _ = qcd.detectAndDecodeMulti(frame)
    if ret_qr:
        for info in decoded_info:
            data = info.lower().replace('.wav', '')
            handle_code(data)

    root.update()

cap.release()
cv2.destroyAllWindows()