#!/usr/bin/env python3

from tkinter import Tk, Canvas, Frame, BOTH
import random, time

class Application(Frame):

    def __init__(self, master=None):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.master.title("AutoCoach")
        self.pack(fill=BOTH, expand=1)
        #self.place(x=0, y=0, relwidth=1, relheight=1)
        self.width = 600
        self.height = 50
        w = Canvas(self, width=self.width, height=self.height)
        backg = w.create_rectangle(0, 0, self.width, 50, fill="gray")
        redbar = w.create_rectangle(0, 0, (self.width/2), 50, fill="red")
        greenbar = w.create_rectangle(0, 0, (self.width/4), 50, fill="green")
        w.pack(fill=BOTH, expand=1)
        
        self.after(10, self.update, w, redbar, greenbar, self.width)
        
    def Random_Generate(self):
        RPre = random.randint(-10,10)
        RAct = random.randint(-10,10)
        return (RPre,RAct)

    def update(self, w, redbar, greenbar, width):   # Example just adds random # from -10,10 to the bars, to make them move
        Nums = self.Random_Generate()
        rx0, ry0, rx1, ry1 = w.coords(redbar)   # Redbar is Predicted Grip
        rx1 = rx1+Nums[0]                       # If statements are to keep example
        if rx1 > width:                         # within the bounds of the bar
            rx1 = (width*.9)
        if rx1 < 0:
            rx1 = width*.4
        w.coords(redbar, rx0,ry0,rx1,ry1)
        
        gx0, gy0, gx1, gy1 = w.coords(greenbar) # Greenbar is actual Grip
        gx1 = gx1+Nums[1]
        if gx1 > width:
            gx1 = (width*.9)
        if gx1 > rx1:
            rx1 = gx1 + 10
            w.coords(redbar, rx0,ry0,rx1,ry1)
        if gx1 < 0:
            gx1 = width*.3
        w.coords(greenbar, gx0,gy0,gx1,gy1)

        Tk.update(self)
        self.after(10,self.update, w, redbar, greenbar, width)
        
def main():
    root = Tk()
    ex = Application(root)
    root.mainloop()  

if __name__ == '__main__':
    main()
