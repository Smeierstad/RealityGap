import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pickle

from lowpassClass import LowPass

fs = 1000
cutoff =200
order = 5

size = 100

b, a = signal.butter(order, cutoff / (fs/2), 'low')

buffer = []
for i in range(18):
    buffer.append(0)
xData = []
yData = []
x = np.zeros(size)

file = r"runs\2023_05_30_11_10_12_409770\gens\bestInv099"

plt.style.use('ggplot')


with open(file, 'rb') as f:
    ind = pickle.load(f)

controller = ind.getController()

controller.reset()
filterData = []


fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(-2, 2)
line, = ax.plot(0, 0)

lowpass = LowPass()

for i in range(100):
    newData = controller.advance(np.zeros(12))[4]

    filterData.append(lowpass.filter(newData))


def animate(i):
    line.set_ydata(filterData[i])
    return line,

    
# def animate(i):
#     line.set_ydata(np.sin(x+i/50))
#     return line,


# for i in range(size):
#     # newData = np.sin(i/2) + np.random.normal(0, 1)
#     newData = controller.advance(np.zeros(12))[4]
#     x[i] = newData

#     buffer.append(newData)
#     # print(buffer)

#     if i > 18:
#         filterData = signal.filtfilt(b, a, buffer)


# print(filterData)


ani = animation.FuncAnimation(fig, func=animate, frames=np.arange(0, 100, 1), interval = 10)


# plt.plot(x, label = "signal")
# plt.plot(filterData, label = "filter")

# plt.legend(loc="upper left")
plt.show()
