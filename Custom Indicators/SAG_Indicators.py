import pandas as pd
import numpy as np
from tapy import Indicators


class Williams_Alligator_Indicators:

    def alligator_jaws(df: pd.DataFrame, period_jaws_=13, shift_jaws_=8):
        df = df.reset_index()
        df['Date'] = [d.date() for d in df['index']]
        df['Time'] = [d.time() for d in df['index']]
        i = Indicators(df)
        i.alligator(period_jaws=period_jaws_, period_teeth=8,
                    period_lips=5, shift_jaws=shift_jaws_,
                    shift_teeth=5, shift_lips=3,
                    column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth',
                    column_name_lips='alligator_lips')
        df = i.df
        df = df.drop(
            columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'alligator_teeth', 'alligator_lips'])
        df: pd.DataFrame = df.set_index('index')
        df.index.name = None

        return df

    def alligator_teeth(df: pd.DataFrame, period_teeth_=8, shift_teeth_=5):
        df = df.reset_index()
        df['Date'] = [d.date() for d in df['index']]
        df['Time'] = [d.time() for d in df['index']]
        i = Indicators(df)
        i.alligator(period_jaws=13, period_teeth=period_teeth_,
                    period_lips=5, shift_jaws=8,
                    shift_teeth=shift_teeth_, shift_lips=3,
                    column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth',
                    column_name_lips='alligator_lips')
        df = i.df
        df = df.drop(
            columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'alligator_jaw', 'alligator_lips'])
        df: pd.DataFrame = df.set_index('index')
        df.index.name = None

        return df

    def alligator_lips(df: pd.DataFrame, period_lips_=5, shift_lips_=3):
        df = df.reset_index()
        df['Date'] = [d.date() for d in df['index']]
        df['Time'] = [d.time() for d in df['index']]
        i = Indicators(df)
        i.alligator(period_jaws=13, period_teeth=8,
                    period_lips=period_lips_, shift_jaws=8,
                    shift_teeth=5, shift_lips=shift_lips_,
                    column_name_jaws='alligator_jaw', column_name_teeth='alligator_teeth',
                    column_name_lips='alligator_lips')
        df = i.df
        df = df.drop(
            columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'alligator_jaw', 'alligator_teeth'])
        df: pd.DataFrame = df.set_index('index')
        df.index.name = None

        return df

    def fractals(df: pd.DataFrame):
        df = df.reset_index()
        df['Date'] = [d.date() for d in df['index']]
        df['Time'] = [d.time() for d in df['index']]
        i = Indicators(df)
        i.fractals(column_name_high='fractals_high', column_name_low='fractals_low')
        df = i.df

        # replacing value based on condition:
        df.loc[df['fractals_high'] == True, 'fractals_high'] = df['High'] + (df['High'] * 0.001)
        df.loc[df['fractals_high'] == False, 'fractals_high'] = np.nan
        df.loc[df['fractals_low'] == True, 'fractals_low'] = df['Low'] - (df['Low'] * 0.001)
        df.loc[df['fractals_low'] == False, 'fractals_low'] = np.nan

        df = df.drop(columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df: pd.DataFrame = df.set_index('index')
        df.index.name = None

        return df

    def awesome_osc(df: pd.DataFrame):
        df = df.reset_index()
        df['Date'] = [d.date() for d in df['index']]
        df['Time'] = [d.time() for d in df['index']]
        i = Indicators(df)
        i.accelerator_oscillator(column_name='awesome_osc')
        df = i.df
        df = df.drop(columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df: pd.DataFrame = df.set_index('index')
        df.index.name = None

        return df

    def awesome_osc_abs(df: pd.DataFrame):
        df = df.reset_index()
        df['Date'] = [d.date() for d in df['index']]
        df['Time'] = [d.time() for d in df['index']]
        i = Indicators(df)
        i.accelerator_oscillator(column_name='awesome_osc_abs')
        df = i.df
        df = df.drop(columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['awesome_osc_abs'] = df['awesome_osc_abs'].abs()
        df: pd.DataFrame = df.set_index('index')
        df.index.name = None

        return df
