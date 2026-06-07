# 🤖 C.A.T.S. BlueStacks Auto Fight Script

An automation script that automatically farms Quick Fights in **C.A.T.S.: Crash Arena Turbo Stars** using BlueStacks 5. It detects win/loss outcomes and taps the correct button every time — no ads, no mistakes.


---

## 📋 Requirements

- [BlueStacks 5](https://www.bluestacks.com/)
- [Python 3.13+](https://www.python.org/downloads/)
- [ADB (Android Debug Bridge)](https://developer.android.com/tools/releases/platform-tools)
- Python libraries:
  - `Pillow`

Install the required library with:
```bash
pip install Pillow
```

---

## ⚙️ Setup

### 1. Enable ADB in BlueStacks
1. Open BlueStacks and go to **Settings → Advanced**
2. Enable **Android Debug Bridge (ADB)**
3. Note the IP and port shown (usually `127.0.0.1:5555`)
4. <img width="1008" height="476" alt="image" src="https://github.com/user-attachments/assets/6f340759-7aef-4fc4-babf-b43aca9893ff" />


### 2. Download ADB
1. Download [Platform Tools](https://developer.android.com/tools/releases/platform-tools) from Google
2. Extract it to a folder on your PC (e.g. `C:\adb\`)

### 3. Configure the script
Open `cats_farm.py` and update the following lines to match your setup:

```python
ADB = r"C:\path\to\platform-tools\adb.exe"   # Path to your adb.exe
DEVICE = "127.0.0.1:5555"                     # Your BlueStacks IP and port
```

### 4. Connect ADB to BlueStacks
Open a terminal and run:
```bash
adb connect 127.0.0.1:5555
```
You should see: `connected to 127.0.0.1:5555`

---

## ▶️ How to Use

1. Open BlueStacks and launch **C.A.T.S.**
2. Navigate to the **main menu** screen
<img width="1953" height="1116" alt="image" src="https://github.com/user-attachments/assets/4434a10a-8986-4a2e-893c-46854988c117" />
4. Run the script:
```bash
python cats_farm.py
```
<img width="957" height="553" alt="image" src="https://github.com/user-attachments/assets/444e1ab4-7bab-416d-85a9-e2d8f43ab221" />

4. When prompted, enter your current win streak (or `0` if you have none)
5. Switch to BlueStacks — the script starts in 3 seconds!
<img width="747" height="64" alt="image" src="https://github.com/user-attachments/assets/4aefcd7d-5c43-4b28-8078-90b2ebe1d0fa" />

To stop the script press **Ctrl + C** in the terminal.

---

## 🗺️ Button Coordinates

The script uses percentage-based coordinates (works across resolutions). These are calibrated for the default BlueStacks 5 layout:

| Action | X | Y |
|---|---|---|
| Quick Fight | 85 | 120 |
| Start Fight | 50 | 40 |
| OK (Victory) | 58 | 85 |
| Retreat (No streak) | 80 | 120 |
| Retreat (Streak loss) | 70 | 120 |

> If buttons are in different positions on your setup, hover over them in BlueStacks to get the coordinates and update the `tap()` calls in the script.

---

## ✨ Features

- Automatically taps Quick Fight, Start Fight, and the result button
- Detects **Victory**, **Defeat**, and **Defeat with Win Streak** separately
- Avoids accidental ad clicks on the "Keep Win Streak" button
- Tracks your win streak across fights
- Runs in a loop until you stop it

---

## 🔧 Troubleshooting

**Script clicks the wrong button**
→ Hover over the correct button in BlueStacks and update the coordinates in the script.

**Fight not finished before result is detected**
→ Increase `time.sleep(12)` to a higher value like `time.sleep(20)`.

**ADB not recognized**
→ Make sure the path to `adb.exe` in the script is correct.

**Unknown result detected**
→ The script will print the RGB value of the banner. Share it and the detection thresholds can be updated.



## 🙏 Credits

Built with Python + ADB + BlueStacks 5.  
Game: [C.A.T.S.: Crash Arena Turbo Stars](https://www.catsthegame.com/)
