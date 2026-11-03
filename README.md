# EECS_690_HRI_Study_Code

## Description


A Wizard-of-Oz (WOZ) control panel for the NAO humanoid robot, built with Python and Tkinter. An operator uses the GUI to control NAO remotely while watching what the robot sees.


Features:
- **Text-to-speech:**
- **Live dual camera feeds:**


## Requirements


- Python 3.8+
- A NAO robot on the same network (NAOqi listening on port 9559)
- Python packages:


```bash
pip install numpy pillow qi
```


Tkinter ships with most Python installs. On Ubuntu/Debian, install it with `sudo apt install python3-tk`.


## How to Run


1. Power on NAO and get its IP
2. From the project folder, run:


```bash
python3 nao_woz_gui.py NAO_IP_ADDRESS
```


4. Use the GUI:
  - Click **Introduction** for NAO to introduce itself.
  - Type a message and click **Speak** to have NAO say it.


## Demo Video
