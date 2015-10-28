#!/usr/bin/python

import rospy
from std_msgs.msg import Float64MultiArray
import matplotlib.pyplot as plt
import numpy as np

# create the figure
fig = plt.figure()
im=[ fig.add_subplot(1,6,n+1).imshow(np.random.random((60,20))) for n in range(6)]
plt.show(block=False)

critic_scores = np.empty((60,20,12))
critic_scores[:,:,:] = np.nan
for i in im:
    i.set_array(critic_scores[:,:,0])

# redraw the figure
fig.canvas.draw()

go=False # flag to trigger redraw in main thread
rospy.init_node("dwlogger")

def cost_data_cb(msg):
    global go # oh yeah
    print "------------------\ngot some.", len(msg.data)
    #print msg.layout
    rows=msg.layout.data_offset
    if rows != len(msg.data)/14:
        print "bad"
        print "Data size:", len(msg.data)
        print "Number of rows: ", rows
        return
    else:
        print "ok"
    data=np.array(msg.data).reshape((rows, 14))

    print data[:,12]
    # scale the velocities by 10 and centre them in the plot window...
    data[:,0:2]*=10
    data[:,0]+=10
    data[:,1]+=30

    critic_scores[:,:,:]=1 # default illegal
    critic_scores[data[:,1].astype('int'), data[:,0].astype('int'),:] = data[:,2:]/255.0
    critic_scores[critic_scores<0]=1 # -ve values illegal
    go=True
#    while go:   # if pause until redraw then all are qeued but none missed
#        pass


sub = rospy.Subscriber("/move_base/DWAPlannerROS/sample_costs", Float64MultiArray, cost_data_cb)

t=0
while not rospy.is_shutdown():
    t+=1
    if go:
        for i,j in enumerate(im):
            j.set_array(critic_scores[:,:,i*2]*6) # multiplied by 6 here just to stretch the scale...
        fig.canvas.draw()
        print "Draw!"
        go=False
    if t>1000000:
        # occasional draw for fun
        t=0
        fig.canvas.draw()
    
rospy.spin()

