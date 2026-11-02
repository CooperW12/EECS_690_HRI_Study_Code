import tkinter as tk
import sys, time, os, qi


if len(sys.argv) > 1 and len(sys.argv) < 3: #ensures proper number of arguments
    ROBOT_IP = sys.argv[1]
    ROBOT_PORT = 9559
else:
    print("please provide proper number of arguments")
    print("Proper program usage: python3 name.py IP_ADDRESS_HERE")
    sys.exit(1)

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
        tts = session.service("ALTextToSpeech") #initialized text-to-speech service
        motion_service = session.service("ALMotion")
        motion_service.setStiffnesses("Head", 1.0)
        posture_service = session.service("ALRobotPosture")
        leds_service = session.service("ALLeds")
    except Exception as e:
        print(f"Failed to load services: {e}")
        sys.exit(1)

    def rest():
            motion_service.rest()

    def thinkingEyes():
        leds_service.on('FaceLeds')
        leds_service.randomEyes(2)
        leds_service.fadeRGB("FaceLeds", 0x000000FF, 0.5)

    def happyEyes():
        leds_service.on('FaceLeds')
        leds_service.fadeRGB("FaceLeds", 0x0000FF00, 0.5)
        time.sleep(2)
        leds_service.fadeRGB("FaceLeds", 0x000000FF, 0.5) 

    def say(text):
         tts.say(text)

    root = tk.Tk()
    root.minsize(1000,500)
    root.title("NAO WOZ GUI")

    talking_frame = tk.Frame(root, width=100, height=200, borderwidth=1, relief="solid")
    talking_frame.pack(padx=5, pady=5, side="left", fill="both", expand=True)

    tk.Label(
        talking_frame,
        text="Talking",
    ).pack(padx=5, pady=5)

    introButton = tk.Button(
        talking_frame,
        text = "Introduction",
        command = lambda: say("Hello my name is Nao"),
    )
    introButton.pack(padx=5, pady=5)

    goodOneButton = tk.Button(
        talking_frame,
        text = "Good thing #1",
        command = lambda: say("My first good thing is that I get to talk with someone today! Now, your turn!"),
    )
    goodOneButton.pack(padx=5, pady=5)

    conclusionButton = tk.Button(
        talking_frame,
        text = "Conclusion",
        command = lambda: say("Thanks for sharing 3 good things with me! Goodbye!"),
    )
    conclusionButton.pack(padx=5, pady=5)

    input_row = tk.Frame(talking_frame)
    input_row.pack(padx=5, pady=5, fill="x")
    entry = tk.Entry(input_row)
    entry.insert(0, "Enter your text")
    entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
    submitButton = tk.Button(
        input_row,
        text="Speak",
        command=lambda: say(entry.get())
    )
    submitButton.pack(side="left")

    eye_frame = tk.Frame(root, width=200, height=400, borderwidth=1, relief="solid")
    eye_frame.pack(padx=5, pady=5, side="left", fill="both", expand=True)

    tk.Label(
        eye_frame,
        text="Eyes",
    ).pack(padx=5, pady=5)

    thinkingEyesButton = tk.Button(
        eye_frame,
        text = "Thinking Eyes",
        command = thinkingEyes,
    )
    thinkingEyesButton.pack(padx=5, pady=5)

    happyEyesButton = tk.Button(
        eye_frame,
        text = "Happy Eyes",
        command = happyEyes,
    )
    happyEyesButton.pack(padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
    