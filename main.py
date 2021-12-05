import datetime

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import pandas as pd
import yfinance as yf

plt.style.use('dark_background')


class Animation():
    def __init__(self, datasets=[], yesterday_close_price=0):
        self.datasets = datasets

        # list for animation chart
        self.x = []
        self.y = []
        # For calculation
        self.yesterday_close_price = yesterday_close_price
        self.price_list = [price for idex, price in datasets]
        self.datasets_num = len(self.datasets)
        self.price_min = min(self.price_list)
        self.price_max = max(self.price_list)
        self.open_price = float(self.price_list[0])
        self.current_price = self.open_price
        self.fluctuation = 0

        # fig
        self.y_top = self.price_max + \
            int((self.price_max - self.price_min) * 0.20)
        self.y_bot = self.price_min - \
            int((self.price_max - self.price_min) * 0.04)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [])
        self.title = self.ax.set_title(
            'NASDAQ100 INDEX', fontsize=24, fontfamily="Arial")
        self.text_info = self.ax.text(
            1, 1, None, fontsize=12,
            transform=self.ax.transAxes, va='top', ha="right",
            fontfamily="Arial", bbox=dict(boxstyle='square', fc=self.get_fluctuation_color()),)
       # start animation
        self.animate()

    def init_ax_style(self):
        # initialize graph area
        self.ax.set_xlim(0, self.datasets_num)
        self.ax.set_ylim(self.y_bot, self.y_top)
        self.ax.tick_params(labelsize=18,)
        del (self.x[:], self.y[:])
        self.title.set_text("NASDAQ100 INDEX")
        self.text_info.set_text(None)
        self.text_info.set_bbox(dict(fc=self.get_fluctuation_color()))
        self.ax.xaxis.set_visible(False)
        return self.line,

    def update_fluctuation(self):
        self.fluctuation = (
            self.current_price / self.yesterday_close_price - 1)

    def str_info(self):
        return 'Before:${:.2f}, Now:${:.2f}, Rate:{:+.2%}'.format(self.yesterday_close_price, self.current_price, self.fluctuation)

    # def str_info(self):
    #     return 'Rate:{:.2%}'.format(self.fluctuation)

    def get_fluctuation_color(self):
        return 'tomato' if self.fluctuation <= 0 else 'seagreen'

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
        self.text_info.set_bbox(dict(fc=self.get_fluctuation_color()))

        return self.line,

    def animate(self):
        print("Start animation.")
        self.anime = animation.FuncAnimation(
            self.fig, self.update, frames=range(self.datasets_num), interval=30, init_func=self.init_ax_style, repeat=False)
        self.anime.save('test-anime.mp4',
                        writer='ffmpeg')  # fpsはデフォルトの5

        # plt.show()
        # plt.close()


class Stock:
    def __init__(self, code="", period="1d", interval="1m"):
        self.code = code
        self.period = period
        self.interval = interval

        self.todays_stock_df = self.download_stock_data_from_period(
            code, period, interval)
        # get todays close price(1m stock_df has wrong data)
        self.todays_stock_df_1d = self.download_stock_data_from_period(
            code, "1d", "1d")
        # get yesterdays stock_df
        cur_date, one_week_ago = self.get_date_x_ago(0), self.get_date_x_ago(7)
        self.to_yesterdays_stock_df_1d = self.download_stock_data_from_date(
            code, one_week_ago, cur_date, "1d")

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

    def get_date_x_ago(self, ago=0):
        cur_datetime = self.todays_stock_df.index[0]
        ago_datetime = cur_datetime - datetime.timedelta(days=ago)

        cur_date_str = cur_datetime.strftime("%Y-%m-%d")
        ago_datetime_str = ago_datetime.strftime("%Y-%m-%d")
        return ago_datetime_str

    def get_yesterday_last_price(self):

        return float(self.to_yesterdays_stock_df_1d.iloc[-1:]["Close"])

    def get_todays_last_price(self):
        return float(self.todays_stock_df_1d.iloc[0]["Close"])

    def get_idx_vs_price_list(self):
        # ls = [[idx, price], [idx, price] ,...]
        idx_vs_price = [[0, self.todays_stock_df.iloc[0]["Open"]]]
        idx = 1
        for row in self.todays_stock_df[["Open", "Close"]].itertuples():
            idx_vs_price.append([idx, row.Close])
            idx = idx + 1
        idx_vs_price.append([idx, self.get_todays_last_price()])
        print(idx, self.get_todays_last_price())
        return idx_vs_price


def main():
    stock = Stock(code="^NDX", period="1d", interval="2m")
    datasets = stock.get_idx_vs_price_list()
    yesterday_close_price = stock.get_yesterday_last_price()

    anime = Animation(datasets, yesterday_close_price)


if __name__ == "__main__":
    main()
