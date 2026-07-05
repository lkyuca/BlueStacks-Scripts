"""
C.A.T.S. Timer Reader - Send to Discord
Simple script to read the championship timer and post it to Discord
"""

import os
import io
import sys
import re
import subprocess
import shutil
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import requests

# ============ CONFIGURATIE ============

ADB = r"your own path"
DEVICE = "127.0.0.1:5555"
TESSERACT_CMD = r"your own path"
DISCORD_WEBHOOK_URL = "your own token"

# Replit bot API — updates the live countdown embed automatically
REPLIT_BOT_URL = "Your own token"

# Timer region on screen (calibrated)
CHAMPIONSHIP_BOX = (280, 930, 510, 1010)

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# ============ ADB HELPERS ============

def get_adb_executable():
    if os.path.exists(ADB):
        return ADB
    exe = shutil.which("adb")
    if exe is None:
        raise FileNotFoundError(f"adb not found. Checked: {ADB} and system PATH")
    return exe

def get_target_device():
    exe = get_adb_executable()
    if DEVICE:
        res = subprocess.run([exe, "-s", DEVICE, "get-state"], capture_output=True, text=True)
        if res.returncode == 0 and "device" in (res.stdout or "").lower():
            return DEVICE
    return None

def adb(cmd):
    exe = get_adb_executable()
    device = get_target_device()
    if device:
        return subprocess.run([exe, "-s", device] + cmd, capture_output=True)
    return subprocess.run([exe] + cmd, capture_output=True)

def capture_screen_bytes():
    result = adb(["exec-out", "screencap", "-p"])
    if result.returncode != 0 or not result.stdout:
        return None
    return result.stdout

def normalize_pil_image(img):
    if img is None:
        return None
    if img.width < img.height:
        return img.rotate(-90, expand=True)
    return img

# ============ OCR ============

def read_championship_timer():
    """Read the championship timer from BlueStacks.

    Improvements:
    - Try a few nearby/expanded crop boxes in case CHAMPIONSHIP_BOX is slightly off
    - Try both OTSU threshold and adaptive thresholding
    - Resilient parsing that accepts HHMMSS digit runs
    - Saves debug crops when `DEBUG` environment var is set
    """
    def _parse_ocr_timer(ocr_text):
        """Try to interpret OCR text as HH:MM:SS even when colons are missing.
        Returns a timedelta or None.
        """
        if not ocr_text:
            return None
        # First try direct HH:MM:SS
        m = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", ocr_text)
        if m:
            h, mm, ss = (int(g) for g in m.groups())
            if 0 <= mm < 60 and 0 <= ss < 60:
                return timedelta(hours=h, minutes=mm, seconds=ss)

        # Remove non-digits and try to recover from HHMMSS or HMMSS styles
        digits = re.sub(r"\D", "", ocr_text)
        if len(digits) >= 6:
            # Prefer the last 6 digits as HHMMSS (handles stray leading artifacts)
            cand = digits[-6:]
            hh = int(cand[0:2])
            mm = int(cand[2:4])
            ss = int(cand[4:6])
            if 0 <= mm < 60 and 0 <= ss < 60:
                return timedelta(hours=hh, minutes=mm, seconds=ss)
        if len(digits) == 5:
            # HMMSS -> H:MM:SS
            hh = int(digits[0])
            mm = int(digits[1:3])
            ss = int(digits[3:5])
            if 0 <= mm < 60 and 0 <= ss < 60:
                return timedelta(hours=hh, minutes=mm, seconds=ss)
        return None

    data = capture_screen_bytes()
    if data is None:
        return None, ""

    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        return None, ""

    img = normalize_pil_image(img)

    # candidate boxes: original, slightly expanded, and shifted variants
    x1, y1, x2, y2 = CHAMPIONSHIP_BOX
    candidates = [
        (x1, y1, x2, y2),
        (max(0, x1 - 10), max(0, y1 - 8), x2 + 10, y2 + 8),
        (max(0, x1 - 20), max(0, y1 - 12), x2 + 20, y2 + 12),
        (max(0, x1 - 6), y1, x2 + 6, y2),
        (x1, max(0, y1 - 6), x2, y2 + 6),
    ]

    debug = os.getenv("DEBUG", os.getenv("CFV3_DEBUG", "0")) == "1"
    best_raw = ""

    for i, box in enumerate(candidates):
        bx1, by1, bx2, by2 = box
        try:
            crop = img.crop((bx1, by1, bx2, by2))
        except Exception:
            continue

        gray = cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2GRAY)
        scale = 4
        resized = cv2.resize(gray, (gray.shape[1] * scale, gray.shape[0] * scale),
                             interpolation=cv2.INTER_CUBIC)

        # Try template matcher directly on the resized grayscale first
        try:
            parsed_img, repr_txt = _digit_template_from_image(resized)
            if parsed_img is not None:
                return parsed_img, repr_txt
        except Exception:
            pass

        # Try OTSU binary
        _, thresh_otsu = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Try adaptive (helps with gradients/lighting)
        thresh_adapt = cv2.adaptiveThreshold(resized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 11, 2)

        for prep, img_for_ocr in (("otsu", thresh_otsu), ("adapt", thresh_adapt)):
            # Try multiple variants: normal, inverted, and a slightly sharpened version
            variants = []
            variants.append((prep, img_for_ocr))
            try:
                inv = cv2.bitwise_not(img_for_ocr)
                variants.append((prep + "_inv", inv))
            except Exception:
                pass

            # simple unsharp mask (sharpen)
            try:
                blur = cv2.GaussianBlur(img_for_ocr, (0, 0), 3)
                sharpen = cv2.addWeighted(img_for_ocr, 1.5, blur, -0.5, 0)
                variants.append((prep + "_sh", sharpen))
            except Exception:
                pass

            for vname, vimg in variants:
                # Also try morphological variants: eroded (removes thin outlines) and closed (fills gaps)
                morphs = [(vname, vimg)]
                try:
                    kern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    eroded = cv2.erode(vimg, kern, iterations=1)
                    morphs.append((vname + "_er", eroded))
                    closed = cv2.morphologyEx(vimg, cv2.MORPH_CLOSE, kern, iterations=1)
                    morphs.append((vname + "_cl", closed))
                except Exception:
                    pass

                for mvname, mvimg in morphs:
                    # Run Tesseract with explicit OEM and try multiple PSM modes
                    ocr_text = ""
                    for psm in (7, 6, 8):
                        try:
                            txt = pytesseract.image_to_string(
                                mvimg,
                                config=f"--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789:"
                            ).strip()
                        except Exception:
                            txt = ""
                        if txt:
                            ocr_text = txt
                            break

                if debug:
                    os.makedirs("debug", exist_ok=True)
                    safename = f"champ_crop_{i}_{vname}.png"
                    cv2.imwrite(os.path.join("debug", safename), vimg)
                    with open(os.path.join("debug", f"champ_ocr_{i}_{vname}.txt"), "w", encoding="utf-8") as f:
                        f.write(ocr_text)

                # quick accept if exact match with colons
                m = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", ocr_text)
                if m:
                    h, mm, ss = (int(g) for g in m.groups())
                    if 0 <= mm < 60 and 0 <= ss < 60:
                        return timedelta(hours=h, minutes=mm, seconds=ss), ocr_text

                # try robust digit parsing
                parsed = _parse_ocr_timer(ocr_text)
                if parsed is not None:
                    return parsed, ocr_text

                # remember best raw for reporting
                if len(ocr_text) > len(best_raw):
                    best_raw = ocr_text

    # If Tesseract approaches failed, try a template-based digit OCR fallback
    try:
        parsed_fallback, repr_text = _digit_template_fallback(img.crop((x1, y1, x2, y2)))
        if parsed_fallback is not None:
            return parsed_fallback, repr_text
    except Exception:
        pass

    return None, best_raw


def calibrate_championship_box(step=10, max_offset=40):
    """Scan nearby boxes around CHAMPIONSHIP_BOX to find the crop with the most digit-like contours.
    Saves candidate crops to `debug/calibrate/` and prints a recommended box.
    """
    data = capture_screen_bytes()
    if data is None:
        print("Could not capture screen for calibration.")
        return None
    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        print("Failed to parse screenshot for calibration.")
        return None
    img = normalize_pil_image(img)
    x1, y1, x2, y2 = CHAMPIONSHIP_BOX
    best = None
    scores = []
    os.makedirs(os.path.join("debug", "calibrate"), exist_ok=True)
    for dx in range(-max_offset, max_offset + 1, step):
        for dy in range(-max_offset, max_offset + 1, step):
            bx1 = max(0, x1 + dx)
            by1 = max(0, y1 + dy)
            bx2 = min(img.width, x2 + dx)
            by2 = min(img.height, y2 + dy)
            if bx2 <= bx1 or by2 <= by1:
                continue
            crop = img.crop((bx1, by1, bx2, by2))
            gray = cv2.cvtColor(np.array(crop), cv2.COLOR_RGB2GRAY)
            resized = cv2.resize(gray, (gray.shape[1] * 4, gray.shape[0] * 4), interpolation=cv2.INTER_CUBIC)
            _, th = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            mean = np.mean(th)
            mask = th if mean > 127 else 255 - th
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # score by number of reasonably large contours
            cnt_score = 0
            h_img, w_img = resized.shape[:2]
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w * h < 200:
                    continue
                if h < 0.25 * h_img:
                    continue
                cnt_score += 1
            scores.append(((bx1, by1, bx2, by2), cnt_score))
            # save crop for visual inspection
            fn = os.path.join("debug", "calibrate", f"crop_{bx1}_{by1}_{bx2}_{by2}.png")
            cv2.imwrite(fn, resized)
    if not scores:
        print("No candidate crops generated during calibration.")
        return None
    scores.sort(key=lambda t: t[1], reverse=True)
    best_box, best_score = scores[0]
    print(f"Recommended CHAMPIONSHIP_BOX: {best_box} (score={best_score})")
    print("Saved candidate crops to debug/calibrate/. Inspect the top crops and update CHAMPIONSHIP_BOX accordingly.")
    return best_box


def _build_digit_templates(size=(60, 90)):
    fonts = []
    font_paths = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
        r"C:\Windows\Fonts\tahoma.ttf",
    ]
    for path in font_paths:
        try:
            fonts.append(ImageFont.truetype(path, 100))
        except Exception:
            pass
    if not fonts:
        fonts.append(ImageFont.load_default())

    templates = {}
    for digit in range(10):
        best_img = None
        best_err = None
        for font in fonts:
            img = Image.new("L", size, color=255)
            draw = ImageDraw.Draw(img)
            text = str(digit)
            try:
                w, h = font.getsize(text)
            except Exception:
                bbox = draw.textbbox((0, 0), text, font=font)
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((size[0] - w) / 2, (size[1] - h) / 2), text, font=font, fill=0)
            arr = np.array(img)
            _, arr = cv2.threshold(arr, 128, 255, cv2.THRESH_BINARY_INV)
            error = np.mean(arr.astype(np.float32))
            if best_err is None or error < best_err:
                best_err = error
                best_img = arr
        templates[str(digit)] = best_img
    return templates


def _classify_digit_img(img_gray, templates):
    if img_gray is None:
        return None
    try:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    except Exception:
        thresh = img_gray
    best_digit = None
    best_score = -1.0
    for digit, tpl in templates.items():
        try:
            resized = cv2.resize(thresh, tpl.shape[::-1], interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(resized, tpl, cv2.TM_CCOEFF_NORMED)
            _, maxVal, _, _ = cv2.minMaxLoc(res)
        except Exception:
            maxVal = -1.0
        if maxVal > best_score:
            best_score = maxVal
            best_digit = digit
    if best_digit is None:
        return None
    return int(best_digit)


def _digit_template_fallback(pil_crop):
    """Segment digit regions from the crop and match against templates.
    Returns (timedelta, repr_text) or (None, '')
    """
    img = pil_crop
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    # gentle blur and adaptive threshold to get digits
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=1)
    # Choose mask where digits are white for contour finding
    mean_val = np.mean(th)
    if mean_val > 127:
        mask = th
    else:
        mask = 255 - th
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    h_img, w_img = gray.shape[:2]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 100:  # too small
            continue
        rects.append((x, y, w, h))
    if not rects:
        return None, ""
    rects = sorted(rects, key=lambda r: r[0])
    templates = _build_digit_templates((60, 90))
    digits = []
    for x, y, w, h in rects:
        pad = 4
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w_img, x + w + pad)
        y1 = min(h_img, y + h + pad)
        roi = gray[y0:y1, x0:x1]
        d = _classify_digit_img(roi, templates)
        if d is None:
            return None, ""
        digits.append(str(d))
    digits_only = "".join(digits)
    if len(digits_only) >= 6:
        cand = digits_only[-6:]
        hh = int(cand[0:2])
        mm = int(cand[2:4])
        ss = int(cand[4:6])
        if 0 <= mm < 60 and 0 <= ss < 60:
            return timedelta(hours=hh, minutes=mm, seconds=ss), f"{hh:02d}:{mm:02d}:{ss:02d}"
    return None, ":".join(digits)


def _digit_template_from_image(resized_gray):
    """Attempt digit recognition from a resized grayscale image (numpy array).
    Returns (timedelta, repr_text) or (None, '').
    """
    if resized_gray is None:
        return None, ""
    # Ensure binary where digits are white
    try:
        _, th = cv2.threshold(resized_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    except Exception:
        th = resized_gray
    # find contours of the digits using correct polarity
    mean_val = np.mean(th)
    if mean_val > 127:
        mask = th
    else:
        mask = 255 - th
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, ""
    rects = []
    h_img, w_img = resized_gray.shape[:2]
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w * h < 200:  # skip tiny noise
            continue
        if h < 0.25 * h_img:
            continue
        rects.append((x, y, w, h))
    if not rects:
        return None, ""
    rects = sorted(rects, key=lambda r: r[0])
    templates = _build_digit_templates((60, 90))
    digits = []
    for x, y, w, h in rects:
        pad = 6
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w_img, x + w + pad)
        y1 = min(h_img, y + h + pad)
        roi = resized_gray[y0:y1, x0:x1]
        # resize roi to template size for matching
        try:
            roi_resized = cv2.resize(roi, (templates['0'].shape[1], templates['0'].shape[0]), interpolation=cv2.INTER_AREA)
        except Exception:
            roi_resized = roi
        d = _classify_digit_img(roi_resized, templates)
        if d is None:
            return None, ""
        digits.append(str(d))
    digits_only = "".join(digits)
    if len(digits_only) >= 6:
        cand = digits_only[-6:]
        hh = int(cand[0:2])
        mm = int(cand[2:4])
        ss = int(cand[4:6])
        if 0 <= mm < 60 and 0 <= ss < 60:
            return timedelta(hours=hh, minutes=mm, seconds=ss), f"{hh:02d}:{mm:02d}:{ss:02d}"
    return None, ":".join(digits)

# ============ DISCORD ============

def send_to_discord(remaining, end_time):
    """Send timer info to Discord"""
    if remaining is None:
        message = {
            "content": "❌ Could not read timer. Make sure BlueStacks is running and championship screen is visible."
        }
    else:
        message = {
            "content": (
                f"🕐 **C.A.T.S. Championship Timer**\n\n"
                f"**Current Time Remaining:** `{remaining}`\n"
                f"**Expected End Time:** `{end_time.strftime('%d/%m/%Y %H:%M')}`\n\n"
                f"_Bot countdown updated automatically — use `/countdown_status` to check._"
            )
        }

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=message)
        resp.raise_for_status()
        print("✓ Timer sent to Discord!")
        return True
    except Exception as e:
        print(f"❌ Failed to send to Discord: {e}")
        return False

# ============ REPLIT BOT UPDATE ============

def update_replit_bot(end_time):
    """Send end time to the Replit bot so it updates the live countdown embed"""
    payload = {"end_time": end_time.strftime("%d/%m/%Y %H:%M")}
    try:
        resp = requests.post(REPLIT_BOT_URL, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"✓ Bot updated! End time: {end_time.strftime('%d/%m/%Y %H:%M')}")
        return True
    except Exception as e:
        print(f"❌ Failed to update bot: {e}")
        return False

# ============ MAIN ============

def main():
    print("🕐 C.A.T.S. Timer Reader")
    print("=" * 50)
    print("Reading championship timer...\n")

    # Calibration mode
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        calibrate_championship_box()
        return True

    remaining, raw_text = read_championship_timer()

    if remaining is None:
        print(f"❌ Could not read timer")
        print(f"   OCR text: '{raw_text}'")
        print(f"\nMake sure:")
        print("  1. BlueStacks is running")
        print("  2. Championship screen is visible")
        print("  3. Timer is clearly visible")
        return False

    now = datetime.now()
    end_time = now + remaining

    print(f"✓ Timer found: {remaining}")
    print(f"✓ OCR text: '{raw_text}'")
    print(f"✓ End time: {end_time.strftime('%d/%m/%Y %H:%M')}")
    print(f"\nSending to Discord and updating bot...")

    send_to_discord(remaining, end_time)
    update_replit_bot(end_time)

    print("\n" + "=" * 50)
    print("✓ Done! Bot countdown is now live in Discord.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    main()
