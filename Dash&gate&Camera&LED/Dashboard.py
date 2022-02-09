import base64
import time
import tkinter as tk

import cv2
import cv2 as cv
import numpy as np
from PIL import ImageTk, Image
from tkinter import scrolledtext, font, W

import paho.mqtt.client as mqtt

master = tk.Tk()
client = mqtt.Client('Dashboard')
global_broker_address = "147.83.118.92"
global_broker_port = 1884


# treatment of messages received from gate through the global broker

def on_message(client, userdata, message):
    global panel
    global lbl
    if message.topic == "cameraControllerAnswer/videoFrame":
        img = base64.b64decode(message.payload)
        # converting into numpy array from buffer
        npimg = np.frombuffer(img, dtype=np.uint8)
        # Decode to Original Frame
        img = cv.imdecode(npimg, 1)
        cv.imshow("Stream", img)
        cv.waitKey(1)
    if message.topic == 'cameraControllerAnswer/picture':
        img = base64.b64decode(message.payload)
        # converting into numpy array from buffer
        npimg = np.frombuffer(img, dtype=np.uint8)
        # Decode to Original Frame
        cv2image = cv.imdecode(npimg, 1)
        dim = (300, 300)
        # resize image
        cv2image = cv.resize(cv2image, dim, interpolation=cv.INTER_AREA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        panel.imgtk = imgtk
        panel.configure(image=imgtk)

    if (message.topic == "autopilotControllerAnswer/droneAltitude"):
        answer = str(message.payload.decode("utf-8"))
        lbl['text'] = answer[:5]
    if (message.topic == "autopilotControllerAnswer/droneHeading"):
        answer = str(message.payload.decode("utf-8"))
        lbl['text'] = answer[:5]
    if (message.topic == "autopilotControllerAnswer/droneGroundSpeed"):
        answer = str(message.payload.decode("utf-8"))
        lbl['text'] = answer[:5]

    if (message.topic == "autopilotControllerAnswer/dronePosition"):
        positionStr = str(message.payload.decode("utf-8"))
        position = positionStr.split('*')
        latLbl['text'] = position[0]
        lonLbl['text'] = position[1]

client.on_message = on_message

# |--DASHBOARD master frame ----------------------------------------------------------------------------------|
# |                                                                                                           |
# |  |---connection frame--------------------------------------------------------------------------------|    |
# |  |---------------------------------------------------------------------------------------------------|    |
# |                                                                                                           |
# |  |---top frame---------------------------------------------------------------------------------------|    |
# |  |                                                                                                   |    |
# |  |   |--Autopilot control label frame ----------------------------|  |--LEDs control label frame--|  |    |
# |  |   |                                                            |  |                            |  |    |
# |  |   |  |--Arm/disarm frame -----------------------------------|  |  |----------------------------|  |    |
# |  |   |  |------------------------------------------------------|  |                                  |    |
# |  |   |                                                            |                                  |    |
# |  |   |  |--bottom frame ---------------------------------------|  |                                  |    |
# |  |   |  |                                                      |  |                                  |    |
# |  |   |  |  |-Autopilot get frame--|  |-Autopilot set frame -|  |  |                                  |    |
# |  |   |  |  |----------------------|  |----------------------|  |  |                                  |    |
# |  |   |  |                                                      |  |                                  |    |
# |  |   |  |------------------------------------------------------|  |                                  |    |
# |  |   |                                                            |                                  |    |
# |  |   |------------------------------------------------------------|                                  |    |
# |  |---------------------------------------------------------------------------------------------------|    |
# |                                                                                                           |
# |  |---camera control label frame----------------------------------------------------------------------|    |
# |  |                                                                                                   |    |
# |  |   |--- Take picture frame -----------|            |--- Video stream frame -----------|            |    |
# |  |   |                                  |            |                                  |            |    |
# |  |   |----------------------------------|            |----------------------------------|            |    |
# |  |---------------------------------------------------------------------------------------------------|    |
# |                                                                                                           |
# |-----------------------------------------------------------------------------------------------------------|



# Connection frame ----------------------
connected = False
connectionFrame = tk.Frame (master)
connectionFrame.pack(fill = tk.X)

def connectionButtonClicked():
    global connected
    global client
    if not connected:
        print ('Connect with drone platform')
        connectionButton['text'] = "Disconnect"
        connectionButton['bg'] = "green"
        connected = True

        client.connect(global_broker_address, global_broker_port)
        client.publish("connectPlatform")
        client.loop_start()
        client.subscribe("#")
        print('Connected with drone platform')

        topFrame.pack(fill=tk.X)
        cameraControlFrame.pack(padx=20, pady=20);

    else:
        print('Disconnect')
        connectionButton['text'] = "Connect with drone platform"
        connectionButton['bg'] = "red"
        connected = False
        topFrame.pack_forget()
        ledsControlFrame.pack_forget()
        cameraControlFrame.pack_forget()

connectionButton = tk.Button(connectionFrame, text="Connect with drone platform", width = 100, bg='red', fg="white", command=connectionButtonClicked)
connectionButton.grid(row = 0, column = 0, padx=60, pady=20)


# top frame -------------------------------------------
topFrame = tk.Frame (master)


# Autopilot control label frame ----------------------
autopilotControlFrame = tk.LabelFrame(topFrame, text="Autopilot control", padx=5, pady=5)
autopilotControlFrame.pack(padx=20, side = tk.LEFT);

# Arm/disarm frame ----------------------
armDisarmFrame = tk.Frame (autopilotControlFrame)
armDisarmFrame.pack(padx=20)

armed = False
def armDisarmButtonClicked():
    global armed

    if not armed:
            armDisarmButton['text'] = "Disarm drone"
            armDisarmButton['bg'] = "green"
            armed = True
            client.publish("autopilotControllerCommand/armDrone")

    else:
            armDisarmButton['text'] = "Arm drone"
            armDisarmButton['bg'] = "red"
            armed = False
            client.publish("autopilotControllerCommand/disarmDrone")



armDisarmButton = tk.Button(armDisarmFrame, text="Arm drone", bg='red', fg="white",  width = 90, command=armDisarmButtonClicked)
armDisarmButton.grid(column=0, row=0,  pady = 5)

# bottomFrame frame ----------------------
bottomFrame = tk.Frame (autopilotControlFrame)
bottomFrame.pack(padx=20)

# Autopilot get frame ----------------------
autopilotGet = tk.Frame (bottomFrame)
autopilotGet.pack(side = tk.LEFT, padx=20)

v1 = tk.StringVar()
s1r1= tk.Radiobutton(autopilotGet,text="Altitude", variable=v1, value=1).grid(column=0, row=0, columnspan = 5, sticky=tk.W)
s1r2= tk.Radiobutton(autopilotGet,text="Heading", variable=v1, value=2).grid(column=0, row=1, columnspan = 5, sticky=tk.W)
s1r3= tk.Radiobutton(autopilotGet,text="Ground Speed", variable=v1, value=3).grid(column=0, row=2, columnspan = 5, sticky=tk.W)
v1.set(1)

def autopilotGetButtonClicked():
    if v1.get() == "1":
        client.publish("autopilotControllerCommand/getDroneAltitude")
    elif v1.get() == "2":
        client.publish("autopilotControllerCommand/getDroneHeading")
    else:
        client.publish("autopilotControllerCommand/getDroneGroundSpeed")

autopilotGetButton = tk.Button(autopilotGet, text="Get", bg='red', fg="white", width = 10, height=5, command=autopilotGetButtonClicked)
autopilotGetButton.grid(column=5, row=0, columnspan=2, rowspan = 3, padx=10)

lbl = tk.Label(autopilotGet, text=" ", width = 10, borderwidth=2, relief="sunken")
lbl.grid(column=7, row=1,  columnspan=2 )

# Autopilot set frame ----------------------
autopilotSet = tk.Frame (bottomFrame)
autopilotSet.pack( padx=20)



def takeOffButtonClicked():
    client.publish("autopilotControllerCommand/takeOff", metersEntry.get() )

takeOffButton = tk.Button(autopilotSet, text="Take Off", bg='red', fg="white",  width = 10, command=takeOffButtonClicked)
takeOffButton.grid(column=0, row=1, columnspan=2, sticky=tk.W)

to = tk.Label(autopilotSet, text="to")
to.grid(column=2, row=1)
metersEntry = tk.Entry(autopilotSet, width = 10)
metersEntry.grid(column=3, row=1,  columnspan=2 )
meters = tk.Label(autopilotSet, text="meters")
meters.grid(column=5, row=1)



lat = tk.Label(autopilotSet, text="lat")
lat.grid(column=2, row=2,  columnspan=2,padx = 5 )

lon = tk.Label(autopilotSet, text="lon")
lon.grid(column=4, row=2,  columnspan=2,padx = 5 )

def getPositionButtonClicked():
    client.publish("autopilotControllerCommand/getDronePosition" )


getPositionButton = tk.Button(autopilotSet, text="Get Position", bg='red', fg="white",  width = 10,  command=getPositionButtonClicked)
getPositionButton.grid(column=0, row=3, pady = 5, sticky=tk.W)

latLbl = tk.Label(autopilotSet, text=" ", width = 10, borderwidth=2, relief="sunken")
latLbl.grid(column=2, row=3,  columnspan=2,padx = 5 )

lonLbl = tk.Label(autopilotSet, text=" ", width = 10, borderwidth=2, relief="sunken")
lonLbl.grid(column=4, row=3,  columnspan=2,padx = 5 )

def goToButtonClicked():
    position = str (goTolatEntry.get()) + '*' + str(goTolonEntry.get())
    client.publish("autopilotControllerCommand/goToPosition", position)



goToButton = tk.Button(autopilotSet, text="Go To", bg='red', fg="white",  width = 10,  command=goToButtonClicked)
goToButton.grid(column=0, row=4, pady = 5, sticky=tk.W)

goTolatEntry = tk.Entry(autopilotSet, width = 10)
goTolatEntry.grid(column=2, row=4,  columnspan=2,padx = 5 )

goTolonEntry = tk.Entry(autopilotSet, width = 10)
goTolonEntry.grid(column=4, row=4,  columnspan=2,padx = 5 )

def returnToLaunchButtonClicked():
    client.publish("autopilotControllerCommand/returnToLaunch")




returnToLaunchButton = tk.Button(autopilotSet, text="Return To Launch", bg='red', fg="white",  width = 40, command=returnToLaunchButtonClicked)
returnToLaunchButton.grid(column=0, row=5,  pady = 5, columnspan=6, sticky=tk.W)


# LEDs control frame ----------------------
ledsControlFrame = tk.LabelFrame(topFrame, text="LEDs control", padx=5, pady=5)
ledsControlFrame.pack(padx=20, pady=20);

v3 = tk.StringVar()
s1r7= tk.Radiobutton(ledsControlFrame,text="LED sequence START/STOP", variable=v3, value=1).grid(column=2, row=2, columnspan = 3)
s1r8= tk.Radiobutton(ledsControlFrame,text="LED sequence for N seconds", variable=v3, value=2).grid(column=2, row=3, columnspan = 3)

seconds = tk.Entry(ledsControlFrame, width = 5)
seconds.grid(column=5, row=3, columnspan = 3)
v3.set(1)

lEDSequence = False;

def LEDControlButtonClicked():
    global E1
    global lEDSequence
    if v3.get() == "1":
        if not lEDSequence:
            ledControlButton['text'] = "Stop"
            ledControlButton['bg'] = "green"
            lEDSequence = True
            client.publish("LEDsControllerCommand/startLEDsSequence")

        else:
            ledControlButton['text'] = "Start"
            ledControlButton['bg'] = "red"
            lEDSequence = False
            client.publish("LEDsControllerCommand/stopLEDsSequence")

    if v3.get() == "2":
            client.publish("LEDsControllerCommand/LEDsSequenceForNSeconds", seconds.get())


ledControlButton = tk.Button(ledsControlFrame, text="Start", bg='red', fg="white",  width = 10, height = 3, command=LEDControlButtonClicked)
ledControlButton.grid(column=8, row=1,  padx = 5, columnspan=4, rowspan = 3)



# Camera control label frame ----------------------
cameraControlFrame = tk.LabelFrame(master, text="Camera control", padx=5, pady=5)


takePictureFrame = tk.Frame (cameraControlFrame)
takePictureFrame.pack(side = tk.LEFT)

def takePictureButtonClicked():
    print ("Take picture")
    client.publish("cameraControllerCommand/takePicture")

takePictureButton = tk.Button(takePictureFrame, text="Take Picture", width=50, bg='red', fg="white", command=takePictureButtonClicked)
takePictureButton.grid(column=0, row=0, pady = 20, padx = 20)

img = Image.open("image1.jpg")
img = img.resize((350, 350), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
panel = tk.Label(takePictureFrame, image=img, borderwidth=2, relief="raised")
panel.image = img
panel.grid(column=0, row=1, columnspan=3, rowspan = 3)




videoStreamFrame = tk.Frame(cameraControlFrame)
videoStreamFrame.pack()

videoStream = False;

def videoStreamButtonClicked():
    global videoStream
    global client
    if not videoStream:
        videoStreamButton['text'] = "Stop video stream"
        videoStreamButton['bg'] = "green"
        videoStream = True
        client.publish("cameraControllerCommand/startVideoStream")

    else:
        videoStreamButton['text'] = "Start video stream on a separaded window"
        videoStreamButton['bg'] = "red"
        videoStream = False
        client.publish("cameraControllerCommand/stopVideoStream")

        cv.destroyWindow("Stream")



videoStreamButton = tk.Button(videoStreamFrame, text="Start video stream \n on a separaded window", width=50, height = 25, bg='red', fg="white",
                              command=videoStreamButtonClicked)
myFont = font.Font(size=12)
videoStreamButton['font'] = myFont
videoStreamButton.grid(column=0, row=0, pady=20, padx=20, )



master.mainloop()