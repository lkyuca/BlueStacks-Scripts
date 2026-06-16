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
<img width="1008" height="476" alt="image" src="https://github.com/user-attachments/assets/6f340759-7aef-4fc4-babf-b43aca9893ff" />


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
<img width="1405" height="92" alt="image" src="https://github.com/user-attachments/assets/15092b3b-fae3-4b43-8522-8d2405161ba6" />

"it should perform this action automaticly once you have setup your path correctly in the script"



---

## ▶️ How to Use

1. Open BlueStacks and launch **C.A.T.S.**
2. Make sure your resolution is **1920 x 1080**
<img width="890" height="707" alt="image" src="https://github.com/user-attachments/assets/13913676-41fb-40a5-8e2d-cf1399ea8529" />

4. Navigate to the  **main menu** screen

<img width="1953" height="1116" alt="image" src="https://github.com/user-attachments/assets/4434a10a-8986-4a2e-893c-46854988c117" />
6. Run the script:
```bash
python cats_farmV3.py
```
<img width="957" height="553" alt="image" src="https://github.com/user-attachments/assets/444e1ab4-7bab-416d-85a9-e2d8f43ab221" />

4. When prompted, enter your current win streak (or `0` if you have none)

"is should do this automaticly with the new version with the streak detector function"

6. you will see a message saying Switch to BlueStacks — the script starts in 3 seconds!
<img width="747" height="64" alt="image" src="https://github.com/user-attachments/assets/4aefcd7d-5c43-4b28-8078-90b2ebe1d0fa" />

To stop the script press **q** in the terminal.
<img width="910" height="66" alt="image" src="https://github.com/user-attachments/assets/df9ead4b-587e-4f7c-9e61-8408c7bbab4d" />


---


## ✨ Features

- Automatically taps Quick Fight, Start Fight, and the result button
- Detects **Victory**, **Defeat**, and **Defeat with Win Streak** separately
- Avoids accidental ad clicks on the "Keep Win Streak" button
- Tracks your win streak across fights
- Runs in a loop until you stop it

<img width="464" height="159" alt="image" src="https://github.com/user-attachments/assets/a4eb2e2b-4198-4976-aa4f-39065eaa2f2c" />

---

## 🔧 Troubleshooting


**ADB not recognized**
→ Make sure the path to `adb.exe` in the script is correct.

**Unknown result detected**
→ The script will send a screenshot to the debug folder 

**contact information**
→ you can send an email if you are really struggeling linked on my [github profile]([(https://github.com/lkyuca)]) 


## 🙏 Credits

Built with Python + ADB + BlueStacks 5.  
Game: [C.A.T.S.: Crash Arena Turbo Stars](https://www.catsthegame.com/)
