import base64
import cv2
import numpy as np
import time
import pyttsx3
from flask import Flask, render_template
from flask_socketio import SocketIO
from blink_detector import BlinkProcessor
from utils import morse_letters_to_text

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Initialize blink processor
proc = BlinkProcessor()

# Buffers for Morse decoding
morse_buffer = ""   # collect '.' and '-'
decoded_text = ""   # final output text
last_blink_time = time.time()
morse_timeout = 2.0  # seconds of silence before auto-decoding a letter

# Speech engine (server-side)
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 160)
tts_engine.setProperty('volume', 1.0)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('frame')
def handle_frame(data):
    """Receive frame, process blink, and update live preview."""
    global morse_buffer, decoded_text, last_blink_time

    try:
        _, b64 = data.split(',', 1)
        frame_bytes = base64.b64decode(b64)
        arr = np.frombuffer(frame_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        return

    ev = proc.process_frame(img)
    if not ev:
        # Check timeout (auto end of one Morse letter)
        current_time = time.time()
        if current_time - last_blink_time > morse_timeout and morse_buffer:
            try:
                letter = morse_letters_to_text([[morse_buffer]])
                if letter and letter != '?':
                    decoded_text += letter
                    socketio.emit('live', {'action': 'auto_letter_end', 'preview': decoded_text, 'letter': letter})
                    socketio.emit('decoded', {'text': decoded_text})
                morse_buffer = ""
            except Exception as e:
                print(f"Error decoding morse: {e}")
                morse_buffer = ""
        return

    action = ev['type']
    last_blink_time = time.time()

    # === Morse & text actions ===
    if action == 'dot':
        morse_buffer += '.'
        socketio.emit('live', {'action': 'dot', 'preview': decoded_text + morse_buffer, 'buffer': morse_buffer})
        
    elif action == 'dash':
        morse_buffer += '-'
        socketio.emit('live', {'action': 'dash', 'preview': decoded_text + morse_buffer, 'buffer': morse_buffer})
        
    elif action == 'morse_backspace':
        # Delete last dot/dash from morse buffer
        if morse_buffer:
            morse_buffer = morse_buffer[:-1]
            socketio.emit('live', {'action': 'morse_backspace', 'preview': decoded_text + morse_buffer, 'buffer': morse_buffer})
            socketio.emit('decoded', {'text': decoded_text})
        else:
            socketio.emit('live', {'action': 'morse_backspace_fail', 'preview': decoded_text, 'buffer': ''})
            
    elif action == 'letter_backspace':
        # Delete last decoded letter from final text
        if decoded_text:
            decoded_text = decoded_text[:-1]
            socketio.emit('live', {'action': 'letter_backspace', 'preview': decoded_text, 'buffer': morse_buffer})
            socketio.emit('decoded', {'text': decoded_text})
        else:
            socketio.emit('live', {'action': 'letter_backspace_fail', 'preview': '', 'buffer': morse_buffer})
            
    elif action == 'space':
        # space = end of word (finalize current letter and add space)
        if morse_buffer:
            try:
                letter = morse_letters_to_text([[morse_buffer]])
                if letter and letter != '?':
                    decoded_text += letter + " "
                morse_buffer = ""
            except Exception:
                morse_buffer = ""
        else:
            # Just add space if no morse buffer
            decoded_text += " "
        socketio.emit('decoded', {'text': decoded_text})
        socketio.emit('live', {'action': 'space', 'preview': decoded_text, 'buffer': ''})
        
    elif action == 'enter':
        # Finalize current letter if any, then speak and reset
        if morse_buffer:
            try:
                letter = morse_letters_to_text([[morse_buffer]])
                if letter and letter != '?':
                    decoded_text += letter
                morse_buffer = ""
            except Exception:
                morse_buffer = ""

        if decoded_text.strip():
            print("🗣 Final Text:", decoded_text)
            # Emit text for client-side TTS (more reliable than server-side)
            socketio.emit('speak', {'text': decoded_text})
            # Also try server-side TTS as backup (non-blocking)
            try:
                tts_engine.say(decoded_text)
                tts_engine.runAndWait()
            except Exception as e:
                print(f"Server TTS error: {e}")

        socketio.emit('decoded', {'text': decoded_text})
        socketio.emit('live', {'action': 'enter', 'preview': decoded_text, 'buffer': ''})
        decoded_text = ""
        morse_buffer = ""

    # === Live preview update ===
    live_preview = decoded_text
    if morse_buffer:
        try:
            temp_letter = morse_letters_to_text([[morse_buffer]])
            if temp_letter and temp_letter != '?':
                live_preview += temp_letter
            else:
                live_preview += f"[{morse_buffer}]"
        except Exception:
            live_preview += f"[{morse_buffer}]"

    socketio.emit('live', {'action': action, 'preview': live_preview, 'buffer': morse_buffer})


@socketio.on('connect')
def on_connect():
    print("🌐 Client connected")

@socketio.on('clear')
def handle_clear():
    """Clear all buffers."""
    global morse_buffer, decoded_text
    morse_buffer = ""
    decoded_text = ""
    socketio.emit('decoded', {'text': ''})
    socketio.emit('live', {'action': 'clear', 'preview': '', 'buffer': ''})

@socketio.on('morse_backspace')
def handle_morse_backspace():
    """Manual morse backspace trigger."""
    global morse_buffer
    if morse_buffer:
        morse_buffer = morse_buffer[:-1]
        socketio.emit('live', {'action': 'morse_backspace', 'preview': decoded_text + morse_buffer, 'buffer': morse_buffer})
        socketio.emit('decoded', {'text': decoded_text})

@socketio.on('letter_backspace')
def handle_letter_backspace():
    """Manual letter backspace trigger."""
    global decoded_text
    if decoded_text:
        decoded_text = decoded_text[:-1]
        socketio.emit('live', {'action': 'letter_backspace', 'preview': decoded_text, 'buffer': morse_buffer})
        socketio.emit('decoded', {'text': decoded_text})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
