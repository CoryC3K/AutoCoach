#!/usr/bin/env python3

from tkinter import * 
from tkinter import ttk
import tkinter as tk
import random, time, math, cmath, itertools
import irsdk

Max_G =         0.2     # Declare some random starter values
Predicted_G =   0.01
Actual_G =      0.01
outerPoints = []    # Outer Points are always !!! Radius, Theta format!!!
theta = .01         # controls resolution of outer points, smaller = more
dot_size = 3
smoothing = .02

# Connect to IRacing through IRSDK
ir = irsdk.IRSDK()
ir.startup()

class Application(Frame):
    def __init__(self, master='none'):
        Frame.__init__(self, master)
        self.master.title("AutoCoach")

        style = ttk.Style()
        style.theme_use('vista')

        self.p = ttk.Panedwindow(self.master, orient=VERTICAL)
        self.TopFrame = ttk.Frame(self.p)#, text='G-Graph', width=100, height=100)
        self.BottomFrame = ttk.Frame(self.p)#, text='G-Bar', width=100, height=100)   # second pane
        self.p.add(self.TopFrame, weight=1)
        self.p.add(self.BottomFrame, weight=60)
        self.p.pack(side=TOP, expand=TRUE, fill=BOTH)

        self.c1 = Canvas(self.TopFrame, borderwidth=1, bg="white")
        self.c1.pack(side=TOP, expand=TRUE, fill=BOTH)
        self.c2 = Canvas(self.BottomFrame, borderwidth=1, bg="black")
        self.c2.pack(side=TOP, expand=TRUE, fill=X)
        
        self.c1.update()
        self.c2.update()
        
        window_width = self.c1.winfo_width() 
        c1_height = self.c1.winfo_height()
        c2_height = self.c2.winfo_height()
        
        backgr = self.c2.create_rectangle( 0, 0, (window_width*1.0), c2_height, fill="gray")
        redbar = self.c2.create_rectangle( 0, 0, (window_width*0.8), c2_height, fill="red")
        grnbar = self.c2.create_rectangle( 0, 0, (window_width*0.5), c2_height, fill="green")
        
        plot_backgr = self.c1.create_rectangle( 0, 0, (window_width), c1_height, fill='grey')
        create_graph = draw_graph(self.c1, window_width, c1_height)

        self.c1.create_oval((.49*window_width),(.49*c1_height),(.51*window_width),(.51*c1_height), fill='blue', tags='g_dot')
        
        outerGridCreate()   # Creates list of starter outer points
        outerCoords = draw_outer_bounds(self.c1, window_width, c1_height)
        self.c1.create_polygon(outerCoords, fill = '', outline='yellow', tags='bounds')
        
        self.bars(self.c1, self.c2, backgr, redbar, grnbar, plot_backgr)    # starts the looper


        
    def bars(self, c1, c2, backgr, redbar, grnbar, plot_backgr):    # main loop of updating stuff
        global Actual_G, Max_G, Predicted_G

        width = self.TopFrame.winfo_width()
        c1_height = self.TopFrame.winfo_height()
        c2_height = self.BottomFrame.winfo_height()

        self.c2.coords(backgr, 0, 0, (Max_G*width), c2_height)          # Resize the background bar (for new width/height)
        self.c2.coords(redbar, 0, 0, ((Predicted_G/Max_G)*width), c2_height) # Resize the Red Bar
        self.c2.coords(grnbar, 0, 0, ((abs(Actual_G)/Max_G)*width), c2_height) # Resize the Green Bar        

        self.c1.coords(plot_backgr, 0, 0, width, c1_height)     # Re-size grid canvas
        
        draw_current_dot(self.c1, width, c1_height)             # draw current G dot
        redraw_graph(self.c1, width, c1_height)                 # redraw the graph background with new window size    
        
        Tk.update(self)                                         # Update app window
        root.lift()
        self.after(1, self.bars, self.c1, self.c2, backgr, redbar, grnbar, plot_backgr)    # Do another cycle

def draw_current_dot(canvas, cwidth, cheight):
    global Actual_G, Max_G, dot_size

    r,phi = randomPoint()
    Actual_G = r
    comp = cmath.rect(r,phi)    # convert from polar to cartesian
    
    dotx_out =  Map(comp.real, 0, (2*Max_G), 0, cwidth)         # Changes grid values to screen height ratios
    doty_out =  Map(comp.imag, 0, (2*Max_G), 0, cheight)
    
    canvas.coords('g_dot',((.5*cwidth  + dotx_out - dot_size)),   # middle of screen + position + size modifier (in pixels)
                          ( .5*cheight + doty_out - dot_size),
                          ( .5*cwidth  + dotx_out + dot_size),
                          ( .5*cheight + doty_out + dot_size)) 

def redraw_graph(canvas, cwidth, cheight):  # re-draws the graph so that it updates if you change window size
    global Predicted_G, Max_G, outerPoints
    canvas.coords('xAxis',(.1*cwidth),(.5*cheight),(.9*cwidth),(.5*cheight))    # re-draw x axis
    canvas.coords('yAxis',(.5*cwidth),(.1*cheight),(.5*cwidth),(.9*cheight))    # re-draw Y axis
    canvas.coords('outCirc',(.1*cwidth),(.1*cheight),(.9*cwidth),(.9*cheight))
    canvas.coords('inCirc', (.3*cwidth),(.3*cheight),(.7*cwidth),(.7*cheight))
    
    outerWindow = draw_outer_bounds(canvas, cwidth, cheight)
    canvas.coords('bounds', *flatten(outerWindow))

    Pred_out =   Map(Predicted_G, 0, (2*Max_G), 0, cheight) #twice maxg for top and bottom of outer bound
    Pred_out_w = Map(Predicted_G, 0, (2*Max_G), 0, cwidth)
    Max_out =    Map(Max_G, 0, (2*Max_G), 0, cheight)
    Max_out_w =  Map(Max_G, 0, (2*Max_G), 0, cwidth)
    
    canvas.coords('predg_cir', (.5*cwidth + Pred_out_w),(.5*cheight + Pred_out),(.5*cwidth - Pred_out_w),(.5*cheight - Pred_out)) # This shit is key right here
    canvas.coords('maxg_cir',  (.5*cwidth + Max_out_w) ,(.5*cheight + Max_out) ,(.5*cwidth - Max_out_w) ,(.5*cheight - Max_out))

def draw_graph(canvas, cwidth, cheight):    # draws the inital graph background
    canvas.create_line((.1*cwidth),(.5*cheight),(.9*cwidth),(.5*cheight), tags='xAxis', width=2)            # create x axis
    canvas.create_line((.5*cwidth),(.1*cheight),(.5*cwidth),(.9*cheight), tags='yAxis', width=2)            # create Y axis
    canvas.create_oval((.1*cwidth),(.1*cheight),(.9*cwidth),(.9*cheight), tags='outCirc', dash=1, width=.5) # create outer dotted circle
    canvas.create_oval((.3*cwidth),(.3*cheight),(.7*cwidth),(.7*cheight), tags='inCirc', dash=1, width=.5)  # create inner dottec circle
    canvas.create_oval((.4*cwidth),(.4*cheight),(.6*cwidth),(.6*cheight), fill='', tags='predg_cir', outline='red') # predicted G red circle
    canvas.create_oval((.4*cwidth),(.4*cheight),(.6*cwidth),(.6*cheight), fill='', tags='maxg_cir', outline='blue') # maximum G blue circle

def outerGridCreate():  # Points are stored in polar format, because it's easier, and I had code from a previous version in matplotlib
                        # Python's math function works with -pi to pi for theta, so that's what we're mapping
    global outerPoints, theta
    radius = .1
    p1 = (radius,0)
    thetaWorking = 0
    
    while thetaWorking < math.pi:   # go around the circle, adding points every couple degrees at a starter radius
        outerPoints.append(p1)
        thetaWorking = round((thetaWorking + theta),6)
        p1 = (radius, thetaWorking)
        
    thetaWorking = (math.pi * -1)   # after we get theta > pi, reset to -pi
    p1 = (radius, thetaWorking)     # add that first point on the x negative axis
    
    while thetaWorking < 0:         # Do the bottom half of the circle, going from negative pi back to zero
            outerPoints.append(p1)
            thetaWorking = round((thetaWorking + theta),6)
            p1 = (radius, thetaWorking)
            
    outerPoints.append(outerPoints[0]) # close the polygon

def draw_outer_bounds(canvas, cwidth, cheight):
    global outerPoints, Max_G
    outerCartesian = []
    outerWindow = []
    
    for point in outerPoints:           #Convert polar coords to cartesian coords
        cartesian = cmath.rect(point[0], point[1])  #cmath.rect = (radius, theta)
        cartesian = (round(cartesian.real, 5), round(cartesian.imag, 5))
        outerCartesian.append(cartesian)
   
    for pointb in outerCartesian:       # Convert cartesian coords to screen locations
        pointbw = Map(pointb[0], 0, (2*Max_G), 0, cwidth)
        pointbh = Map(pointb[1], 0, (2*Max_G), 0, cheight)
        windowPoint = (round((pointbw +(.5 * cwidth))), round((pointbh + (.5 * cheight))))
        outerWindow.append(windowPoint)

    return outerWindow
    
    
def randomPoint():          # Creates a random point, and updates the outer bounds for that new point

    lat =  ir['LatAccel']  * .10197162129779    # converts m/s^2 to G's
    long = ir['LongAccel'] * .10197162129779
    ActRadius = round((math.sqrt(math.pow(lat,2) + math.pow(long,2))),3)    # Figures point x,y Radius for polar graphing
    ActTheta  = round((math.atan2(long,lat)),4)                              # Figures point x,y Theta  for polar graphing

    checkOuterBounds(ActRadius, ActTheta)   # updates the outer bounds

    return(ActRadius, ActTheta)

def checkOuterBounds(pRad,pTheta):  # just updates the outerPoints list, and sets predicted & Max g's
    global outerPoints, theta, Max_G, Predicted_G, Actual_G

    # Use theta to figure out what sector we're in
    nearPoint1 = [p for p in outerPoints if (p[1] >= pTheta) and (p[1] <= (pTheta + theta))]
    nearPoint2 = [x for x in outerPoints if (x[1] < pTheta) and (x[1] > (pTheta - theta))]

    # If we didn't find anything, it's becuase we're at the zero line sector, so push 'em
    if nearPoint1 == []:  nearPoint1 = [outerPoints[0]]
    if nearPoint2 == []:  nearPoint2 = [outerPoints[-1]]
                          
    nearPoint1 = nearPoint1[0] # converts from list item to tuple
    nearPoint2 = nearPoint2[0]

    # Figure out if we need to push the sector boundaries out
    if pRad > nearPoint1[0]:        # If the point radius is more than the sector radius limit...
        nnp1 = (pRad,nearPoint1[1]) # create new point tuple, with new radius and old point theta
        # We need to find the point in the list, and replace it. List comprehension works for that...
        outerPoints[:] = [nnp1 if (p[0] == nearPoint1[0] and p[1] == nearPoint1[1]) else p for p in outerPoints]

    # Do the same for the other point
    if pRad > nearPoint2[0]:
        nnp2 = (pRad,nearPoint2[1])
        outerPoints[:] = [nnp2 if (p[0] == nearPoint2[0] and p[1] == nearPoint2[1]) else p for p in outerPoints]
    
    outerPoints.pop()   # Updates the last point in the list with the first point, closing the polygon, 
    outerPoints.append(outerPoints[0])  # this is just to make sure if it's changed, it's updated.

    # Check for maximum G's to set the bars to
    if nearPoint1[0] > nearPoint2[0]: Predicted_G = nearPoint1[0]  # Updates Predicted G to the sector G
    else: Predicted_G = nearPoint2[0]
    
    if Predicted_G > Max_G: Max_G = Predicted_G # Updates the MaxG if we're going hard.

    filtering() # runs outer bounds through any filters to smooth it

def filtering():    # This just makes sure the next and previous points are smoothed, better filtering to come in the future
    global outerPoints, smoothing
    for i,point in enumerate(outerPoints):  # index, point (Radius, Theta)
        prad = point[0]
        if (i+1) > (len(outerPoints)-1): pass  # if we're at the end of the list, we're done
        else:
            if outerPoints[i+1][0] < (prad - smoothing):
                outerPoints[i+1] = ((outerPoints[i+1][0] + (.5* smoothing)),(outerPoints[i+1][1]))
        if outerPoints[i-1][0] < (prad - smoothing):
            outerPoints[i-1] = ((outerPoints[i-1][0] + (.5* smoothing)),(outerPoints[i-1][1]))

def Map(value, fLow, fHigh, toLow, toHigh):     #pretty much the map() function in arduino, it just scales values
    return toLow + (toHigh - toLow) * ((value - fLow) / (fHigh - fLow))

def flatten(list_of_lists): # Used in redraw_graph
    return itertools.chain.from_iterable(list_of_lists)
            
    
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("300x300")
    e = Application(master=root)
    e.mainloop()
