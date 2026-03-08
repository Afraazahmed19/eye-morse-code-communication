# recorder.py
import cv2
import csv
from blink_detector import BlinkProcessor

OUT_CSV = 'blink_data.csv'
proc = BlinkProcessor()
cap = cv2.VideoCapture(0)

print('Recorder: Press q to quit.')
print('Labels:')
print('  d = dot (short blink)')
print('  k = dash (medium blink)')
print('  m = morse_backspace (delete last dot/dash)')
print('  l = letter_backspace (delete last letter)')
print('  s = space (end word)')
print('  e = enter (finalize and speak)')

with open(OUT_CSV, 'a', newline='') as f:
    writer = csv.writer(f)
    # If file new - write header once (optional)
    writer.writerow(['duration','avg_ear','min_ear','time_gap','label'])
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ev = proc.process_frame(frame)
            cv2.putText(frame, 'Recorder: press label when blink detected', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),1)
            cv2.imshow('recorder', frame)
            key = cv2.waitKey(1) & 0xFF
            if ev:
                print('Blink duration:', ev['duration'])
                print('Press label key for this blink (d/k/s/b/e) or q to quit:')
                while True:
                    k = cv2.waitKey(0) & 0xFF
                    label = None
                    if k == ord('d'):
                        label = 'dot'
                    elif k == ord('k'):
                        label = 'dash'
                    elif k == ord('m'):
                        label = 'morse_backspace'
                    elif k == ord('l'):
                        label = 'letter_backspace'
                    elif k == ord('s'):
                        label = 'space'
                    elif k == ord('e'):
                        label = 'enter'
                    elif k == ord('q'):
                        raise KeyboardInterrupt
                    if label:
                        writer.writerow([ev['duration'], ev['avg_ear'], ev['min_ear'], ev['time_gap'] or 0.0, label])
                        print('Saved as', label)
                        break
            if key == ord('q'):
                break
    except KeyboardInterrupt:
        print('Stopping recorder...')
    finally:
        cap.release()
        cv2.destroyAllWindows()
        proc.close()
