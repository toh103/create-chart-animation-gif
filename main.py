import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class Animation():
    def __init__(self, datasets=[0, ]):
        self.datasets = datasets
        # list for animation chart
        self.y = []
        self.fig = plt.figure()
        # start animation
        self.animate()

    def AnimationUpdater(self, frame):
        # clear plot
        plt.cla()
        if len(self.datasets) <= 0:
            # stop animation
            self.anime.event_source.stop()
        else:
            value = self.datasets.pop()
            self.y.append(value)
        # show plot
        plt.plot(self.y)

    def animate(self):
        self.anime = animation.FuncAnimation(
            self.fig, self.AnimationUpdater, interval=100)
        plt.show()


def main():
    datasets = [int(np.random.rand() * 20) for i in range(20)]
    anime = Animation(datasets)


if __name__ == '__main__':
    main()
