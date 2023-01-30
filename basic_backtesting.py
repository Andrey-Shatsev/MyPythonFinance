import sys

sys.path.insert(0,
                r'C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\Quotes '
                r'Getters\web_downloader_Python_from_MDF')
import Mdf_downloader as mdf

sys.path.insert(0,
                r'C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\Custom Indicators')
import SAG_Indicators as SAG_Indicators

sys.path.insert(0,
                r"C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\E-mailer\Yandex")
import YandexSender3 as YandexSender3

from backtesting import Strategy, Backtest
from backtesting.lib import crossover
import math
from contextlib import suppress

# optimization:
import time
import pandas as pd


class MainTrading:
    """В данном классе собираются параметры для стратегии, такие как таймфрейм,
    тикер, начальная дата, конечная дата и т.д."""
    def __init__(self, strategy_name, s_d: str, f_d: str,
                 ticker: str,
                 timeframe: int,
                 deposit_sum: float,
                 fee_rate: float,
                 stop_loss_max: float,
                 stop_loss_daily_limit: int):
        self.strategy_name = strategy_name
        self.s_d = s_d
        self.f_d = f_d
        self.ticker = ticker
        self.timeframe = timeframe
        self.deposit_sum = deposit_sum
        self.fee_rate = fee_rate
        self.stop_loss_max = stop_loss_max
        self.stop_loss_daily_limit = stop_loss_daily_limit

    def get_df(self):
        """Метод получает котировки по API"""
        df = pd.read_csv(r"C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\feed\write_market_quotes_feed.csv")
        df['Unnamed: 0'] = pd.to_datetime(df['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")
        df.set_index('Unnamed: 0', inplace = True)
        df.index.name = None
        return df
        #return mdf.get_market_quotes(ticker=self.ticker, timeframe=self.timeframe, date_start=self.s_d,
        #                         data_end=self.f_d) # ввиду того, что оптимизация.


class FirstStrategy(Strategy):
    """Данный клас содержит в себе конкнетную стратегию входа в позицию и выхода из нее.
     Правило входа: если позиция не открыта, тогда если есть пересечение линии челюсти с
     линией зубов аллигатора, либо пересечение линии челюсти и губ аллигатора и одновременно с этим выполняются условия:
     есть точка фрактала и не прошло № свечей (10 по умолчанию) со свечи пересечения, тогда вход в длинную позицию
     Правило выхода: если произошло пересечение цены закрытия кривой губ аллигатора."""

    # class variables:
    alligators_line_crossover_watch = 10
    osc_close_to_zero_threshold = 10
    confirm_trend_bars_check = 15

    period_jaws_ = 13
    period_teeth_ = 8
    period_lips_ = 5

    bars_cross_happened_long = 0
    bars_fractal_plus_low_osc_long = 0
    fractal_high_value = 0

    # ----------------- not for optimization parameters -----------------
    stop_loss_count = 0
    closed_trades_static = (0)

    # -------------------------------------------------------------------

    def check_positions(self, tuple_closed):
        # процедура проверки, выход прошел по sl либо по обычной сделке.
        with suppress(Exception):
            if tuple_closed[-1].pl <= -x.stop_loss_max:
                self.stop_loss_count += 1
                # print(
                #    f"stop-loss pl = {tuple_closed[-1].pl}, sl count = {self.stop_loss_count},"
                #    f" date = {tuple_closed[-1].exit_time}")

            # else:
            #    print(
            #        f"ordinal pl = {tuple_closed[-1].pl}, sl count = {self.stop_loss_count},"
            #        f" date = {tuple_closed[-1].exit_time}")

    def init(self):
        df_x = x.get_df()
        self.alligator_jaws = self.I(additional_indicators.alligator_jaws, df_x, self.period_jaws_, plot=True, overlay=True,
                                     color='#0000FF',
                                     name='allig_jaw')
        self.alligator_teeth = self.I(additional_indicators.alligator_teeth, df_x, self.period_teeth_, plot=True, overlay=True,
                                      color='#CB0F0F',
                                      name='allig_teeth')
        self.alligator_lips = self.I(additional_indicators.alligator_lips, df_x, self.period_lips_, plot=True, overlay=True,
                                     color='#20A429',
                                     name='allig_lips')
        self.fractals = self.I(additional_indicators.fractals, df_x, plot=True, overlay=True, color='#686868',
                               name='fractals',
                               scatter=True)
        self.awesome_osc = self.I(additional_indicators.awesome_osc, df_x, plot=True, overlay=False, color='#0000FF',
                                  name='awesome_osc')
        self.awesome_osc_abs = self.I(additional_indicators.awesome_osc_abs, df_x, plot=True, overlay=False,
                                      color='#20A429',
                                      name='awesome_osc_abs')

    def next(self):

        upper_fractal = self.fractals[0]

        if self.data.index[-1].day != self.data.index[-2].day:
            self.stop_loss_count = 0

        if not self.position.is_long and self.stop_loss_count < x.stop_loss_daily_limit:
            # для сделок long:

            if crossover(self.alligator_jaws[-1], self.alligator_teeth[-1]) or crossover(self.alligator_jaws[-1],
                                                                                         self.alligator_lips[-1]):
                self.bars_cross_happened_long = len(self.data.Close)

            if (len(self.data.Close) - self.bars_cross_happened_long) <= self.alligators_line_crossover_watch:
                if not math.isnan(upper_fractal[-1]) and self.awesome_osc_abs[-1] <= \
                        self.osc_close_to_zero_threshold and upper_fractal[-1] > self.alligator_teeth[-1]:
                    self.fractal_high_value = upper_fractal[-1]
                    self.bars_fractal_plus_low_osc_long = len(self.data.Close)

            if ((len(self.data.Close) - self.bars_fractal_plus_low_osc_long) <= self.confirm_trend_bars_check) \
                    and (self.data.Close[-1] > self.fractal_high_value):
                # nullifying variables
                self.bars_fractal_plus_low_osc_long = 0
                self.fractal_high_value = 0
                self.bars_cross_happened_long = 0

                price = self.data.Close[-1]
                self.buy(size=1, sl=(
                        price - x.stop_loss_max))

        else:
            if crossover(self.data.Close[-1], self.alligator_lips[-1]):
                self.position.close()

        with suppress(Exception):
            if self.closed_trades != self.closed_trades_static:
                self.check_positions(self.closed_trades)
                self.closed_trades_static = self.closed_trades


# get custom indicators: получение индикаторов из внешнего модуля
additional_indicators = SAG_Indicators.Williams_Alligator_Indicators

# settings for testing:
start_date = '15.10.2022'
finish_date = '15.11.2022'

# light database management - getting fee rate:


x = MainTrading(f"GAZR - Alligator_plus_fractal {start_date}-{finish_date}", start_date, finish_date, ticker='GAZR',
                timeframe=2, fee_rate=0.00039443659676192543,
                deposit_sum=100000, stop_loss_max=200, stop_loss_daily_limit=2)


# OPTIMIZATION FUNCS:
def save_optimization_matrix(dataframe_):
    file_path = r'C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\__Optimization\Approach\Results'
    file_name = x.strategy_name + ".csv"
    full_path = file_path + "\\" + file_name
    dataframe_.to_csv(full_path)


def send_notification_via_email(email, number_of_strategies, time):
    theme = f'Завершена оптимизация: {x.strategy_name}'

    text = f"Внимание! " \
           f"Была завершена оптимизация стратегии {x.strategy_name}. " \
           f"В результате было проверено {number_of_strategies} вариаций стратегии." \
           f" Оптимизация заняла - {time}"

    YandexSender3.send_notification([email],theme,text)




if __name__ == "__main__":
    bt = Backtest(x.get_df(), FirstStrategy, cash=x.deposit_sum, commission=x.fee_rate * 2)
    # stat = bt.run()

    start_time = time.perf_counter()

    stats, df = bt.optimize(period_jaws_=range(6, 80, 2),
                            period_teeth_=range(4, 60, 2),
                            period_lips_=range(2, 46, 2),
                            alligators_line_crossover_watch = range(4, 100, 2),
                            confirm_trend_bars_check=range(2, 50, 2),
                            osc_close_to_zero_threshold=range(2, 40, 2),
                            maximize='Equity Final [$]',
                            return_heatmap=True,
                            max_tries = 1500)

    save_optimization_matrix(df)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    send_notification_via_email('TradingRobots.mail@yandex.ru', df.shape[0], f'{total_time / 60:.0f} мин.')

    print(stats)
    print(f"Strategies count: {df.shape[0]}")
    print(f'Optimization took {total_time / 60:.1f} minutes')
    # print(stat['_trades'])
    # stat['_trades'].to_excel(r"C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\log.xlsx")
    # print(stat)
    # bt.plot()
    # print("\nCurrency is Russian Rubles")
