import cv2
import mediapipe as mp
import time
import numpy as np
import joblib
import os
import pandas as pd

class BlinkProcessor:
    """
    Detect blinks (duration, ear stats), and classify into:
      - 'dot', 'dash', 'space', 'backspace', 'enter'
    Uses model if available, otherwise rule-based fallback.
    """

    FEATURE_COLS = ['duration', 'avg_ear', 'min_ear', 'time_gap', 'ear_range', 'duration_normalized', 'blink_intensity']
    BASE_FEATURES = ['duration', 'avg_ear', 'min_ear', 'time_gap']

    def __init__(self, model_path=os.path.join("models", "blink_classifier.pkl"), 
                 scaler_path=os.path.join("models", "scaler.pkl")):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # --- Blink state ---
        self.blinking = False
        self.start_time = None
        self.eye_aspect_ratios = []
        self.last_blink_end = 0.0
        self.prev_blink_time = 0.0

        # --- Model loading ---
        self.classifier = None
        self.scaler = None
        self.max_duration = 3.0  # Default max duration for normalization
        
        if os.path.exists(model_path):
            try:
                self.classifier = joblib.load(model_path)
                print(f"✅ Model loaded from {model_path}")
                
                # Try to load scaler if available
                if os.path.exists(scaler_path):
                    try:
                        self.scaler = joblib.load(scaler_path)
                        print(f"✅ Scaler loaded from {scaler_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to load scaler: {e}")
                        
            except Exception as e:
                print(f"⚠️ Failed to load model at {model_path}: {e}")
        else:
            print("⚠️ No trained model found. Using rule-based blink classification.")

        # --- Thresholds and timings ---
        self.EAR_THRESH = 0.23           # lower = more sensitive blink detection
        self.DOT_THRESHOLD = 0.40        # seconds (short blink)
        self.DASH_THRESHOLD = 0.90       # seconds (long blink)
        self.DEBOUNCE_TIME = 0.30        # minimum gap between two valid blinks
        self.IGNORE_TOO_LONG = 2.0       # ignore eye closures > 2 sec

    def eye_aspect_ratio(self, landmarks, eye_indices):
        points = np.array([[landmarks[i].x, landmarks[i].y] for i in eye_indices])
        A = np.linalg.norm(points[1] - points[5])
        B = np.linalg.norm(points[2] - points[4])
        C = np.linalg.norm(points[0] - points[3])
        ear = (A + B) / (2.0 * C) if C != 0 else 0.0
        return ear

    def _classify(self, duration, avg_ear, min_ear, time_gap):
        """Predict blink type using model or rule-based fallback."""
        if self.classifier is not None:
            try:
                # Calculate additional features
                ear_range = avg_ear - min_ear if avg_ear > min_ear else 0.0
                duration_normalized = duration / (self.max_duration + 1e-6)
                blink_intensity = min_ear / (avg_ear + 1e-6) if avg_ear > 0 else 0.0
                
                # Create feature array
                features = np.array([[duration, avg_ear, min_ear, time_gap, ear_range, 
                                    duration_normalized, blink_intensity]])
                
                # Scale if scaler available
                if self.scaler is not None:
                    features = self.scaler.transform(features)
                
                pred = self.classifier.predict(features)[0]
                return pred
            except Exception as e:
                print("⚠️ Model predict failed:", e)
                import traceback
                traceback.print_exc()

        # --- Rule-based fallback ---
        # Dot: very short blink (0.1-0.4s)
        if duration < self.DOT_THRESHOLD:
            return 'dot'
        # Dash: medium blink (0.4-0.9s)
        elif duration < self.DASH_THRESHOLD:
            return 'dash'
        # Morse backspace: medium-long blink (0.9-1.5s)
        elif duration < 1.5:
            return 'morse_backspace'
        # Letter backspace: long blink (1.5-2.0s)
        elif duration < 2.0:
            return 'letter_backspace'
        # Enter: very long blink (2.0-2.5s)
        elif duration < 2.5:
            return 'enter'
        # Space: extra long blink (2.5-3.0s) - optional, can also use timeout
        elif duration < 3.0:
            return 'space'
        else:
            return None  # too long — ignore accidental closure

    def process_frame(self, frame):
        """Process a frame and detect blinks."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE = [362, 385, 387, 263, 373, 380]

        left_ear = self.eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = self.eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        now = time.time()
        blink_event = None

        # --- Detect blink start ---
        if ear < self.EAR_THRESH and not self.blinking:
            if now - self.last_blink_end < self.DEBOUNCE_TIME:
                return None  # ignore tiny flickers
            self.blinking = True
            self.start_time = now
            self.eye_aspect_ratios = []

        # --- During blink ---
        if self.blinking:
            self.eye_aspect_ratios.append(ear)

        # --- Detect blink end ---
        if ear >= self.EAR_THRESH and self.blinking:
            self.blinking = False
            duration = now - (self.start_time or now)
            avg_ear = float(np.mean(self.eye_aspect_ratios)) if self.eye_aspect_ratios else float(ear)
            min_ear = float(np.min(self.eye_aspect_ratios)) if self.eye_aspect_ratios else float(ear)
            time_gap = now - self.last_blink_end if self.last_blink_end != 0 else 0.0

            # Ignore accidental long closures
            if duration > self.IGNORE_TOO_LONG:
                self.last_blink_end = now
                return None

            blink_type = self._classify(duration, avg_ear, min_ear, time_gap)
            if blink_type:
                blink_event = {
                    'duration': duration,
                    'avg_ear': avg_ear,
                    'min_ear': min_ear,
                    'time_gap': time_gap,
                    'type': blink_type
                }
                print(f"Blink: {blink_type} | Duration: {duration:.2f}s | Gap: {time_gap:.2f}s")

            self.last_blink_end = now
            self.start_time = None
            self.eye_aspect_ratios = []

        return blink_event

    def close(self):
        try:
            self.face_mesh.close()
        except Exception:
            pass
