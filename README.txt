This is a program to display a G-force graph in iRacing.

It does require IRSDK (to connect to the data from iracing): https://github.com/kutu/pyirsdk

______________________________

Currently my plan is to use it, so that you can see where you've got more grip than you think.

Gif of it running: https://imgur.com/fMGqtmV
It graphs the:

Maximum Overall G-force (Gray bar at the bottom, and blue circle)
Predicted available G-Force (Red bar, and Red circle, also the yellow outer line)
Current G-force (Green bar, and blue dot)

I still need to add:

Lots of filtering. Right now if you hit a wall, and it registers 50 G's, it'll re-size the graph to 50 g's and it'll be useless. 
Also it has no idea when you're sliding, but I think I can get that from yaw and steering input? Dunno. We'll see.
ABS freaks it out too (shows more G's than are real).

I think I could also filter out when you're at max throttle and it shows a bunch of red. 

But yeah, it works! 

You can use OVRDrop to display it in VR as well. I'm devloping it using the following setup:

Fanatec CSR (old-school) FFB wheel
Fanatec CSL Elite pedals (loadcell to come someday)
DIY made of 2x4's chassis
Some random mechanical number pad I got off of amazon for $16 for a button box.

GTX 1070
i5-8400 ish, 6 core. 
8gb single channel ram
NVME SSD 970 Evo

Lenovo Explorer WMR headset (works FANTASTIC, highly recommend for a $100 VR setup!)
The key to using it in VR is a program called "OVRDrop", available on steam: https://store.steampowered.com/app/586210/OVRdrop/
