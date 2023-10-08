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




def eval_genome(ind, queue, steps, deltaTime, controller, robot, plot = None):

    lst = queue.get()
    env = lst[0]
    sideChannel = lst[1]

    ind.reset()

    sideChannel.send_string(f"Robot:{robot}")
    env.reset()

    individual_name = list(env._env_specs)[0]

    for j in range(steps):
        observation, termial_steps = env.get_steps(individual_name)
        if (len(observation.agent_id) > 0):

            input = observation.obs[0][0][0:12]
            actions = ind.advance(input, deltaTime)
            action = np.empty((1,len(actions)))

            for i in range(len(actions)):
                action[0, i] = actions[i]

            if plot != None:
                plot.append(input)

            action_tuple = ActionTuple(action)
            env.set_action_for_agent(individual_name, observation.agent_id, action_tuple)
            env.step()

            ind.setFitness(float(observation.reward[0]))

            # if(j > 20):
            #     if (ind.getFitness() < j * 0.05):
            #         break

            # if(ind.getFitness() < ((j - 20)*0.01)):
            #     break
    
    lst = [env, sideChannel]
    queue.put(lst)


if __name__ == "__main__":
    # path = r"Builds/12DOFLinux/12DOF.x86_64"
    path = r"Builds/NewLeg"

    steps = 15
    robot = 0



    ind = Individual(CTRNNController, "configs/config.ini")

    ind.reset()

    # controller = ind.getController()
    # controller.drawNet()
    # controller.plot(50)

    plotX = []



    id = 4000

    sideChannel = SideChannelPythonside()
    env = UnityEnvironment(file_name=path, worker_id=id, seed = 4, side_channels=[sideChannel], no_graphics=False)

    env.reset()
    for i in range(10):
        env.step()
    env.reset()


    q = queue.Queue()
    q.put([env, sideChannel])

    controller = [1, 0, -1, 1, 0, -1, 1, 0, -1, 1, 0, -1]
    

    

    for i in range(1):
        eval_genome(ind, q, steps, 0.2, controller, robot, plotX)

    figure, axis = plt.subplots(4, 3)

    print(plotX)

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


    print(ind.getFitness())

    env.close()

    
