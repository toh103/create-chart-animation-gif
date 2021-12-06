import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import pandas as pd
import yfinance as yf

plt.style.use("dark_background")
# ----------
#  CONFIG
# ----------
font_family = "Monaco"
color_positive = "springgreen"
color_negative = "orangered"


class StockAnimation:
    def __init__(self, stock):
        self.stock = stock
        self.datasets = stock.get_idx_vs_price_list()

        # list for animation chart
        self.x = []
        self.y = []
        # For calculation
        self.yesterday_close_price = stock.get_yesterday_close_price()
        self.price_list = [price for idex, price in self.datasets]
        self.datasets_num = len(self.datasets)
        self.price_min = min(self.price_list)
        self.price_max = max(self.price_list)
        self.current_price = float(self.price_list[0])
        self.fluctuation = 0

        print(stock.get_todays_date())

        # fig
        self.y_top = self.price_max + \
            int((self.price_max - self.price_min) * 0.20)
        self.y_bot = self.price_min - \
            int((self.price_max - self.price_min) * 0.04)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [])
        self.title = self.ax.set_title(
            None, fontsize=24, fontfamily=font_family)
        self.text_info = self.ax.text(
            1, 0.95, None, fontsize=12, alpha=0.8,
            transform=self.ax.transAxes, va="center", ha="right",
            fontfamily=font_family)
        self.text_rate = self.ax.text(
            0.5, 0.5, None, fontsize=96,
            transform=self.ax.transAxes, va="center", ha="center", alpha=0.7,
            fontfamily=font_family, color='white')
       # start animation
        self.animate()

    def init_ax_style(self):
        # initialize graph area
        self.ax.set_xlim(0, self.datasets_num)
        self.ax.set_ylim(self.y_bot, self.y_top)
        self.ax.tick_params(labelsize=18,)
        del (self.x[:], self.y[:])
        self.title.set_text(
            "NASDAQ100 INDEX ({})".format(self.stock.get_todays_date()))
        self.text_info.set_text(None)
        self.ax.xaxis.set_visible(False)
        return self.line,

    def update_fluctuation(self):
        self.fluctuation = (
            self.current_price / self.yesterday_close_price - 1)

    def str_info(self):
        return "PREVIOUS CLOSE :${:.2f}\nCURRENT :${:.2f}".format(self.yesterday_close_price, self.current_price)

    def str_rate(self):
        return "{:.2%}".format(self.fluctuation)
    # def str_info(self):
    #     return "Rate:{:.2%}".format(self.fluctuation)

    def get_fluctuation_color(self):
        return color_negative if self.fluctuation <= 0 else color_positive

    def update(self, frame):
        # update graph area
        x, y = self.datasets.pop(0)
        self.x.append(x)
        self.y.append(y)

        self.line.set_data(self.x, self.y)

        # update fluctuation
        self.current_price = y
        self.update_fluctuation()
        self.text_info.set_text(self.str_info())
        self.text_rate.set_text(self.str_rate())
        self.text_rate.set_color(self.get_fluctuation_color())

        return self.line,

    def animate(self):
        print("Start animation.")
        self.anime = animation.FuncAnimation(
            self.fig, self.update, frames=range(self.datasets_num), interval=30, init_func=self.init_ax_style, repeat=False)
        # self.anime.save("test-anime.mp4",
        #                 writer="ffmpeg")  # fpsはデフォルトの5

        plt.show()
        plt.close()


class Stock:
    def __init__(self, code="", period="1d", interval="1m"):
        self.code = code
        self.period = period
        self.interval = interval
        # 1st. 1d interval stock df
        # 2nd. 2m interval stock df for target-ymd
        self.oneday_interval_stock_df = self.download_stock_data_from_period(
            code=code, period="7d", interval="1d")
        self.todays_stock_df = self.download_stock_data_from_period(
            code, period, interval)

    def download_stock_data_from_period(self, code, period, interval):
        print("Downloading stock data ... ")
        try:
            stock_df = yf.download(
                code, period=period, interval=interval)
        except e:
            print("Download Error.")
        print("Complete.")
        return stock_df

    def download_stock_data_from_date(self, code, start, end, interval):
        print("Downloading stock data ... ")
        try:
            stock_df = yf.download(
                code, start=start, end=end, interval=interval)
        except e:
            print("Download Error.")
        print("Complete.")
        return stock_df

    def get_yesterday_close_price(self):
        return float(self.oneday_interval_stock_df.iloc[-2]["Close"])

    def get_todays_close_price(self):
        return float(self.oneday_interval_stock_df.iloc[-1]["Close"])

    def get_todays_date(self):
        return self.todays_stock_df.index[0].strftime("%Y/%m/%d")

    def get_idx_vs_price_list(self):
        # ls = [[idx, price], [idx, price] ,...]
        idx_vs_price = [[0, self.todays_stock_df.iloc[0]["Open"]]]
        idx = 1
        for row in self.todays_stock_df[["Open", "Close"]].itertuples():
            idx_vs_price.append([idx, row.Close])
            idx = idx + 1
        idx_vs_price.append([idx, self.get_todays_close_price()])
        print(idx, self.get_todays_close_price())
        return idx_vs_price


def get_recent_workday():
    return datetime.datetime.now().strftime("%Y-%M-$d")


def main():
    stock = Stock(code="^NDX", period="1d", interval="2m")
    anime = StockAnimation(stock)


if __name__ == "__main__":
    main()
