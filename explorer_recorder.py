# explorer_recorder.py
import cv2, mss, numpy as np, win32gui, win32con
import time, threading, ctypes
from datetime import datetime
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────
OUTPUT_DIR      = Path.home() / "Videos" / "ExplorerRecords"
WEBCAM_DIR      = Path.home() / "Videos" / "ExplorerRecords" / "FaceCam"
FPS             = 10
CHECK_DELAY     = 1.0
CAPTURE_COOLDOWN = 5  # detik antar snapshot

WATCHED_FOLDERS = [
    r"D:", r"E:", r"F:"  # ganti sesuai kebutuhan
]
# ──────────────────────────────────────────────────────

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
WEBCAM_DIR.mkdir(parents=True, exist_ok=True)

_recording         = False
_stop_event        = threading.Event()
_lock              = threading.Lock()
_last_folder       = ""
_last_capture_time = 0


def get_explorer_windows() -> list:
    found = []
    def _enum(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        if win32gui.GetClassName(hwnd) in ("CabinetWClass", "ExplorerWClass"):
            found.append(hwnd)
    win32gui.EnumWindows(_enum, None)
    return found


def get_active_explorer_path() -> str:
    try:
        import pythoncom
        from win32com.client import Dispatch
        pythoncom.CoInitialize()
        shell = Dispatch("Shell.Application")
        for w in shell.Windows():
            try:
                loc = w.LocationURL
                if loc.startswith("file:///"):
                    return loc[8:].replace("/", "\\").replace("%20", " ")
            except Exception:
                continue
    except Exception:
        pass
    return ""


def capture_webcam():
    global _last_capture_time
    now = time.time()
    if now - _last_capture_time < CAPTURE_COOLDOWN:
        return
    _last_capture_time = now

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[WARN] Webcam tidak ditemukan.")
        return
    ret, frame = cap.read()
    cap.release()
    if ret:
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path  = WEBCAM_DIR / f"face_{stamp}.jpg"
        cv2.imwrite(str(path), frame)
        print(f"[CAM] Snapshot → {path}")


def _record_loop(filepath: str):
    with mss.mss() as sct:
        mon    = sct.monitors[1]
        w, h   = mon["width"], mon["height"]
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        writer = cv2.VideoWriter(filepath, fourcc, float(FPS), (w, h))
        if not writer.isOpened():
            print(f"[ERROR] Gagal buka VideoWriter: {filepath}")
            return
        interval = 1.0 / FPS
        print(f"[REC] Mulai → {filepath}")
        while not _stop_event.is_set():
            t0    = time.perf_counter()
            img   = sct.grab(mon)
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGRA2BGR)
            writer.write(frame)
            slp = interval - (time.perf_counter() - t0)
            if slp > 0:
                time.sleep(slp)
        writer.release()
        print(f"[REC] Selesai → {filepath}")


def start_recording():
    global _recording
    with _lock:
        if _recording:
            return None
        _recording = True
        _stop_event.clear()
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    t = threading.Thread(target=_record_loop, args=(str(OUTPUT_DIR / f"explorer_{stamp}.avi"),), daemon=True)
    t.start()
    return t


def stop_recording(thread):
    global _recording
    _stop_event.set()
    if thread:
        thread.join(timeout=10)
    with _lock:
        _recording = False


def monitor_loop():
    global _last_folder
    explorer_was_open = False
    rec_thread        = None

    print("[*] Monitor aktif...")
    print(f"[*] Video  : {OUTPUT_DIR}")
    print(f"[*] FaceCam: {WEBCAM_DIR}\n")

    while True:
        try:
            windows_open = bool(get_explorer_windows())

            if windows_open and not explorer_was_open:
                explorer_was_open = True
                rec_thread = start_recording()

            elif not windows_open and explorer_was_open:
                explorer_was_open = False
                stop_recording(rec_thread)
                rec_thread   = None
                _last_folder = ""

            if windows_open:
                current_folder = get_active_explorer_path()
                if current_folder and current_folder != _last_folder:
                    _last_folder = current_folder
                    cur = current_folder.rstrip("\\").lower()
                    for watched in WATCHED_FOLDERS:
                        if cur == watched.rstrip("\\").lower():
                            print(f"[!] Folder sensitif dibuka: {current_folder}")
                            threading.Thread(target=capture_webcam, daemon=True).start()
                            break

        except Exception as e:
            print(f"[WARN] {e}")

        time.sleep(CHECK_DELAY)


if __name__ == "__main__":
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, win32con.SW_HIDE)
    except Exception:
        pass
    monitor_loop()