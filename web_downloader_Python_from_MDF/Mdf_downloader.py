import io  # библиотека, которая позволяет работать с буфером обмена Windows
import requests
import pandas as pd
import inspect
import datetime as dt


end_date = dt.date.today()
st_date = end_date - dt.timedelta(days=30)



def get_ticker_df():
    """
    This function get ticker table
    :return: df of available tickers
    """
    ticker_df = pd.DataFrame({"Number": ['225*', '82*', '33*', '45*', '39*', '220*', '122*', '5*'],
                             "Ticker": ['GMKN', 'SBRF', 'GAZR', 'MTSI', 'LKOH', 'MGNT', 'USRU', 'RTS_']})
    return ticker_df

def refine_df(df):
    """ Internal function get df refined"""
    # обработка df < ----------------------------------------------------------------------------
    df['<DATE>'] = df['<DATE>'].map(str)
    df['<TIME>'] = df['<TIME>'].map(str)
    df['DateTime'] = df['<DATE>'] + " " + df['<TIME>']
    # reformating date and time
    df['DateTime'] = pd.to_datetime(df['DateTime'], format="%Y%m%d %H%M%S")
    # drop unnecessary columns
    df.drop(['<TICKER>', '<PER>', '<DATE>', '<DATE>', '<TIME>', '<OPENINT>'], axis=1)
    # swap places
    columns_titles = ["DateTime", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>", "<VOL>"]
    df = df.reindex(columns=columns_titles)
    df = df.rename(
         columns={"DateTime": "DateTime", "<OPEN>": "Open", "<HIGH>": "High", "<LOW>": "Low", "<CLOSE>": "Close",
                  "<VOL>": "Volume"})
    df = df.set_index('DateTime')
    df.index.name = None
    # обработка df > ----------------------------------------------------------------------------
    return df
    
    

def get_market_quotes(ticker="SBRF", timeframe=1, date_start=st_date, data_end=end_date):
    """
    Function get market_quotes in proper format
	:param ticker: type str. Four capital letters which is searched in tickers df
	:param timeframe: timeframe
	:param date_start: type str if inputting manually, without time
	:param data_end: type str if inputting manually, without time
	:return: pandas dataframe with quotes of selected ticker for selected time array
	"""

    ticker_code  = get_ticker_df().query(f"Ticker == '{ticker}'")['Number'].values[0]

    if not isinstance(date_start, str):
        x_day = str(date_start.day) if len(str(date_start.day)) == 2 else '0'+ str(date_start.day)
        x_mon = str(date_start.month) if len(str(date_start.month)) == 2 else '0'+ str(date_start.month)
        date_start = x_day + '.' + x_mon + '.' + str(date_start.year)

        x_day = str(data_end.day) if len(str(data_end.day)) == 2 else '0'+ str(data_end.day)
        x_mon = str(data_end.month) if len(str(data_end.month)) == 2 else '0'+ str(data_end.month)
        data_end =  x_day + '.' + x_mon + '.' + str(data_end.year)

    url = f"""http://mfd.ru/export/handler.ashx/?TickerGroup=&Tickers={ticker_code}&Alias=false&Period={timeframe}&timeframeValue={timeframe}&timeframeDatePart=day&StartDate={date_start}&EndDate={data_end}&SaveFormat=0&SaveMode=0&FileName=1&FieldSeparator=%253b&DecimalSeparator=.&DateFormat=yyyyMMdd&TimeFormat=HHmmss&DateFormatCustom=&TimeFormatCustom=&AddHeader=true&RecordFormat=0&Fill=false"""
    f = requests.get(url)

    data = io.StringIO(f.text)
    df = pd.read_csv(data, sep=";")

    return refine_df(df)
    
def write_market_quotes(ticker="SBRF", timeframe=1, date_start=st_date, data_end=end_date):
    """
    Function get market_quotes in proper format
	:param ticker: type str. Four capital letters which is searched in tickers df
	:param timeframe: timeframe
	:param date_start: type str if inputting manually, without time
	:param data_end: type str if inputting manually, without time
	:return: pandas dataframe with quotes of selected ticker for selected time array
	"""
    folder = r"C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\feed"
    file_name = "write_market_quotes_feed.csv"
    ticker_code = get_ticker_df().query(f"Ticker == '{ticker}'")['Number'].values[0]

    if not isinstance(date_start, str):
        x_day = str(date_start.day) if len(str(date_start.day)) == 2 else '0'+ str(date_start.day)
        x_mon = str(date_start.month) if len(str(date_start.month)) == 2 else '0'+ str(date_start.month)
        date_start = x_day + '.' + x_mon + '.' + str(date_start.year)

        x_day = str(data_end.day) if len(str(data_end.day)) == 2 else '0'+ str(data_end.day)
        x_mon = str(data_end.month) if len(str(data_end.month)) == 2 else '0'+ str(data_end.month)
        data_end =  x_day + '.' + x_mon + '.' + str(data_end.year)

    url = f"""http://mfd.ru/export/handler.ashx/?TickerGroup=&Tickers={ticker_code}&Alias=false&Period={timeframe}&timeframeValue={timeframe}&timeframeDatePart=day&StartDate={date_start}&EndDate={data_end}&SaveFormat=0&SaveMode=0&FileName=1&FieldSeparator=%253b&DecimalSeparator=.&DateFormat=yyyyMMdd&TimeFormat=HHmmss&DateFormatCustom=&TimeFormatCustom=&AddHeader=true&RecordFormat=0&Fill=false"""
    f = requests.get(url)

    data = io.StringIO(f.text)
    df = pd.read_csv(data, sep=";")

    df = refine_df(df)
    print(df)
    df.to_csv(folder + "\\" + file_name)

def get_quotes_from_folder(path_to_quotes):

    df = pd.read_csv(path_to_quotes, sep=";")
    df = refine_df(df)


if __name__ == '__main__':
    start_date = '01.07.2022'
    finish_date = '15.11.2022'

    write_market_quotes(ticker='GAZR',timeframe=2,date_start=start_date,data_end=finish_date)
    df = pd.read_csv(r"C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\feed\write_market_quotes_feed.csv")
    df['Unnamed: 0'] = pd.to_datetime(df['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S")
    df.set_index('Unnamed: 0', inplace = True)
    df.index.name = None
    print(df)
    input("нажмите любую кнопку")
