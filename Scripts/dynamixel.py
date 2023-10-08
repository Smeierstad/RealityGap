import queue
from Individual import Individual
from SineController12DOF import SineController12DOF
from CTRNNController import CTRNNController


import numpy as np
import random

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from sideChannelPythonside import SideChannelPythonside

import pickle

from pyax12.connection import Connection
import time
import math

with open(r"runs\2023_01_31_18_23_17_veryGood\gens\bestInv249", "rb") as f:
    ind = pickle.load(f)

controller = ind.getController()
# controller.plot(10)
controller.reset()
for i in range(10):
    print(controller.advance(np.ones(12))[0:3])



# Connect to the serial port
con = Connection(port="COM8", baudrate=1000000)

lower = con.get_cw_angle_limit(1)
upper = con.get_ccw_angle_limit(1)

limit1 = [lower, upper]

lower = con.get_cw_angle_limit(2)
upper = con.get_ccw_angle_limit(2)

limit2 = [lower, upper]


lower = con.get_cw_angle_limit(3)
upper = con.get_ccw_angle_limit(3)

limit3 = [lower, upper]


increment1 = (limit1[1] - limit1[0])/2
increment2 = (limit2[1] - limit2[0])/2
increment3 = (limit3[1] - limit3[0])/2

mid1 = int(limit1[0]+(0.5*(limit1[1]-limit1[0])))
mid2 = int(limit2[0]+(0.5*(limit2[1]-limit2[0])))
mid3 = int(limit3[0]+(0.5*(limit3[1]-limit3[0])))

# print(mid1)
# print(mid2)
# print(mid3)

increment = 0.1

val = -0.02
for i in range(40):
    action = controller.advance(np.ones(12))
    val = val + increment
    con.goto(1, int(mid1 + (action[0]*increment1)), speed=700)
    con.goto(2, int(mid2 + (action[1]*increment2)), speed= 700)
    con.goto(3, int(mid3 + (action[2]*increment3)), speed= 700)
    time.sleep(0.2)

    
con.close()