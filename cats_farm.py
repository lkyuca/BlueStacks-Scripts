import subprocess
import time
import io
from PIL import Image

ADB = r"C:\Users\lucam\OneDrive\Bureaublad\mappen\Scripts\blue stacks\platform-tools\adb.exe"
DEVICE = "127.0.0.1:5555"

def adb(cmd):
    return subprocess.run([ADB, "-s", DEVICE] + cmd, capture_output=True)

def tap(x, y):
    px = int(x / 100 * 1280)
    py = int(y / 100 * 720)
    adb(["shell", "input", "tap", str(px), str(py)])

def detect_result():
    result = adb(["exec-out", "screencap", "-p"])
    img = Image.open(io.BytesIO(result.stdout))
    r, g, b, *_ = img.getpixel((728, 200))
    print(f"  Banner pixel RGB: ({r}, {g}, {b})")
    if r > 180 and g < 60 and b < 60:
        return "victory"
    elif r > 80 and g < 60 and b < 40:
        return "defeat"
    return "unknown"

win_streak = int(input("Do you have a current win streak? Enter the number (0 if none): "))
print("Starting in 3 seconds... switch to BlueStacks!")
time.sleep(3)

fight_count = 0

while True:
    fight_count += 1
    print(f"\n--- Fight {fight_count} | Current streak: {win_streak} ---")

    # 1. Quick Fight
    print("Tapping Quick Fight...")
    if fight_count > 1:
        time.sleep(4)  # Extra delay for 2nd fight onwards
    tap(85, 120)
    time.sleep(3)

    # 2. Start Fight
    print("Tapping Start Fight...")
    tap(50, 40)
    time.sleep(12)

    # 3. Detect result
    result = detect_result()
    print(f"  Result: {result}")

    if result == "victory":
        win_streak += 1
        print(f"  WIN - streak is now {win_streak} - Tapping OK...")
        tap(85, 120)

    elif result == "defeat":
        if win_streak > 0:
            print(f"  LOSS - had streak of {win_streak} - Tapping streak loss Retreat...")
            tap(70, 120)  # <-- update this coordinate once you find it!
        else:
            print("  LOSS - no streak - Tapping Retreat...")
            tap(80, 120)
        win_streak = 0
        time.sleep(8)  # Wait for main screen to fully load before next loop
