# 👁️ Eye Blink Morse Code Translator

A web application that converts **eye blinks into text using Morse code**.  
This system allows users to communicate using only **eye movements**.

It is designed as an **assistive communication tool for people with speech or mobility impairments**.

---

## 🚀 Features

- **Dot (●)** – Short blink (0.1–0.4 seconds)
- **Dash (━)** – Medium blink (0.4–0.9 seconds)
- **Morse Backspace (⌫)** – Delete last dot/dash (0.9–1.5 seconds)
- **Letter Backspace (⌫⌫)** – Delete last letter (1.5–2.0 seconds)
- **Enter (↵)** – Finalize and speak message (2.0–2.5 seconds)
- **Space (␣)** – End word (2.5–3.0 seconds or auto after 2s pause)
- **Auto Decode** – Letters decode automatically after 2 seconds
- **Text-to-Speech** – Speaks the generated message
- **Machine Learning Model** – Trainable blink classification model

---

# ⚡ Quick Start

## 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
