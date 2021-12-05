import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import pandas as pd
import yfinance as yf


class Animation():
    def __init__(self, datasets=[]):
        self.datasets = datasets
        # list for animation chart
        self.x = []
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
            print("Stop animation")
        else:
            x, y = self.datasets.pop(0)
            self.x.append(x)
            self.y.append(y)
        # show plot
        plt.plot(self.x, self.y)

    def animate(self):
        print9 = ("Start animation.")
        self.anime = animation.FuncAnimation(
            self.fig, self.AnimationUpdater, interval=100)
        plt.show()


class Stock:
    def __init__(self, code="", period="7d", interval="15m"):
        self.code = code
        self.period = period
        self.interval = interval

        self.stock_df = self.download_stock_data()

    def download_stock_data(self):
        print("Downloading stock data ... ")
        try:
            stock_df = yf.download(
                self.code, period=self.period, interval=self.interval)
        except e:
            print("Download Error.")
        print("Complete.")
        return stock_df

    def get_idx_vs_price_list(self):
        # ls = [[idx, price], [idx, price] ,...]
        idx_vs_price = [[0, self.stock_df.iloc[0]["Open"]]]
        idx = 1
        for row in self.stock_df[["Open", "Close"]].itertuples():
            idx_vs_price.append([idx, row.Close])
            idx = idx + 1
        return idx_vs_price


def main():
    stock = Stock(code="^NDX", period="1d", interval="5m")
    datasets = stock.get_idx_vs_price_list()
    anime = Animation(datasets)


if __name__ == "__main__":
    main()
