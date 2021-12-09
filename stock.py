import datetime
import pathlib
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import pandas as pd
import yfinance as yf

# for business day
from pandas.tseries.offsets import BDay

plt.style.use("dark_background")
# ----------
#  CONFIG
# ----------
ymd_format = '%Y-%m-%d'
font_family = "Monaco"
color_positive = "springgreen"
color_negative = "orangered"

# ----------
# Memo
# ----------


class StockAnimation:
    def __init__(self, stock):
        self.stock = stock
        self.datasets = stock.get_idx_vs_price_list(stock.stock_df)

        # list for animation chart
        self.x = []
        self.y = []
        # For calculation
        self.base_price = stock.get_base_price()
        self.price_list = [price for idex, price in self.datasets]
        self.datasets_num = len(self.datasets)
        self.price_min = min(min(self.price_list), self.base_price)
        self.price_max = max(max(self.price_list), self.base_price)
        self.current_price = float(self.price_list[0])
        self.fluctuation = 0

        # figure
        self.y_top = self.price_max + \
            int((self.price_max - self.price_min) * 0.20)
        self.y_bot = self.price_min - \
            int((self.price_max - self.price_min) * 0.04)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.line, = self.ax.plot([], [], color="white")
        self.axhline = self.ax.axhline(
            y=self.base_price, xmin=0, xmax=self.datasets_num, color="red", alpha=0.5, linewidth=2)
        self.title = self.ax.set_title(
            None, fontsize=24, fontfamily=font_family)
        self.text_info = self.ax.text(
            1, 0.95, None, fontsize=12, alpha=0.8,
            transform=self.ax.transAxes, va="center", ha="right",
            fontfamily=font_family)
        self.text_rate = self.ax.text(
            0.8, 0.5, None, fontsize=96,
            transform=self.ax.transAxes, va="center", ha="right", alpha=0.9,
            fontfamily=font_family, color='white')

    def init_ax_style(self):
        # initialize graph area
        self.ax.set_xlim(0, self.datasets_num)
        self.ax.set_ylim(self.y_bot, self.y_top)
        self.ax.tick_params(labelsize=18,)
        del (self.x[:], self.y[:])
        self.title.set_text(
            "NASDAQ100 INDEX ({})".format(self.stock.get_title()))
        self.text_info.set_text(None)
        self.ax.xaxis.set_visible(False)
        return self.line,

    def update_fluctuation(self):
        self.fluctuation = (
            self.current_price / self.base_price - 1)

    def str_info(self):
        return "PREVIOUS CLOSE :${:.2f}\nCURRENT :${:.2f}".format(self.base_price, self.current_price)

    def str_rate(self):
        return "{:+.2%}".format(self.fluctuation)

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

    def animate(self, show_chart=True, save_anime=True, save_dir='', file_name=''):
        print("Start animation.")
        self.anime = animation.FuncAnimation(
            self.fig, self.update, frames=range(self.datasets_num), interval=30, init_func=self.init_ax_style, repeat=False)

        if save_anime:
            file_name = file_name if file_name != '' else datetime.datetime.now().strftime(
                '{}_%Y-%m-%d_%H%M%S.mp4'.format(stock.get_code()))
            file_name = re.sub(r'[\\/:*?"<>|^]+', '', file_name)
            save_dir = save_dir if save_dir != '' else '/anime'
            save_path = pathlib.Path(save_dir) / file_name
            print('save_path:', save_path)
            self.anime.save(str(save_path),
                            writer="ffmpeg", fps=30)  # fpsはデフォルトの5
        elif show_chart:
            plt.show()
            plt.close()


class Stock:
    def __init__(self, code, title):
        self.code = code
        self.title = title
        self.bdays = BDay()

    def get_code(self):
        return self.code

    def get_title(self):
        return self.title

    def download_stock_data_from_period(self, period, interval):
        print(" >>> Downloading stock data ... ")
        print('period:{}\tinterval:{}'.format(
            period, interval))
        try:
            stock_df = yf.download(
                self.code, period=period, interval=interval)
        except e:
            print("Download Error.")
        print(" <<< Complete.")
        return stock_df

    def download_stock_data_from_date(self, start_ymd, end_ymd, interval):
        print(" >>> Downloading stock data ... ")
        print('start:{}\tend:{}\tinterval:{}'.format(
            start_ymd, end_ymd, interval))

        try:
            stock_df = yf.download(
                self.code, start=start_ymd, end=end_ymd, interval=interval)
        except e:
            print("Download Error.")
        print(" <<< Complete.")
        return stock_df

    def get_idx_vs_price_list(self, stock_df):
        # ls = [[idx, price], [idx, price] ,...]
        idx_vs_price = [[0, stock_df.iloc[0]["Open"]]]
        idx = 1
        for row in stock_df[["Open", "Close"]].itertuples():
            idx_vs_price.append([idx, row.Close])
            idx = idx + 1
        idx_vs_price.append([idx, self.get_close_price()])
        return idx_vs_price

    def change_index_ts_to_str(self, stock_df):
        tmp_stock_df = stock_df.rename(
            columns=str, index=lambda x: x.strftime(ymd_format))
        # print('renamed stock_df \n', tmp_stock_df.index)
        return tmp_stock_df

    def get_businessday_add_x_days(self, ymd_str, x=1):
        ymd_datetime = datetime.datetime.strptime(ymd_str, ymd_format)
        bday_ymd = (ymd_datetime + BDay(x)).strftime(ymd_format)
        return bday_ymd

    def is_businessday(self, ymd_str):
        ymd_datetime = datetime.datetime.strptime(ymd_str, ymd_format)

        return self.bdays.is_on_offset(ymd_datetime)

    def update_title(self, title):
        self.title = title


class Stock_1d(Stock):
    def __init__(self, code="", period="1d", interval="1m", title=''):
        super().__init__(code, title)
        self.period = period
        self.interval = interval
        # 1st. 1d interval stock df
        # 2nd. 2m interval stock df for target-ymd
        self.daily_stock_df = self.change_index_ts_to_str(
            self.download_stock_data_from_period(period="7d", interval="1d"))
        self.stock_df = self.download_stock_data_from_period(
            period, interval)

        self.base_ymd = self.get_base_date()
        self.current_date = self.get_current_date()
        self.update_title(self.current_date)

    def get_base_date(self):
        base_date = self.stock_df.index[0].to_pydatetime(
        ) - datetime.timedelta(days=1)
        return base_date.strftime("%Y-%m-%d")

    def get_current_date(self):
        return self.stock_df.index[0].strftime("%Y-%m-%d")

    def get_base_price(self):
        return float(self.daily_stock_df.loc[self.base_ymd]["Close"])

    def get_close_price(self):
        return float(self.daily_stock_df.loc[self.get_current_date()]["Close"])


class Stock_specific(Stock):
    def __init__(self, code, start_ymd, end_ymd, interval, title=''):
        super().__init__(code, title)
        print('---------')
        print('[target-date] start:{}\tend:{}'.format(start_ymd, end_ymd))
        print('---------')
        print('start_ymd is businessday:', self.is_businessday(start_ymd))
        print('end_ymd is businessday:', self.is_businessday(end_ymd))
        self.start_ymd = start_ymd if self.is_businessday(
            start_ymd) else self.get_businessday_add_x_days(start_ymd, -1)
        self.end_ymd = end_ymd if self.is_businessday(
            end_ymd) else self.get_businessday_add_x_days(end_ymd, +1)
        print(end_ymd == datetime.datetime.now().strftime(ymd_format))
        if end_ymd == datetime.datetime.now().strftime(ymd_format):
            self.end_ymd = self.get_businessday_add_x_days(end_ymd, -1)

        print('start_ymd \t: {}\t to self.start_ymd \t: {}'.format(
            start_ymd, self.start_ymd))
        print('end_ymd \t: {}\t to self.end_ymd \t: {}'.format(
            end_ymd, self.end_ymd))

        self.start_ymd_expand = self.get_businessday_add_x_days(
            self.start_ymd, -1)
        self.end_ymd_expand = self.get_businessday_add_x_days(
            self.end_ymd, +1)
        # update title
        self.update_title('{} to {}'.format(self.start_ymd, self.end_ymd))

        self.base_ymd = self.start_ymd_expand
        self.interval = interval
        self.stock_df = self.download_stock_data_from_date(
            self.start_ymd_expand, self.end_ymd_expand, interval)
        self.daily_stock_df = self.change_index_ts_to_str(self.download_stock_data_from_date(
            self.start_ymd, self.end_ymd_expand, "1d"))

    def get_base_price(self):
        return float(self.daily_stock_df.loc[self.base_ymd]['Close'])

    def get_base_date(self):
        return self.base_ymd

    def get_close_price(self):
        return float(self.daily_stock_df.loc[self.end_ymd]["Close"])


def main():
    stock = Stock_1d(code="^NDX", period="1d", interval="2m", title='')
    # stock = Stock_specific('^NDX', '2021-10-10', '2021-12-04', '1h')
    anime = StockAnimation(stock)
    return


if __name__ == "__main__":
    main()
