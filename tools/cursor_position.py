
import time
import pyautogui

print("마우스를 움직이면 절대 좌표가 갱신됩니다. (Ctrl+C로 종료)")
try:
    while True:
        x, y = pyautogui.position()
        print(f"\r현재 좌표 → X: {x:4d}  Y: {y:4d}", end="")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n종료")