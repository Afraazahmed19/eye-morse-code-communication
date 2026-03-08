# 👁️ Eye Blink Morse Code Guide

## Overview
This application allows you to communicate using eye blinks converted to Morse code. Each blink pattern corresponds to a specific action that helps you build letters and words.

## Blink Patterns & Timing

### 1. **DOT (●)** - Short Blink
- **Duration:** 0.1 - 0.4 seconds
- **Description:** A quick, natural blink
- **Use:** Building Morse code dots (●) for letters like E (●), I (●●), S (●●●)
- **Example:** Close eyes briefly and open immediately

### 2. **DASH (━)** - Medium Blink
- **Duration:** 0.4 - 0.9 seconds
- **Description:** Hold your eyes closed slightly longer than a normal blink
- **Use:** Building Morse code dashes (━) for letters like T (━), M (━━), O (━━━)
- **Example:** Close eyes and hold for about half a second, then open

### 3. **MORSE BACKSPACE (⌫)** - Medium-Long Blink
- **Duration:** 0.9 - 1.5 seconds
- **Description:** A noticeably longer blink
- **Use:** Deletes the last dot or dash from your current Morse code letter
- **Example:** If you have "●━" (A) and blink this pattern, you'll have "●" (E)
- **Tip:** Use this if you made a mistake while building a letter

### 4. **LETTER BACKSPACE (⌫⌫)** - Long Blink
- **Duration:** 1.5 - 2.0 seconds
- **Description:** A long, deliberate blink
- **Use:** Deletes the last decoded letter from your final text
- **Example:** If you have "HE" and blink this pattern, you'll have "H"
- **Tip:** Use this to correct a completed letter

### 5. **SPACE (␣)** - End Word
- **Duration:** 2.5 - 3.0 seconds OR wait 2 seconds without blinking
- **Description:** Very long blink OR automatic after pause
- **Use:** Adds a space after the current letter (end of word)
- **Example:** Type "HELLO" then space to start a new word
- **Tip:** You can also wait 2 seconds without blinking - the system will auto-decode the current letter and you can add a space manually

### 6. **ENTER (↵)** - Finalize & Speak
- **Duration:** 2.0 - 2.5 seconds
- **Description:** Very long blink (but shorter than space)
- **Use:** Finalizes your text and speaks it aloud using text-to-speech
- **Example:** Type your message, then enter to hear it spoken
- **Tip:** This also clears your text buffer to start a new message

## How to Use

### Basic Workflow:
1. **Build a letter:** Use DOT (●) and DASH (━) blinks to create Morse code
   - Example: "●━" = A, "━●●●" = B, "●━●" = R
   
2. **Complete the letter:** 
   - Wait 2 seconds (auto-decode) OR
   - Use SPACE to add space after letter
   - Use ENTER to finalize and speak

3. **Correct mistakes:**
   - If still building letter: Use MORSE BACKSPACE (⌫)
   - If letter already decoded: Use LETTER BACKSPACE (⌫⌫)

### Example: Typing "HELLO"

```
H = ●●●●
  → DOT, DOT, DOT, DOT (wait 2 sec or SPACE)
  
E = ●
  → DOT (wait 2 sec or SPACE)
  
L = ●━●●
  → DOT, DASH, DOT, DOT (wait 2 sec or SPACE)
  
L = ●━●●
  → DOT, DASH, DOT, DOT (wait 2 sec or SPACE)
  
O = ━━━
  → DASH, DASH, DASH (wait 2 sec or SPACE)
  
ENTER → Speaks "HELLO"
```

## Morse Code Reference

### Alphabet:
- **A:** ●━
- **B:** ━●●●
- **C:** ━●━●
- **D:** ━●●
- **E:** ●
- **F:** ●●━●
- **G:** ━━●
- **H:** ●●●●
- **I:** ●●
- **J:** ●━━━
- **K:** ━●━
- **L:** ●━●●
- **M:** ━━
- **N:** ━●
- **O:** ━━━
- **P:** ●━━●
- **Q:** ━━●━
- **R:** ●━●
- **S:** ●●●
- **T:** ━
- **U:** ●●━
- **V:** ●●●━
- **W:** ●━━
- **X:** ━●●━
- **Y:** ━●━━
- **Z:** ━━●●

## Training the Model

For better accuracy, you can train the model with your own blink patterns:

1. **Run the recorder:**
   ```bash
   python recorder.py
   ```

2. **Collect training data:**
   - When a blink is detected, press the corresponding key:
     - `d` = dot
     - `k` = dash
     - `m` = morse_backspace
     - `l` = letter_backspace
     - `s` = space
     - `e` = enter
   - Collect at least **30-50 samples per class** for best results
   - Press `q` to quit

3. **Train the model:**
   ```bash
   python train_model.py
   ```

4. **Restart the app:**
   ```bash
   python app.py
   ```

## Tips for Better Accuracy

1. **Consistent Lighting:** Use consistent lighting conditions
2. **Face the Camera:** Keep your face clearly visible in the camera
3. **Practice Timing:** Practice the timing differences between blink types
4. **Train Personal Model:** Train the model with your own blink patterns for best results
5. **Steady Position:** Keep your head relatively still during blinks
6. **Clear Blinks:** Make deliberate, clear blinks (full eye closure)

## Troubleshooting

- **Blink not detected:** Ensure good lighting and face visibility
- **Wrong classification:** Train the model with more samples of your blinks
- **Too sensitive/not sensitive enough:** Adjust `EAR_THRESH` in `blink_detector.py`
- **Timing issues:** Practice the duration differences, or retrain with more data

## System Requirements

- Python 3.7+
- Webcam
- Good lighting
- Modern web browser with camera access

## Files

- `app.py` - Main Flask application
- `blink_detector.py` - Blink detection and classification
- `recorder.py` - Training data collection tool
- `train_model.py` - Model training script
- `blink_data.csv` - Training data
- `models/blink_classifier.pkl` - Trained model
- `models/scaler.pkl` - Feature scaler

## Support

For issues or improvements, please check the code comments or contact the developer.

