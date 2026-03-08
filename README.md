👁️ Eye Blink Morse Code Translator
A web application that converts eye blinks to text using Morse code. Control your computer using only your eyes!

Features
✅ Dot (●) - Short blink (0.1-0.4s)
✅ Dash (━) - Medium blink (0.4-0.9s)
✅ Morse Backspace (⌫) - Delete last dot/dash (0.9-1.5s)
✅ Letter Backspace (⌫⌫) - Delete last letter (1.5-2.0s)
✅ Space (␣) - End word (2.5-3.0s or auto after 2s pause)
✅ Enter (↵) - Finalize & speak (2.0-2.5s)
✅ Auto-decode - Letters automatically decode after 2 seconds
✅ Text-to-Speech - Hear your message spoken aloud
✅ Machine Learning - Trainable model for improved accuracy
Quick Start
1. Install Dependencies
pip install -r requirements.txt
2. Run the Application
python app.py
3. Open in Browser
Navigate to http://localhost:5000 and allow camera access.

Training Your Model (For Better Accuracy)
Step 1: Collect Training Data
python recorder.py
When a blink is detected:

Press d for dot
Press k for dash
Press m for morse_backspace
Press l for letter_backspace
Press s for space
Press e for enter
Press q to quit
Recommendation: Collect at least 30-50 samples per class for best results.

Step 2: Train the Model
python train_model.py
This will:

Load your training data
Extract features and engineer additional features
Train multiple models (Random Forest & Gradient Boosting)
Select the best performing model
Save the trained model to models/blink_classifier.pkl
Save the feature scaler to models/scaler.pkl
Step 3: Use the Trained Model
Restart the application - it will automatically use your trained model!

python app.py
Blink Pattern Reference
Action	Duration	Description
DOT	0.1-0.4s	Quick, natural blink
DASH	0.4-0.9s	Hold eyes closed slightly longer
Morse Backspace	0.9-1.5s	Delete last dot/dash
Letter Backspace	1.5-2.0s	Delete last decoded letter
ENTER	2.0-2.5s	Finalize and speak
SPACE	2.5-3.0s	End word (or wait 2s)
Example: Typing "HELLO"
H = ●●●● (4 dots)
E = ● (1 dot)
L = ●━●● (dot-dash-dot-dot)
L = ●━●● (dot-dash-dot-dot)
O = ━━━ (3 dashes)
ENTER → Speaks "HELLO"
Project Structure
eye_morse_webapp/
├── app.py                 # Main Flask application
├── blink_detector.py      # Blink detection & classification
├── recorder.py            # Training data collection
├── train_model.py         # Model training script
├── utils.py               # Morse code utilities
├── blink_data.csv         # Training data
├── models/
│   ├── blink_classifier.pkl  # Trained model
│   └── scaler.pkl            # Feature scaler
├── templates/
│   └── index.html         # Web interface
├── BLINK_GUIDE.md         # Detailed blink guide
└── requirements.txt       # Python dependencies
Model Features
The model uses the following features:

duration - Blink duration in seconds
avg_ear - Average Eye Aspect Ratio during blink
min_ear - Minimum EAR during blink
time_gap - Time since last blink
ear_range - Range of EAR values (avg - min)
duration_normalized - Normalized duration
blink_intensity - Intensity of blink (min/avg)
Tips for Best Results
Good Lighting: Ensure consistent, adequate lighting
Face the Camera: Keep your face clearly visible
Practice Timing: Practice the different blink durations
Train Personal Model: Train with your own blink patterns
Steady Position: Keep head relatively still during blinks
Clear Blinks: Make deliberate, full eye closures
Troubleshooting
Blink not detected: Check lighting and camera visibility
Wrong classification: Train model with more samples
Too sensitive: Adjust EAR_THRESH in blink_detector.py (increase value)
Not sensitive enough: Decrease EAR_THRESH value
Dependencies
Flask - Web framework
Flask-SocketIO - WebSocket support
OpenCV - Video processing
MediaPipe - Face mesh detection
scikit-learn - Machine learning
NumPy & Pandas - Data processing
joblib - Model serialization
pyttsx3 - Text-to-speech
License
This project is open source and available for personal and educational use.

Support
For detailed information about blink patterns, see BLINK_GUIDE.md.
