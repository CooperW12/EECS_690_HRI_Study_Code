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

    def standUp():
            posture_service.goToPosture("StandInit", 0.5)

    def rest():
            motion_service.rest()

    def nod():
        motion_service.setStiffnesses("Head", 1.0)
        motion_service.setAngles("HeadPitch", .4, .4)
        time.sleep(.5)
        motion_service.setAngles("HeadPitch", -.2, .4)
        time.sleep(.5)
        motion_service.setAngles("HeadPitch", .4, .4)
        time.sleep(.5)
        motion_service.setAngles("HeadPitch", 0, .4)
        time.sleep(.5)
        motion_service.setStiffnesses("Head", 0.0)

    def thinkingEyes():
        leds_service.on('FaceLeds')
        leds_service.randomEyes(2)
        leds_service.fadeRGB("FaceLeds", 0x000000FF, 0.5)

    def happyEyes():
        leds_service.on('FaceLeds')
        leds_service.fadeRGB("FaceLeds", 0x0000FF00, 0.5)
        time.sleep(2)
        leds_service.fadeRGB("FaceLeds", 0x000000FF, 0.5)

    def greetStanding():
        motion_service.setStiffnesses("RArm", 0.5)
        motion_service.setAngles("RShoulderRoll", -1, .3)
        motion_service.setAngles("RShoulderPitch", -1, .3)
        time.sleep(2.0)
        motion_service.setAngles("RShoulderRoll", 0, .3)
        motion_service.setAngles("RShoulderPitch", 0, .3)
        time.sleep(2.0)
        motion_service.setStiffnesses("RArm", 1.0)
        

    def sayCustom(text):
        tts.say(text.widget.get()) 

    def say(text):
         tts.say(text)

    root = tk.Tk()
    root.minsize(1000,500)
    root.title("Lab 2 NAO WOZ GUI")

    talking_frame = tk.Frame(root, width=100, height=200, borderwidth=1, relief="solid")
    talking_frame.pack(padx=5, pady=5, side="left", fill="both", expand=True)

    tk.Label(
        talking_frame,
        text="Talking",
    ).pack(padx=5, pady=5)

    introButton = tk.Button(
        talking_frame,
        text = "Introduction",
        command = lambda: say("Hello my name is Nao, lets take turns sharing 3 good things that happened to us today."),
    )
    introButton.pack(padx=5, pady=5)

    goodOneButton = tk.Button(
        talking_frame,
        text = "Good thing #1",
        command = lambda: say("My first good thing is that I get to talk with someone today! Now, your turn!"),
    )
    goodOneButton.pack(padx=5, pady=5)

    goodTwoButton = tk.Button(
        talking_frame,
        text = "Good thing #2",
        command = lambda: say("My second good thing is that my motors aren't overheatting!"),
    )
    goodTwoButton.pack(padx=5, pady=5)
    
    goodThreeButton = tk.Button(
        talking_frame,
        text = "Good thing #3",
        command = lambda: say("My last good thing is that it is almost the weekend!"),
    )
    goodThreeButton.pack(padx=5, pady=5)

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

    motion_frame = tk.Frame(root, width=200, height=400, borderwidth=1, relief="solid")
    motion_frame.pack(padx=5, pady=5, side="left", fill="both", expand=True)

    tk.Label(
        motion_frame,
        text="Moving",
    ).pack(padx=5, pady=5)
    standButton = tk.Button(
        motion_frame,
        text = "Stand Up",
        command = standUp,
    )
    standButton.pack(padx=5, pady=5)

    restButton = tk.Button(
        motion_frame,
        text = "Rest",
        command = rest,
    )
    restButton.pack(padx=5, pady=5)

    nodButton = tk.Button(
        motion_frame,
        text = "Nod",
        command = nod,
    )
    nodButton.pack(padx=5, pady=5)

    greetStandingButton = tk.Button(
        motion_frame,
        text = "Greet (Standing)",
        command = greetStanding,
    )
    greetStandingButton.pack(padx=5, pady=5)

    thinkingEyesButton = tk.Button(
        motion_frame,
        text = "Thinking Eyes",
        command = thinkingEyes,
    )
    thinkingEyesButton.pack(padx=5, pady=5)

    happyEyesButton = tk.Button(
        motion_frame,
        text = "Happy Eyes",
        command = happyEyes,
    )
    happyEyesButton.pack(padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
    