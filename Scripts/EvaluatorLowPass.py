import queue
from Individual import Individual
from SineController12DOF import SineController12DOF
from CTRNNController import CTRNNController

from lowpassClass import LowPass

import numpy as np
import random
import os

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from sideChannelPythonside import SideChannelPythonside
import matplotlib.pyplot as plt

import pickle




def eval_genome_lowpass(ind, queue, steps, advanceTime, timeStep, robot = 0, plot = None):

    lst = queue.get()
    env = lst[0]
    sideChannel = lst[1]

    ind.reset()
    ind.setRobot(robot)

    sideChannel.send_string(f"Robot:{robot}")
    env.reset()

    individual_name = list(env._env_specs)[0]

    action = np.empty((1,12))

    lowPassList = []
    filterDataList = []

    for i in range(12):
        lowPassList.append(LowPass())
        filterDataList.append([])

    for j in range(steps):
        observation, termial_steps = env.get_steps(individual_name)
        if (len(observation.agent_id) > 0):

            input = observation.obs[0][0][0:12]
            actions = ind.advance(input, advanceTime, timeStep)

            actionFull = []
            
            for i in range(len(actions)):
                filterAction = lowPassList[i].filter(actions[i])
                action[0, i] = filterAction
                actionFull.append(filterAction)
                

            if plot != None:
                plot.append(actionFull)


            action_tuple = ActionTuple(action)
            env.set_action_for_agent(individual_name, observation.agent_id, action_tuple)
            env.step()

            ind.setFitness(float(observation.reward[0]))

            # if(j > 20):
            #     if (ind.getFitness() < j * 0.05):
            #         break

    
    lst = [env, sideChannel]
    queue.put(lst)


def testAll(folder, advanceTime, timeStep, queue, steps):

    ind = []

    for subdir, dirs, files in os.walk(folder):
        for file in files:
            name = os.path.join(subdir, file)
            if "bestInv" in name:
                with open(name, "rb") as f:
                    ind.append(pickle.load(f))
    
    j = 1
    for i in ind:
        eval_genome_lowpass(i, queue, steps, advanceTime, timeStep, i.getRobot())
        j += 1
        print(i.getFitness())
    
def testOne(file, advanceTime, timeStep, queue, steps):


    plt.style.use('ggplot')
    plotX = []

    with open(file, "rb") as f:
        ind = pickle.load(f)

    # controller = ind.getController()
    # controller.drawNet()
    # controller.plot(10)

    eval_genome_lowpass(ind, queue, steps, advanceTime, timeStep, ind.getRobot(), plotX)

    print(ind.getFitness())

    figure, axis = plt.subplots(4, 3, sharey=True)

    newList = []

    for i in range(12):
        newList.append([])

    for i in range(len(plotX)):
        for j in range(12):
            newList[j].append(plotX[i][j])

    k = 0
    for i in range(4):
        for j in range(3):
            axis[i, j].plot(newList[k])
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
    path = r"Builds/WindowsTest"
    # path = None



    steps = 100

    q = makeEnv(path)

    # testAll(r"runs\MutateDecentralized\24\2023_05_04_18_23_14_670207", 0.2, 0.02, q, steps)


    testOne(r"runs\mutate\2023_05_09_11_42_01_773930\gens\bestInv029", 0.05, 0.05, q, steps)


    q.get()[0].close()

    
