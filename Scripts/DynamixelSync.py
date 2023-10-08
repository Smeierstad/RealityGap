#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
# Copyright 2017 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

# Author: Ryu Woon Jung (Leon)

#
# *********     Sync Write Example      *********
#
#
# Available Dynamixel model on this example : All models using Protocol 1.0
# This example is tested with two Dynamixel MX-28, and an USB2DYNAMIXEL
# Be sure that Dynamixel MX properties are already set as %% ID : 1 / Baudnum : 34 (Baudrate : 57600)
#

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from AX12 import ax_12
import time
import math


import queue
from Individual import Individual
from SineController12DOF import SineController12DOF
from CTRNNController import CTRNNController


import numpy as np
import random

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from sideChannelPythonside import SideChannelPythonside
import matplotlib.pyplot as plt

import pickle



# Control table address
ADDR_MX_TORQUE_ENABLE      = 24               # Control table address is different in Dynamixel model
ADDR_MX_GOAL_POSITION      = 30
ADDR_MX_PRESENT_POSITION   = 36

# Data Byte Length
LEN_MX_GOAL_POSITION       = 4
LEN_MX_PRESENT_POSITION    = 4

# Protocol version
PROTOCOL_VERSION            = 1.0               # See which protocol version is used in the Dynamixel

BAUDRATE                    = 1000000            # Dynamixel default baudrate : 57600
DEVICENAME                  = 'COM8'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = 430          # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 530            # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold

index = 0
dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]         # Goal position


# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Set the protocol version
# Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
packetHandler = PacketHandler(PROTOCOL_VERSION)

# Initialize GroupSyncWrite instance
groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_MX_GOAL_POSITION, LEN_MX_GOAL_POSITION)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()


# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()



def eval_genome(ind, steps, deltaTime, dynamixelList):

    ind.reset()


    for j in range(steps):
        
        input = list()
    
        for d in dynamixelList:
            input.append(d.currentPos())

        actions = ind.advance(input, deltaTime)

        for pos in actions:
            for d in dynamixelList:
                param = d.param(pos)
                groupSyncWrite.addParam(d.id, param)

        groupSyncWrite.txPacket()
        groupSyncWrite.clearParam()
        time.sleep(deltaTime)

        # print(actions)


with open(r"runs\mutateRate20\2023_03_09_12_18_22\gens\bestInv99", "rb") as f:
    ind = pickle.load(f)

# for i in range(12):
#     dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, i+1, 32, 100)

# dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, 2, 32, 100)

for i in range(12):
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, i+1, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)

# packetHandler.write2ByteTxRx(portHandler, 2, 32, 100)
# packetHandler.write4ByteTxRx(portHandler, 2, 30, 600)

# time.sleep(1)
dynamixelList = list()

for i in range(12):
    dynamixelList.append(ax_12(i+1, packetHandler, portHandler))



# print(dynamixelList[0].param(0.5))
# dynamixelList[1].setSpeed(100)
# dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, 2, 32, 100)


for d in dynamixelList:
    groupSyncWrite.addParam(d.id, d.paramSpeed(0, 200))

groupSyncWrite.txPacket()
groupSyncWrite.clearParam()

time.sleep(0.2)

for d in dynamixelList:
    groupSyncWrite.addParam(d.id, d.paramSpeed(1, 200))

groupSyncWrite.txPacket()
groupSyncWrite.clearParam()

time.sleep(0.2)

for d in dynamixelList:
    groupSyncWrite.addParam(d.id, d.paramSpeed(0, 200))

# print(dynamixelList[1].paramSpeed(0, 300))

# groupSyncWrite.addParam(dynamixelList[1].id, dynamixelList[1].paramSpeed(0, 100))

groupSyncWrite.txPacket()
groupSyncWrite.clearParam()


    
portHandler.closePort()


