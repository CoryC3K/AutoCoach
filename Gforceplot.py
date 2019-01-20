import random, cmath, math, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
from tkinter import Tk, Canvas, Frame, BOTH


numOfPoints = 1     # How many current G-force points do we want?
theta = .4          # controls resolution of outer bound points, smaller theta = more points

# random starter values for global stuff
ActTheta = 0.0
ActRadius = 0.0
points = []
outerPoints = []
barlist = []
maxOverallG = .1
maxSectorG = .1
currentMaxG = .1

def outerGridCreate():
    global outerPoints, theta
    radius = .5
    p1 = (radius,0)
    thetaWorking = 0
    while thetaWorking < 2*math.pi:
        outerPoints.append(p1)
        thetaWorking = round((thetaWorking + theta),6)
        p1 = (thetaWorking, radius)
        
    outerPoints.pop(0) #remove last entry for drawing reasons.


def randomPoint():
    global ActTheta, ActRadius
    RThet = random.randint(-9,9)/20
    RRad = random.randint(-9,9)/20
    ActTheta = ActTheta+RThet
    ActRadius = ActRadius+RRad

    if ActRadius < 0:
        ActRadius = abs(ActRadius)
    if ActRadius > 1.8 :
        ActRadius = 0+RRad

    if ActTheta < 0:
        ActTheta = (2*math.pi) + ActTheta
    if ActTheta > 2*math.pi:
        ActTheta = 0+RThet

    ActTheta  = round(ActTheta,6)
    ActRadius = round(ActRadius,6)
    
    checkOuterBounds(ActTheta,ActRadius)

    return(ActTheta, ActRadius)    

def checkOuterBounds(pTheta,pRad):
    global outerPoints, theta, maxOverallG, maxSectorG, currentMaxG

    DistFromCenter = pRad
    currentMaxG = DistFromCenter
    if currentMaxG == 0:
        currentMaxG = .1

    if DistFromCenter < .5: # we don't need to check these points, so don't bother
        return maxOverallG, maxSectorG, currentMaxG
    
    # Use theta to figure out what sector we're in
    nearPoint1 = [p for p in outerPoints if (p[0] >= pTheta) and (p[0] <= (pTheta + theta))]
    nearPoint2 = [x for x in outerPoints if (x[0] < pTheta) and (x[0] > (pTheta - theta))]

    # If we didn't find anything, it's becuase we're at the zero line sector, so push 'em
    if nearPoint1 == []:
        nearPoint1 = [outerPoints[0]]
    if nearPoint2 == []:
        nearPoint2 = [outerPoints[-1]]
                          
    nearPoint1 = nearPoint1[0]
    nearPoint2 = nearPoint2[0]

    # Figure out if we need to push the sector boundaries out
    if DistFromCenter > nearPoint1[1]:
        
        nnp1 = (nearPoint1[0], DistFromCenter)
        outerPoints[:] = [nnp1 if (p[0] == nearPoint1[0] and p[1] == nearPoint1[1]) else p for p in outerPoints]
        
    if DistFromCenter > nearPoint2[1]:
        nnp2 = (nearPoint2[0], DistFromCenter)
        outerPoints[:] = [nnp2 if (p[0] == nearPoint2[0] and p[1] == nearPoint2[1]) else p for p in outerPoints]
        
    if nearPoint1[1] > nearPoint2[1]:
        maxSectorG = nearPoint1[1]
    else:
        maxSectorG = nearPoint2[1]

    if maxSectorG > maxOverallG:
        maxOverallG = maxSectorG
        ax2.axes.set_xlim(0,maxOverallG)
    
    
def animateGPoints(i): # animates the actual blue G point reading
    global numOfPoints
    points.append(randomPoint())
    N = numOfPoints
    while len(points) > numOfPoints:
        points.pop(0)
    theta_val = [x[0] for x in points]
    rad_val = [x[1] for x in points]
    ln = ax1.plot(theta_val[-N:],rad_val[-N:], 'bo-')
    return ln

def animateBounds(i):    # animate the outer yellow bound points
    global outerPoints
    ax1.cla()
    ax1.set_ylim(0,2)
    ax1.axes.set_yticklabels([])
    ax1.axes.set_xticklabels([])
    
    theta_val = [t[0] for t in outerPoints]
    rad_val = [r[1] for r in outerPoints]
    theta_val.append(theta_val[0])
    rad_val.append(rad_val[0])
    out = ax1.plot(theta_val,rad_val, 'y-')
    
    return out

def animateBars(i): # animate the lower limit bars
    global barlist, maxOverallG, maxSectorG, currentMaxG
    Nums = [maxOverallG,maxSectorG,currentMaxG]
    ax2.axes.set_ylim(0,1)
    ax2.axes.tick_params(left=False, bottom=False)
    ax2.axes.set_yticklabels([])
    
    for i in enumerate(barlist):
        i[1][0].set_width(Nums[i[0]])
    thing2 = ax2.plot()
    
    fig.canvas.draw()
    
    return thing2
    
def initGPoints():
    global numOfPoints
    points = []
    c = 0
    while c <= numOfPoints:                       # create initial list of 10 points
        points.append(randomPoint())
        c = c+1

    ox_val = [x[0] for x in points]     # split it so we can plot it
    oy_val = [x[1] for x in points]
    ln = ax1.plot(points[0],points[1])
    
    return ln

def initBounds():                # generate the initial outside grip circle points
    global outerPoints
    outerGridCreate()
    theta_val = [t[0] for t in outerPoints]
    rad_val = [r[1] for r in outerPoints]
    out = ax1.plot(theta_val,rad_val)
    
    return out

def initBars():
    global barlist
    max_G = 1.0
    current_sec = .4
    current = .3
    p1 = ax2.barh(0, max_G, height=2, color='gray')
    p2 = ax2.barh(0, current_sec, height=2, color='red')
    p3 = ax2.barh(0, current, height=2, color='green')
    barlist = [p1,p2,p3]
    return barlist

fig = plt.figure()
gs = gridspec.GridSpec(2,1,height_ratios=[4,1])

ax1 = fig.add_subplot(gs[0], projection='polar')
ax2 = fig.add_subplot(gs[1])

ani = []
ani.append(animation.FuncAnimation(fig, animateBounds,  interval=1, init_func=initBounds))
ani.append(animation.FuncAnimation(fig, animateGPoints, interval=1, init_func=initGPoints))
ani.append(animation.FuncAnimation(fig, animateBars,    interval=5, init_func=initBars))

plt.show()
