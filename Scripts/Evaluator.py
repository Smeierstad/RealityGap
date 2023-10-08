import queue
from Individual import Individual
from SineController12DOF import SineController12DOF
from CTRNNController import CTRNNController
from DecentralizedController import DecentralizedController
from SyncControllerOne import SyncControllerOne

import numpy as np
import random
import os

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from sideChannelPythonside import SideChannelPythonside
import matplotlib.pyplot as plt
from configparser import ConfigParser

import pickle




def eval_genome(ind, queue, steps, advanceTime, timeStep, robot = 0, DP = 10, plot = None, plotInput = None):

    lst = queue.get()
    env = lst[0]
    sideChannel = lst[1]

    ind.reset()
    ind.setRobot(robot)

    sideChannel.send_string(f"Robot:{robot}")
    env.reset()

    individual_name = list(env._env_specs)[0]

    action = np.empty((1,12))

    for j in range(steps):
        observation, termial_steps = env.get_steps(individual_name)
        if (len(observation.agent_id) > 0):

            input = observation.obs[0][0][0:12]
            actions = ind.advance(input, advanceTime, timeStep)
            
            
            # for i in range(len(actions)):
            #     action[0, i] = actions[i]
                

            if plot != None:
                # print(type(actions))
                plot.append(actions)
            
            if plotInput != None:
                # print(type(input.tolist()))
                plotInput.append(input.tolist())


            if(j % DP == 0):
                for i in range(len(actions)):
                    action[0, i] = actions[i]
                    # if plot != None:
                    #     plot.append(actions)


            action_tuple = ActionTuple(action)
            env.set_action_for_agent(individual_name, observation.agent_id, action_tuple)
            env.step()

            ind.setFitness(float(observation.reward[0]))
    
    lst = [env, sideChannel]
    queue.put(lst)


def testAll(folder, queue, number):

    fileList = []

    for subdir, dirs, files in os.walk(folder):
            for file in files:
                name = os.path.join(subdir, file)
                if "config.ini" in name:
                    config = name
                if "bestInv" + number in name:
                    fileList.append(name)
                    
    configFile = ConfigParser()
    configFile.read(config)

    eaData = configFile["EA"]

    steps = int(eaData["steps"])
    DP = int(eaData["dp"])
    advanceTime = float(eaData["advanceTime"])
    timeStep = float(eaData["timeStep"])
    
    for i in range(len(fileList)):
            
        with open(fileList[i], 'rb') as f:
            ind = pickle.load(f)
        
        # controller = ind.getController()
        # controller.drawNet()
        
        testOne(ind, advanceTime, timeStep, queue, steps, DP)
    
    # j = 1
    # for i in ind:
    #     eval_genome(i, queue, steps, advanceTime, timeStep, i.getRobot())
    #     j += 1
        # print(i.getFitness())
    
def testOne(ind, advanceTime, timeStep, queue, steps, DP, robot = None):


    plt.style.use('ggplot')
    plotX = []
    plotY = []

    # controller = ind.getController()
    # controller.drawNet()
    # controller.plot(10)
    
    if not robot:
        robot = ind.getRobot()

    eval_genome(ind, queue, steps, advanceTime, timeStep, robot, DP, plotX, plotY)

    print(ind.getFitness())

    figure, axis = plt.subplots(4, 3, sharey=True)

    newList = []
    newListY = []

    for i in range(12):
        newList.append([])
        newListY.append([])


    for i in range(len(plotX)):
        for j in range(12):
            newList[j].append(plotX[i][j])
            newListY[j].append(plotY[i][j])            
    

    k = 0
    for i in range(4):
        for j in range(3):
            axis[i, j].plot(newList[k])
            axis[i, j].plot(newListY[k])
            k += 1
    plt.show()

def makeEnv(path):

    id = 0

    sideChannel = SideChannelPythonside()
    env = UnityEnvironment(file_name=path, worker_id=id, seed = 4, side_channels=[sideChannel], no_graphics=False)
    
    env.reset()
    for i in range(10):
        env.step()
    env.reset()


    q = queue.Queue()
    q.put([env, sideChannel])

    return q

if __name__ == "__main__":
    # path = r"Builds/12DOFLinux/12DOF.x86_64"
    path = r"Builds/DP1_W_01_noGround"
    path = None



    steps = 100

    q = makeEnv(path)

    # testAll(r"runs\MutateDecentralized\24\2023_05_04_18_23_14_670207", 0.2, 0.02, q, steps)



    ind = Individual(SyncControllerOne, "configs/config.ini", 0.01)

    # for i in range(10):
    #     ind.mutate(0.5, 0.5)

    testOne(ind, 0.01, 0.004, q, 500, 10, 5)

    # testOne(r"runs\mutate\2023_05_09_11_42_01_773930\gens\bestInv029", 0.05, 0.05, q, steps)


    q.get()[0].close()

    
