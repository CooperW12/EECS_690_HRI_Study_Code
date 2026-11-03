import tkinter as tk
import sys, time, threading, qi
import numpy as np                 # pip install numpy
from PIL import Image, ImageTk     # pip install pillow

if len(sys.argv) == 2:
    ROBOT_IP = sys.argv[1]
    ROBOT_PORT = 9559
else:
    print("please provide proper number of arguments")
    print("Proper program usage: python3 name.py IP_ADDRESS_HERE")
    sys.exit(1)

# ---------------- Camera settings ----------------
CAM_TOP = 0
CAM_BOTTOM = 1
RES_QQVGA = 0          # 160x120
RES_QVGA = 1           # 320x240
COLORSPACE_YUV422 = 9  # native camera format: smaller and no conversion on the robot
CAM_RESOLUTION = RES_QVGA
CAM_FPS = 30
GUI_REFRESH_MS = 15

# Which feeds to run. Both cameras share one bus on NAO, so running both is
# slower. Try ("top",) or ("bottom",) to see the full speed of a single camera.
ACTIVE_CAMERAS = ("top", "bottom")

RES_SIZES = {RES_QQVGA: (160, 120), RES_QVGA: (320, 240)}
VIEW_W, VIEW_H = RES_SIZES[CAM_RESOLUTION]


def yuv422_to_rgb(data, w, h):
    """Convert a packed YUYV (YUV422) buffer to RGB bytes using numpy."""
    a = np.frombuffer(data, dtype=np.uint8).reshape(h, w // 2, 4).astype(np.int16)
    y = np.empty((h, w), dtype=np.int16)
    y[:, 0::2] = a[:, :, 0]
    y[:, 1::2] = a[:, :, 2]
    u = np.repeat(a[:, :, 1], 2, axis=1) - 128
    v = np.repeat(a[:, :, 3], 2, axis=1) - 128
    r = y + ((359 * v) >> 8)
    g = y - ((88 * u + 183 * v) >> 8)
    b = y + ((454 * u) >> 8)
    rgb = np.stack((r, g, b), axis=-1).clip(0, 255).astype(np.uint8)
    return rgb.tobytes()


class CameraFeed:
    """Pulls frames from one NAO camera on a background thread and converts
    them to RGB there, so the GUI thread only has to draw."""

    def __init__(self, video_service, camera_index, name):
        self.video_service = video_service
        self.camera_index = camera_index
        self.name = name
        self.handle = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = None
        self.latest = None      # (width, height, rgb_bytes)
        self.frame_id = 0
        self.error = None
        self.fps = 0.0

    def start(self):
        self.handle = self.video_service.subscribeCamera(
            self.name, self.camera_index, CAM_RESOLUTION, COLORSPACE_YUV422, CAM_FPS
        )
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        count = 0
        t0 = time.time()
        while not self.stop_event.is_set():
            try:
                frame = self.video_service.getImageRemote(self.handle)
                if frame is not None:
                    w, h = frame[0], frame[1]
                    rgb = yuv422_to_rgb(bytes(frame[6]), w, h)
                    with self.lock:
                        self.latest = (w, h, rgb)
                        self.frame_id += 1
                        self.error = None
                    count += 1
                    now = time.time()
                    if now - t0 >= 1.0:
                        self.fps = count / (now - t0)
                        count, t0 = 0, now
            except Exception as e:
                with self.lock:
                    self.error = str(e)
                time.sleep(0.5)

    def get_frame(self):
        with self.lock:
            return self.latest, self.frame_id, self.error

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=1.0)
        try:
            if self.handle is not None:
                self.video_service.unsubscribe(self.handle)
        except Exception:
            pass


def main():
    session = qi.Session()
    try:
        print(f"Connecting to NAO at {ROBOT_IP}:{ROBOT_PORT}...")
        session.connect(f"tcp://{ROBOT_IP}:{ROBOT_PORT}")
        print("Successfully connected to NAO!")
    except RuntimeError as e:
        print(f"Failed to connect to the robot at {ROBOT_IP}: {e}")
        print("Please try again")
        sys.exit(1)

    try:
        tts = session.service("ALTextToSpeech")
        motion_service = session.service("ALMotion")
        motion_service.setStiffnesses("Head", 1.0)
        posture_service = session.service("ALRobotPosture")
        leds_service = session.service("ALLeds")
        video_service = session.service("ALVideoDevice")
    except Exception as e:
        print(f"Failed to load services: {e}")
        sys.exit(1)

    def rest():
        motion_service.rest()

    def say(text):
        tts.say(text, _async=True)

    # ---------------- Cameras ----------------
    all_feeds = {
        "top": CameraFeed(video_service, CAM_TOP, "woz_gui_top"),
        "bottom": CameraFeed(video_service, CAM_BOTTOM, "woz_gui_bottom"),
    }
    feeds = {k: v for k, v in all_feeds.items() if k in ACTIVE_CAMERAS}
    labels = {}
    fps_labels = {}
    photos = {}
    last_ids = {k: -1 for k in feeds}

    def update_frames():
        for key, feed in feeds.items():
            frame, frame_id, error = feed.get_frame()
            if error and frame is None:
                labels[key].config(image="", text=f"Camera error: {error}")
            elif frame is not None and frame_id != last_ids[key]:
                w, h, data = frame
                photos[key] = ImageTk.PhotoImage(Image.frombytes("RGB", (w, h), data))
                labels[key].config(image=photos[key], text="")
                last_ids[key] = frame_id
            fps_labels[key].config(text=f"{feed.fps:.1f} FPS")
        root.after(GUI_REFRESH_MS, update_frames)

    def on_close():
        for feed in feeds.values():
            feed.stop()
        root.destroy()

    # ---------------- GUI ----------------
    root = tk.Tk()
    root.minsize(1000, 500)
    root.title("NAO WOZ GUI")
    root.protocol("WM_DELETE_WINDOW", on_close)

    # Talking panel (left)
    talking_frame = tk.Frame(root, width=100, height=200, borderwidth=1, relief="solid")
    talking_frame.pack(padx=5, pady=5, side="left", fill="both", expand=True)

    tk.Label(talking_frame, text="Talking").pack(padx=5, pady=5)

    introButton = tk.Button(
        talking_frame,
        text="Introduction",
        command=lambda: say("Hello my name is Nao"),
    )
    introButton.pack(padx=5, pady=5)

    input_row = tk.Frame(talking_frame)
    input_row.pack(padx=5, pady=5, fill="x")
    entry = tk.Entry(input_row)
    entry.insert(0, "Enter your text")
    entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
    submitButton = tk.Button(
        input_row,
        text="Speak",
        command=lambda: say(entry.get()),
    )
    submitButton.pack(side="left")

    # Camera panel (right)
    camera_frame = tk.Frame(root, borderwidth=1, relief="solid")
    camera_frame.pack(padx=5, pady=5, side="right", fill="both", expand=True)

    titles = {"top": "Top Camera", "bottom": "Bottom Camera"}
    for key in feeds:
        col = tk.Frame(camera_frame)
        col.pack(side="left", padx=5, pady=5, expand=True)
        tk.Label(col, text=titles[key]).pack()

        # Fixed-pixel holder so the image can't shrink the layout
        holder = tk.Frame(col, width=VIEW_W, height=VIEW_H, bg="black")
        holder.pack_propagate(False)
        holder.pack()
        labels[key] = tk.Label(holder, text="Connecting...", bg="black", fg="white")
        labels[key].pack(fill="both", expand=True)

        fps_labels[key] = tk.Label(col, text="0.0 FPS")
        fps_labels[key].pack()

    for feed in feeds.values():
        feed.start()
    update_frames()

    root.mainloop()


if __name__ == "__main__":
    main()