import os
import pickle
from datetime import datetime
import shutil
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plotFile(file):

    df = pd.read_csv(file, header=None)

    mean = df.mean(axis=1)
    max = df.max(axis=1)
    min = df.min(axis=1)


    plt.plot(mean)
    plt.plot(min)
    plt.plot(max)
    # plt.show()

def plotDf(df):
    mean = df.mean(axis=1)
    max = df.max(axis=1)
    min = df.min(axis=1)


    plt.plot(mean)
    # plt.plot(min)
    # plt.plot(max)
    plt.show()

def plotAll(list, n, legendList = None, onePlot = False):
    
    plt.style.use('ggplot')

    if onePlot:
        for i in range(n):
            if legendList:
                # plt.plot(list[i].max(axis=1), colorList[i], label = legendList[i])
                mean = list[i].mean(axis=1)
                std = list[i].std(axis=1)
                plt.plot(mean, label = legendList[i])
                # plt.plot(mean - std, colorList[i]+'.')
                # plt.plot(mean + std, colorList[i]+'.')
                plt.legend(loc="upper left")
            else:
                plt.plot(list[i].mean(axis=1))

    else:
        figure, axis = plt.subplots(1, n, sharey=True)
        for i in range(n):
            mean = list[i].mean(axis=1)
            std = list[i].std(axis=1)
            axis[i].plot(mean, label = legendList[i])
            axis[i].legend(loc="upper left")
           # axis[i].plot(mean - std, 'g-.')
            # axis[i].plot(mean + std, 'g-.')
            
            # axis[i].plot(list[i].max(axis=1))
            # axis[i].plot(list[i].min(axis=1))

    plt.show()



def combine(folder):

    dataframes = []

    for subdir, dirs, files in os.walk(folder):
        for file in files:
            name = os.path.join(subdir, file)
            if "stats" in name:
                # print(name)
                dataframes.append(pd.read_csv(name, header=None))
    all = dataframes[0]

    for i in range(len(dataframes) - 1):
        all = pd.concat([all, dataframes[i+1]], axis=1, join="inner")

    return all

def meanMax(folder):

    maxList = []
    
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            name = os.path.join(subdir, file)
            if "stats" in name:
                df = pd.read_csv(name, header=None)
                maxList.append(df.max(axis=1))
    all = maxList[0]

    for i in range(len(maxList) - 1):
        all = pd.concat([all, maxList[i+1]], axis=1, join="inner")

    return all




def mutatePower(folder):
    powerList = [[], [], [], []]
    i = 0
    for subdir, dirs, files in os.walk(folder):
        # print(subdir)
        for dir in dirs:
            for file in files:
                name = os.path.join(subdir, file)
                if i > 7:
                    if "08\\2023" in subdir:
                        if "stats" in name:
                            df = pd.read_csv(name, header=None)
                            powerList[0].append(df.max(axis=1))
                    if "16\\2023" in subdir:
                        if "stats" in name:
                            df = pd.read_csv(name, header=None)
                            powerList[1].append(df.max(axis=1))
                    if "24\\2023" in subdir:
                        if "stats" in name:
                            df = pd.read_csv(name, header=None)
                            powerList[2].append(df.max(axis=1))
                    if "32\\2023" in subdir:
                        if "stats" in name:
                            df = pd.read_csv(name, header=None)
                            powerList[3].append(df.max(axis=1))
                i += 1


    all0 = powerList[0][0]
    for i in range(len(powerList[0]) - 1):
        all0 = pd.concat([all0, powerList[0][i+1]], axis=1, join="inner")

    all1 = powerList[1][0]
    for i in range(len(powerList[1]) - 1):
        all1 = pd.concat([all1, powerList[1][i+1]], axis=1, join="inner")

    all2 = powerList[2][0]
    for i in range(len(powerList[2]) - 1):
        all2 = pd.concat([all2, powerList[2][i+1]], axis=1, join="inner")

    all3 = powerList[3][0]
    for i in range(len(powerList[3]) - 1):
        all3 = pd.concat([all3, powerList[3][i+1]], axis=1, join="inner")

    print(all0)

    dfList = [all0, all1, all2, all3]
    legendList = ["08", "16", "24", "32"]
    plotAll(dfList, len(dfList), legendList, True)




loc = r"runs\1\CTRNN\SDP"


rootList = [loc + r"\\02", loc + r"\\04" , loc + r"\\08", loc + r"\\16", loc + r"\\24", loc + r"\\32", loc + r"\\48", loc + r"\\60"]
legendList = ["mutateRate = 2%", "mutateRate = 4%", "mutateRate = 8%", "mutateRate = 16%", "mutateRate = 24%", "mutateRate = 32%", "mutateRate = 40%", "mutateRate = 60%", "mutateRate = 48%", "mutateRate = 48%"]

rootList = [loc + r"\\1", loc + r"\\10" , loc + r"\\20", loc + r"\\30", loc + r"\\40", loc + r"\\50"]
legendList = ["SDP = 1", "SDP = 10", "SDP = 20", "SDP = 30", "SDP = 40", "SDP = 50"]


# rootList = [r"runs\1\CTRNN\Mutate", r"runs\1\CTRNN\1", r"runs\1\CTRNN\2"] #, r"runs\1\CTRNN\2", r"runs\1\CTRNN\3", r"runs\1\CTRNN\4"]
# legendList = ["Mutate", "1", "2", "4"]

# mutatePower(loc)


# mutatePower(loc)

dfList = []
for root in rootList:
    dfList.append(meanMax(root))


plotAll(dfList, len(rootList), legendList, True)

