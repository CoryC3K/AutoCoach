#!/usr/bin/env python3

# Dependancies include: matplotlib, pyserial, pynmea2
# 2/26/18

import matplotlib
matplotlib.use('TkAgg')

import pylab, csv, serial, time, threading, pynmea2, os, math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm                          # Color Map

#from pylab import *
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename, asksaveasfile, askdirectory
from datetime import datetime, date

Cone_File    = ""                                               # Default cone file, for testing
Output_File  = ""
Lap_Names    = []                                               # Create lap names list
Directory    = os.getcwd()                                  # Gets current directory for default dir name
GPS_Time_Ref = 0                                            # Sets GPS reference time for TPS logging
Ext_High_Lat    = 100.0
Ext_Low_Lat     = 0.1
Ext_High_Lon    = 100.
Ext_Low_Lon = 0.1
Lat_Lon_Ratio   = 1.33333

fig_size     = [.1,.1]                                              # Graph Drawing Stuff
TheGraphFigure = Figure(figsize=fig_size, dpi=100, linewidth=0 )
TheGraphFigure.set_facecolor('#6a6e09')
plot = TheGraphFigure.add_axes([0,0,1,1])   # Makes graph match frame size

TheSpeedFigure = Figure(figsize=fig_size, dpi=100, linewidth=0)
SpeedPlot= TheSpeedFigure.add_axes([0,0,1,1])


class Application(Frame):                                   # Main window Tkinter setup
    def __init__(self, master=None):

        Frame.__init__(self, master)
        self.grid()
        self.master.title("Cory's Data Analyzer")

        style = ttk.Style()                                     # We like TTK because themes make it look better-er
        #print(style.theme_names())
        """if sys.platform.startswith('win'):
            #style.theme_use('vista')                            # If we're on Sindows, Vista looks way better.
            File_Slashes = "\\"
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            style.theme_use('clam')                         # Vista doesn't work on Linux, so use clam
            File_Slashes = "/"
        elif sys.platform.startswith('darwin'):
            style.theme_use('clam')"""
            
        
        style.configure("red.TFrame", background='red')
        style.configure("green.TFrame", background='green')
        style.configure("yellow.TFrame", background='yellow')

        # Configure Main App window into 2 columns

        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(1, weight=0)
        self.master.columnconfigure(2, weight=1)

        self.FrameLeft = ttk.Frame(master)
        self.FrameRight = ttk.Frame(master)
        self.FrameLeft.grid(row=1, column=1, sticky=N+S)
        self.FrameRight.grid(row=1, column=2, sticky=N+S+E+W)

        #Left Column Stuff

        self.Frame1 = ttk.LabelFrame(self.FrameLeft, text=" Laps          ", )
        self.Frame1.pack(side=TOP, expand=TRUE, fill=BOTH)

        # Right Column Stuff
        nb = ttk.Notebook(self.FrameRight)          # Define nb as notebook doober
        nb.pack(expand=TRUE, fill=BOTH)

        self.NBook1 = ttk.Frame(nb)                     # Define some tabs
        self.NBook1b = ttk.Frame(self.NBook1)   # Create frame inside tab for graph clearing
        self.NBook2 = ttk.Frame(nb)
        self.NBook2b = ttk.Frame(self.NBook2)
        self.NBook3 = ttk.Frame(nb)
        self.NBook4 = ttk.Frame(nb, style='yellow.TFrame')
        self.NBook4b = ttk.Frame(self.NBook4, style='green.TFrame')
        
        

        nb.add(self.NBook1, text = " Map "          )
        nb.add(self.NBook2, text = " Times "        )
        nb.add(self.NBook3, text = " Gyro " )
        nb.add(self.NBook4, text = " TPS and Speed "   )

        self.Frame2 = Frame(self.FrameRight)        # for menu buttons
        self.Frame2.pack(side=BOTTOM, fill=X)


        # Create some buttons, define what they do

        self.b4 = ttk.Button(self.Frame2,  text="Load Course", command=btnLoadCourse)
        self.b5 = ttk.Button(self.Frame2,  text="Load Run Folder",   command=btnLoadRuns)
        self.b6 = ttk.Button(self.Frame2,  text="Exit",        command=btnExit)
        self.b7 = ttk.Button(self.Frame2,  text="Clear",       command=Clear_Button)
        
        self.b7.pack(side=LEFT,  expand=TRUE, fill=X)
        self.b6.pack(side=RIGHT,  expand=TRUE, fill=X)
        self.b5.pack(side=RIGHT,  expand=TRUE, fill=X)
        self.b4.pack(side=RIGHT,  expand=TRUE, fill=X)
        self.NBook4b.pack(fill=BOTH, expand=TRUE)


                                    # Listbox for Lap names
        self.listbox = Listbox(self.Frame1, selectmode=MULTIPLE)
        self.listbox.pack(expand=TRUE, fill=BOTH)

        self.listbox2 = Listbox(self.NBook2)
        self.listbox2.pack(expand=TRUE, fill=BOTH)

#### End of INIT ####





#### Start of Buttons ####


def btnLoadCourse(*ReDraw):
    global Cone_File
    fname = ""
    if bool(ReDraw) == True:                            # if the course is already loaded, we're loading a run instead
        Graph_It(Cone_File, fname, 1)                   #   or we're loading multple runs because user selected more than one
        return                                                      #   Mostly this avoids askopenfilename() because we write runs on top of the *old* Cone_File graph
    plot.clear()
    #Cone_File = askopenfilename()                      # Opens the "Open File" dialog, puts result into Cone_File
    Cone_File = 'C:/Users/coryc.cginow/Google Drive/Bundy Hill/Map.csv'
    #print(str(Cone_File))
    try:
        Graph_It(Cone_File, fname, 1)
    except:
        Cone_File = askopenfilename()
        Graph_It(Cone_File, fname, 1)



def btnLoadRuns():
    global Directory, Cone_File

    runfolder = askdirectory()                         # ask the user which directory
    #print(str(runfolder))
    #runfolder = 'C:/Users/coryc.cginow/Google Drive/Bundy Hill'
    Directory = os.fsencode(runfolder)              # encode it with whatever the os uses
    for file in os.listdir(Directory):                      # for each file:
        Filename = os.fsdecode(file)                    # decode the system path addres
        if Filename.endswith(".csv"):                       # If it's a CSV
            Lap_Names.append(Filename)              # add it to the Lap_Names list
    app.listbox.insert(1, *Lap_Names)                   # Fills the updated listbox
    app.listbox.bind('<<ListboxSelect>>', onselect) # Bind the list, so that when you click it, it launches onselect()


def btnExit():
    root.destroy()                                              # And then kill it all
    time.sleep(5.5)
    raise SystemExit

def onselect(event):                                            # This is for clicking the listbox, and selecting certain runs
    global Directory, prevIndexCnt, Cone_File   # Holds the directory of the run folder

    w = event.widget

    try:                                # Defines prevIndexCnt for first run
        prevIndexCnt
    except NameError:
        prevIndexCnt = 0

    indexCnt = len(w.curselection())    # How many items are currently selected?
    if indexCnt < prevIndexCnt:         # If we used to have more items, clear the old graph
        plot.clear()
        try:
            SpeedPlot.clear()
        except:
            pass
        if Cone_File != "NONE":
            fname = ""
            Graph_It(Cone_File, fname, 1)
        prevIndexCnt = indexCnt

    else:
        prevIndexCnt = len(w.curselection()) # Store number of items for the next time around

    app.listbox2.delete(0, END)
    plot.clear()

    try:
        app.NBook4b.destroy()                   # Clears the graph
    except:
        pass
    app.NBook4b = ttk.Frame(app.NBook4)         # Then re-draws it
    app.NBook4b.pack( in_=app.NBook4, fill=BOTH, expand=TRUE)

    for lsNum in w.curselection()[0:]:  # Iterates through multiple selections in list
        
        index = int(lsNum)              # Gets the list Number of what was clicked
        value = (w.get(index)).encode('utf-8')  # Gets the label (text) from the list number
        fname = value
        btnLoadCourse(True)             # Re-draw cone course, it's True that we're re-drawing it
        try:
            Directory = Directory.encode('utf-8')
        except AttributeError:
            pass
        value = os.path.join(Directory, value)  # Make sure the full filepath is present
        if Cone_File == "NONE":         # If we don't select a Cone_File, map it anyway, use points for extents
            print("Oh shit boy you dun fucked up")
            break
        else:
            Graph_It(value, fname)             # Draw run file

    canvas2 = FigureCanvasTkAgg(TheSpeedFigure, app.master)
    canvas2.show()
    canvas2.get_tk_widget().pack( in_=app.NBook4b, expand=TRUE, fill=BOTH)
    #app.NBook4b.pack(in_ = app.NBook4, expand=TRUE, fill=BOTH)

    
#### End of Buttons!!!! ####




#### Meat 'n Taters ####

def Graph_It(Cone_File, fname, *Set_Extents):
    global Ext_High_Lat, Ext_Low_Lat, Ext_High_Lon, Ext_Low_Lon, Lat_Lon_Ratio, Times
    global SF_Cone_Y, SF_Cone_X

    if Cone_File == "NONE":                     # If we haven't selected a Cone_File
        return                                  # then don't graph anything!
    if Cone_File == "":                         # If user hits cancel, don't do anything
        return

    file = open(Cone_File)
    CSV_Data = csv.reader(file, quoting=csv.QUOTE_NONE)
    file.seek(0)                                # Start at the beginning of the file

    Lat_C_List = []
    Lon_C_List = []
    C_List_Y = []
    C_List_X = []
    SF_Cone_Lat = []
    SF_Cone_Lon = []
    Times = []
    Speeds = []
    StartStopCount = 0
    Row_Str = ""

    try:                                        # Defines lists for first run, because we dont want to over-write them later
        SF_Cone_Y
    except NameError:
        SF_Cone_Y = []
        SF_Cone_X = []

    for row in CSV_Data:                        # Build lists of latitude/Longitude
        if not ''.join(row).strip():            # If we get to an empty line, don't error out
            break

        if row[0] == 'StopStart':               # Start/Stop cone row
            Row_Str = pynmea2.RMC('GP', 'RMC', (row[2:13]))             # Converts row list to sentance
            Cone_GPS_Sent = pynmea2.parse(str(Row_Str), check=False)    # Uses Pynmea2 to parse GPRMC sentance
            StartStopCount = StartStopCount + 1                         # Counts how many start/stop cones we have (should only be 4)
            SF_Cone_Lat.append(-360*(90-Cone_GPS_Sent.latitude)/180)
            Lat_C_List.append(-360*(90-Cone_GPS_Sent.latitude)/180)     # For graph scaling
            SF_Cone_Lon.append(480*(180+Cone_GPS_Sent.longitude)/360)
            Lon_C_List.append(480*(180+Cone_GPS_Sent.longitude)/360)

        else:                                   # Actual GPS Coords run or cone row
            Row_Str = pynmea2.RMC('GP', 'RMC', (row[1:12]))             # Converts row list to sentance
            Cone_GPS_Sent = pynmea2.parse(str(Row_Str), check=False)    # Uses Pynmea2 to parse GPRMC sentance

        latC = Cone_GPS_Sent.latitude           # Loads latitude csv vals into variable
        lonC = Cone_GPS_Sent.longitude          # Loads longitude csv vals into variable
        laty = -(360*(90-latC)/180)             # Does math to make them look right
        lonx = 480*(180+lonC)/360
        Lat_C_List.append(laty)                 # Loads computed value into list
        Lon_C_List.append(lonx)

        Times.append(Cone_GPS_Sent.timestamp)   # Loads times into list for timing later
        Speeds.append(int(Cone_GPS_Sent.spd_over_grnd*100))


    # We need the extents for future graphing, but don't want to reset them if it's not a Cone_File
    if bool(Set_Extents) == True:
        Ext_High_Lat  = max(Lat_C_List)
        Ext_Low_Lat = min(Lat_C_List)
        Ext_High_Lon  = max(Lon_C_List)
        Ext_Low_Lon = min(Lon_C_List)
                                    # We need the ratio between corrected lat and corrected long for graphing to look right
        try:
            Lat_Lon_Ratio = (Ext_High_Lat-Ext_Low_Lat)/(Ext_High_Lon-Ext_Low_Lon)
        except Exception as ex:
            print(ex)
            Lat_Lon_Ratio = 1

        plot.axis('image')                      #Sets the scaling
        plot.set_xlim(-3, 103/Lat_Lon_Ratio)    #Sets plot scale limits
        plot.set_ylim(-3, 103)
        plot.axis('off')

        app.NBook1b.destroy()                   # Clears the graph
        app.NBook1b = Frame(app.NBook1)         # Then re-draws it
        canvas = FigureCanvasTkAgg(TheGraphFigure, app.master)
        canvas.get_tk_widget().pack( in_=app.NBook1b, expand=TRUE, fill=BOTH)
        app.NBook1b.pack(in_ = app.NBook1, expand=TRUE, fill=BOTH)


    i=int(0)
    imax = len(Lat_C_List)

    while i < imax:                             #Converts lat/lon to percent 0-100 for reasons
        C_List_Y.append(Value_Map(Lat_C_List[i], Ext_Low_Lat, Ext_High_Lat, 0, 100))
        C_List_X.append(Value_Map(Lon_C_List[i], Ext_Low_Lon, Ext_High_Lon, 0, 100/Lat_Lon_Ratio))
        if i < StartStopCount:
            SF_Cone_Y.append(Value_Map(SF_Cone_Lat[i], Ext_Low_Lat, Ext_High_Lat, 0, 100))
            SF_Cone_X.append(Value_Map(SF_Cone_Lon[i], Ext_Low_Lon, Ext_High_Lon, 0, 100/Lat_Lon_Ratio))
        i = i+1

    if bool(Set_Extents) == True:
        plot.scatter(C_List_X, C_List_Y, c='orange', marker='^', s=2)       #Plot the orange cones!
    else:
        plot.scatter(C_List_X, C_List_Y, c=Speeds, cmap=cm.plasma, marker=',', s=1, zorder=10)  # Plot the run line!
        plot.plot(C_List_X, C_List_Y, zorder=1) # Can't do color changing line. :( 
        Timing(SF_Cone_Y, SF_Cone_X, C_List_X, C_List_Y, Times, fname) #After drawing, pass the runfile on to timing, with start/stop locations
        Speed_Graph(Speeds, Times)

    if StartStopCount > 0:
        plot.scatter(SF_Cone_X, SF_Cone_Y, c='red', marker='^', s=10)                       # Plot start/stop cones
        plot.plot(SF_Cone_X[0:2], SF_Cone_Y[0:2], color='k', linestyle='-', linewidth=1)    # Start line
        plot.plot(SF_Cone_X[2:4], SF_Cone_Y[2:4], color='k', linestyle='-', linewidth=1)    # Stop line


def Timing(SF_Y, SF_X, Run_X, Run_Y, Times, fname):        # This handles doing the timing, decinding which points are at st/fin, etc.
    global Start_Time, Finish_Time
    Start_Dist = []
    Finish_Dist = []
    Start_Chopped_Run = []
    Finish_Chopped_Run = []

    if SF_Y == [] or SF_X == []:                    # If we don't have a cone file with start/fin, then don't do timing
        return

    # First we cut down the list of possible points to only the ones near the cones...
    # Think of drawing 2 circles the radius of the start line around the start cones, we only want points from in those circles.

    Start_Line_Distance = math.hypot(SF_X[1] - SF_X[0], SF_Y[1] - SF_Y[0])        # Distance of start line, used for excluing points too far away
    Finish_Line_Distance = math.hypot(SF_X[3] - SF_X[2], SF_Y[3] - SF_Y[2])        # Distance of finish line, used for excluing points too far away

    for i in range(len(Run_Y)):
        Start_Line_DistancePt = math.hypot(Run_X[i] - SF_X[0], Run_Y[i] - SF_Y[0])    # Distance of point from the Start cones
        Start_Line_DistancePt2 = math.hypot(Run_X[i] - SF_X[1], Run_Y[i] - SF_Y[1])   # Distance from the other cone
        if Start_Line_DistancePt > Start_Line_Distance and Start_Line_DistancePt2 > Start_Line_Distance:    # If the cone is further from a cone than the other start cone, pass on it
            continue
        else:
            Start_Chopped_Run.append([Run_X[i], Run_Y[i], Times[i]])       # Add cones to list of near cones

    for i in range(len(Run_Y)):
        Finish_Line_DistancePt = math.hypot(Run_X[i]-SF_X[2], Run_Y[i] - SF_Y[2])  # Distance of point from one of the Finish cones
        Finish_Line_DistancePt2 = math.hypot(Run_X[i]-SF_X[3], Run_Y[i] - SF_Y[3]) # Distance from the other cone
        if Finish_Line_DistancePt > Finish_Line_Distance and Finish_Line_DistancePt2 > Finish_Line_Distance:    # If the cone is further from the cone than the other start cone, pass on it
            continue
        else:
            Finish_Chopped_Run.append([Run_X[i], Run_Y[i], Times[i]])         # Add cones to list of near cones

    # Now we do math on the shortened list to figure out which points are closest to the cones

    sDen = math.sqrt((SF_Y[1]-SF_Y[0])**2 + (SF_X[1]-SF_X[0])**2)       #Start Denominator
    fDen = math.sqrt((SF_Y[3]-SF_Y[2])**2 + (SF_X[3]-SF_X[2])**2)       #Finish Denominator

    for i in range(len(Start_Chopped_Run)):                             # Iterate over choprun list of lists, and find the distances to the start or finish line
        #print("Str: " + str(Start_Chopped_Run[i]))
        sNum  = abs(((SF_Y[1]-SF_Y[0])*Start_Chopped_Run[i][0]) - ((SF_X[1]-SF_X[0])*Start_Chopped_Run[i][1]) + (SF_X[1]*SF_Y[0]) - (SF_Y[1]*SF_X[0]))
        Start_Dist.append(sNum/sDen)

    for i in range(len(Finish_Chopped_Run)):
        #print("Fin: " + str(Finish_Chopped_Run[i]))
        fNum = abs(((SF_Y[3]-SF_Y[2])*Finish_Chopped_Run[i][0]) - ((SF_X[3]-SF_X[2])*Finish_Chopped_Run[i][1]) + (SF_X[3]*SF_Y[2]) - (SF_Y[3]*SF_X[2]))
        Finish_Dist.append(fNum/fDen)

    Start_Index  = Start_Dist.index(min(Start_Dist))                    # Find the numbers associated with the indexes
    Start_Index2 = Start_Dist.index(min2(Start_Dist))                   # sorted by the minimum distance from the id'd cone
    Finish_Index  = Finish_Dist.index(min(Finish_Dist))
    Finish_Index2 = Finish_Dist.index(min2(Finish_Dist))

    plot.scatter(Start_Chopped_Run[Start_Index][0], Start_Chopped_Run[Start_Index][1], c='black', marker='.', s=100)
    plot.scatter(Start_Chopped_Run[Start_Index2][0], Start_Chopped_Run[Start_Index2][1], c='black', marker='.', s=100)

    plot.scatter(Finish_Chopped_Run[Finish_Index][0], Finish_Chopped_Run[Finish_Index][1], c='yellow', marker='.', s=100)
    plot.scatter(Finish_Chopped_Run[Finish_Index2][0], Finish_Chopped_Run[Finish_Index2][1], c='yellow', marker='.', s=100)

    #print("The time of Start is: " + str(Start_Chopped_Run[Start_Index][2]))
    #print("The time of Finish is: " + str(Finish_Chopped_Run[Finish_Index2][2]))

    time1 = datetime.combine(date.today(), Start_Chopped_Run[Start_Index][2])       # Uses the indexes to find the times from the orignal list
    time2 = datetime.combine(date.today(), Finish_Chopped_Run[Finish_Index2][2])    # index 2 is the times in the arrays: X,Y,Times
    time3 = time2 - time1                                   # Creates datetime.timedelta object to represent your lap time
    Start_Time = time1
    Finish_Time = time2
    #print("Run Length: " + str(time3))

    lap_descrptior = fname.decode('utf-8') + "     Time: " + str(time3.total_seconds())
    app.listbox2.insert(END, lap_descrptior )       # Prints the # of seconds per lap to the times tab.
    time3 = ""                                                  # Clears the list for the next runaround


def Speed_Graph(Speeds, Times):
    global Start_Time, Finish_Time

    Deltas = []

    for i in range(len(Times)):
        x = (datetime.combine(date.today(), Times[i])) - Start_Time
        Deltas.append(x.total_seconds())

    for i in range(len(Speeds)):
        Speeds[i] = Speeds[i]/100
        
    try:
        #SpeedPlot.axis('image')                      #Sets the scaling
        SpeedPlot.plot(Deltas, Speeds, linestyle='-', linewidth=1)
        
        
    except Exception as e:
        print(e)

def Clear_Button():
    SpeedPlot.set_xlim(-10,max(Deltas))
    app.NBook4.destroy()                                   # Clears the graph
    app.NBook4 = Frame(app.NBook4)         # Then re-draws it
    app.NBook4.pack(in_ = app.NBook4, expand=TRUE, fill=BOTH)
    canvas4 = FigureCanvasTkAgg(Speed_Graph, app.master)
    canvas4.show()
    canvas4.get_tk_widget().pack(in_=app.NBook4, side=tk.BOTTOM, fill=tk.BOTH, expand=TRUE)




#### End of Meat 'n Taters ####



def min2(Number_List):                                  # Used to find second smallest number in a list, for start/finish line timing
    low1, low2 = float('inf'), float('inf')
    for x in Number_List:
        if x <= low1:
            low1, low2 = x, low1
        elif x < low2:
            low2 = x
    return low2

def Value_Map(value, fLow, fHigh, toLow, toHigh):       #pretty much the map() function in arduino, used 4 times so far
    return toLow + (toHigh - toLow) * ((value - fLow) / (fHigh - fLow))

#### End Little Tools ####



if __name__ == "__main__":
    root = Tk()
    app = Application(master=root)
    root.minsize(width=800, height=600)
    root.protocol("WM_DELETE_WINDOW", btnExit)      # Cleanly exit if user closes window
    app.mainloop()
