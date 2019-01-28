This is a program to display a G-force graph in iRacing.

Currently my plan is to use it, so that you can see where you've got more grip than you think.

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

It does Require IRSDK: https://github.com/kutu/pyirsdk
