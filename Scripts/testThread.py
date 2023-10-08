from deap import base,tools,algorithms
import queue
import threading
import numpy as np
import pickle
import time

from tqdm import tqdm
from copy import deepcopy

import random

from Individual import Individual
from SineController12DOF import SineController12DOF
from Evaluator import eval_genome
from CTRNNController import CTRNNController
# from individualController import individualController

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
from sideChannelPythonside import SideChannelPythonside
from SineController12DOF import SineController12DOF
from Individual import Individual
from configparser import ConfigParser
from reporter import Reporter

import socket
HIGHEST_WORKER_ID = 65535 - UnityEnvironment.BASE_ENVIRONMENT_PORT
def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def is_worker_id_open(worker_id: int) -> bool:
    return not is_port_in_use(
        UnityEnvironment.BASE_ENVIRONMENT_PORT + worker_id
    )

def get_worker_id() -> int:
    pid = random.randrange(HIGHEST_WORKER_ID)
    while not is_worker_id_open(pid):
        print("Not open!")
        pid = random.randrange(HIGHEST_WORKER_ID)
    return pid


def eval_genome(ind, queue, steps, deltaTime, dof, robot = 0):

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

            input = observation.obs[0][0][0:dof]
            actions = ind.advance(input, deltaTime)
            action = np.empty((1,len(actions)))

            for i in range(len(actions)):
                action[0, i] = actions[i]

            action_tuple = ActionTuple(action)
            env.set_action_for_agent(individual_name, observation.agent_id, action_tuple)
            env.step()

            ind.setFitness(float(observation.reward[0]))

            if(j > 20):
                if (ind.getFitness() < j * 0.05):
                    break

            # if(ind.getFitness() < ((j - 20)*0.01)):
            #     break
    print(ind.getFitness())
    lst = [env, sideChannel]
    queue.put(lst)


if __name__ == "__main__":

    config = r"configs/config.ini"
    #path = r"Builds/12DOFLinux/12DOF.x86_64"
    path = r"Builds/12DOF"

    Reporter("runs", config)

    threads = []
    inds = []
    for i in range(5):
        inds.append(Individual(CTRNNController, config))

    envQueue = queue.Queue()
    for i in range(5):
        sideChannel = SideChannelPythonside()
        env = UnityEnvironment(file_name=path, worker_id=get_worker_id(), seed=4, side_channels=[sideChannel], no_graphics=True)
        env.reset()
        for j in range(5):
            env.step()
        env.reset()
        env_list = [env, sideChannel]
        envQueue.put(env_list)

    for i in range(5):
        thread = threading.Thread(target=eval_genome, args=(inds[i], envQueue, 50, 0.2, 12, 0))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join

    for i in range(5):
        env = envQueue.get()
        env = env[0]
        env.close()
