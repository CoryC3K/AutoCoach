#!/usr/bin/env python3

from tkinter import Tk, Canvas, Frame, BOTH
import random, time

class Application(Frame):
    def __init__(self, master='none'):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.master.title("AutoCoach")
        self.pack(fill=BOTH, expand=1)
        
        c = Canvas(self, bd=2, bg="black")
        c.pack(fill=BOTH, expand=True)
        c.update()
        
        window_width = c.winfo_width()          # This bit allows for resizing the window
        window_height = c.winfo_height()        # so that the bars will all fit right 
        
        backgr = c.create_rectangle( 0, 0, (window_width*1.0), window_height, fill="gray")  # The 1.0, 0.8, 0.5 are just starter values
        redbar = c.create_rectangle( 0, 0, (window_width*0.8), window_height, fill="red")  
        grnbar = c.create_rectangle( 0, 0, (window_width*0.5), window_height, fill="green")

        self.bars(c, backgr, redbar, grnbar)
        
    def bars(self, c, backgr, redbar, grnbar):
        Nums = G_Forces()   # Read the G-forces from an outside source
        Pred_G = Nums[0]    # It comes in as a list, so we separate them out
        Actu_G = Nums[1]    # mostly for readable code
        Maxx_G = Nums[2]

        width = c.winfo_width()
        height = c.winfo_height()

        c.coords(backgr, 0, 0, (Maxx_G*width), height)          # Redraw the background bar (for new width/height)
        c.coords(redbar, 0, 0, ((Pred_G/Maxx_G)*width), height) # Redraw the Red Bar
        c.coords(grnbar, 0, 0, ((Actu_G/Maxx_G)*width), height) # Redraw the Green Bar
        # print("G's: ", self.lat,self.long)
        Tk.update(self)                                         # Update app window
        self.after(16, self.bars, c, backgr, redbar, grnbar)    # Do another cycle

def G_Forces():
    global Predicted_G, Actual_G, Max_G

    ### this is all for generating random G forces
    ### In the real code, this would pull from the API and do maths
    RPre = random.randint(-5,5)/100
    RAct = random.randint(-3,5)/100
    Predicted_G = round((Predicted_G + RPre),2)
    Actual_G    = round((Actual_G + RAct),2)
    if Predicted_G > Max_G:
        Max_G = Predicted_G
    if Actual_G > Predicted_G:
        Actual_G = Predicted_G * .8
    #print("PredictedG: ", Predicted_G)
    #print("ActualG:    ", Actual_G)
    ### Okay, back to real code stuff
        
    return (Predicted_G, Actual_G, Max_G)

    
if __name__ == '__main__':
    Max_G =         1.0        # Declare some random starter values
    Predicted_G =   0.5
    Actual_G =      0.8
    root = Tk()
    root.geometry("300x50")
    e = Application(root)
    root.mainloop()
