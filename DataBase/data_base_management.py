import pandas as pd
import sqlite3
from datetime import datetime


class SAG_DataBaseManagement:
    """
    description: Class helps to operate with specified database.
    """

    __ex_path = r"C:\Users\user\Dropbox\Business\2. Financial markets\Python Tester\DataBase\TradePreferences - обновление.xlsx"

    def __init__(self, db_name: str = "mock_trading.db"):
        """
        instance initialization method
        @param db_name: path to database working with
        """
        self.db_name = db_name

    def tables_name(self):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        req = """
            SELECT 
                name
            FROM 
                sqlite_schema
            WHERE 
                type ='table' AND 
                name NOT LIKE 'sqlite_%';
        """
        cursor.execute(req)
        print(cursor.fetchall())
        con.commit()
        con.close()

    def read_data(self, table: str = "TradePreferences"):
        # позволяет получить df из базы данных - его можно обработать
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute("SELECT * FROM {};".format(table))
        list_of_tuples = cursor.fetchall()

        cursor.execute("PRAGMA table_info({});".format(table))
        list_of_columns = []
        columns_data = cursor.fetchall()  # тут нужно доставать из листа кортежей второй элемент кортежа
        for _, column in enumerate(columns_data):
            list_of_columns.append(column[1])
        df = pd.DataFrame(list_of_tuples, columns=list_of_columns)
        pd.set_option('display.expand_frame_repr', False)  # отображать весь набор данных
        con.commit()
        con.close()
        return df


    def print_data(self, table: str = "TradePreferences"):
        # позволяет получить df из базы данных - его можно обработать
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute("SELECT * FROM {};".format(table))
        list_of_tuples = cursor.fetchall()

        cursor.execute("PRAGMA table_info({});".format(table))
        list_of_columns = []
        columns_data = cursor.fetchall()  # тут нужно доставать из листа кортежей второй элемент кортежа
        for _, column in enumerate(columns_data):
            list_of_columns.append(column[1])
        df = pd.DataFrame(list_of_tuples, columns=list_of_columns)
        pd.set_option('display.expand_frame_repr', False)  # отображать весь набор данных
        print(df)
        con.commit()
        con.close()


    def alter_of_table(self):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute('ALTER TABLE TradingTable ADD BotOperationID REAL')
        #'ALTER TABLE TradePreferences ADD BotOperationID REAL'
        #'ALTER TABLE TradePreferences DROP COLUMN BotOperationID'

        con.commit()
        con.close()

    def deleting(self, table):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute(f'DELETE FROM {table}')
        con.commit()
        con.close()


    def insert_records_from_excel_table(self, excel_path: str = __ex_path, replace_data_in_table:bool = False):
        """
                                        , db_table: str,
                                        replace_data_in_table: bool)

        The method takes excel table path in order to insert
        records in specified database, and table.
        @param db_table: string. Specified table in data base
        @param excel_path: string. Path to excel table. first sheet.
        @param replace_data_in_table:

        an example of proper excel table to operate with:
            A           B           C           D   E
        1
        2   Name        Age         Gender
        3   Alex        15          Male
        4   Andrew      21          Male
        5   Elly        18          Female
        6

        params: headers_row = 2, values_row = 3.
        """

        if replace_data_in_table:
            self.deleting('TradePreferences')

        df = pd.read_excel(excel_path)
        temp_list = list(df.itertuples(index=False, name=None))

        # -------------------------------------------------------------------------------------
        #                                   Execution
        # -------------------------------------------------------------------------------------
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        for tuple_ in temp_list:
            cursor.execute(f'''
                INSERT INTO TradePreferences VALUES {tuple_};
            ''')
        con.commit()
        con.close()

        # -------------------------------------------------------------------------------------

    def drop_table(self, table_name: str):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute(f'DROP TABLE {table_name}')
        con.commit()
        con.close()

    def create_table(self, table_name: str):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        req = f"""
        CREATE TABLE {table_name} (
            BotOperationID REAL,
            OperationType TEXT,
            TradingType TEXT,
            RobotName TEXT,
            StrategyName TEXT,
            Tiker TEXT,
            Timeframe TEXT,
            DateTimeEnter TEXT,
            DateTimeExit TEXT,
            StopLossExt TEXT,
            WinLoss TEXT,
            EnterPrice REAL,
            ExitPrice REAL,
            FeeSum REAL,
            FinancialResultNet REAL,
            BotEquity REAL
        );
        """
        cursor.execute(req)
        con.commit()
        con.close()



class MockTradingDBOperations(SAG_DataBaseManagement):
    """
    класс управления возаимодействием с торговым счетом - таблице
    2. Формирование модуля ввода остатков по роботу;
    3. Формирование модуля ввода информации о сделке;
    4. Формирование модуля получения информации из базы данных о сделках - текущий баланс и последние 5 сделок.
    """
    __mock_account_db_table = "TradingTable"

    def __init__(self, robot_name: str, strategy_name: str, ticker: str, time_frame: str):
        super().__init__()
        self.robot_name = robot_name
        self.strategy_name = strategy_name
        self.ticker = ticker
        self.time_frame = time_frame

    def get_previous_data_of_table_id(self):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        request_ = f"""
        SELECT
            BotOperationID
        FROM
            {self.__mock_account_db_table}
        ORDER BY 
            BotOperationID DESC
        LIMIT 1;    
        """
        cursor.execute(request_)
        last_number = None
        try:
            last_number = cursor.fetchall()[0][0]
        except:
            #print(last_number)
            con.commit()
            con.close()
            if last_number is None:
                last_number = 0
            return last_number
        con.commit()
        con.close()
        return last_number

    def calc_robot_equity(self):
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        request_ = f"""
                SELECT
                    BotEquity
                FROM
                    {self.__mock_account_db_table}
                WHERE
                    RobotName='{self.robot_name}'
                ORDER BY 
                    BotOperationID DESC
                LIMIT 1;    
                """
        cursor.execute(request_)
        try:
            data = cursor.fetchall()[0][0]
        except:
            return 0
        if data is None:
            data = 0
        con.commit()
        con.close()
        return data


    def get_5_trades(self):
        # позволяет получить df из базы данных - его можно обработать
        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        request_ = f"""SELECT * 
        FROM {self.__mock_account_db_table}
        WHERE
            RobotName='{self.robot_name}'
        ORDER BY 
            BotOperationID DESC
        LIMIT 5;
        """
        cursor.execute(request_)
        list_of_tuples = cursor.fetchall()

        cursor.execute("PRAGMA table_info({});".format(self.__mock_account_db_table))
        list_of_columns = []
        columns_data = cursor.fetchall()  # тут нужно доставать из листа кортежей второй элемент кортежа
        for _, column in enumerate(columns_data):
            list_of_columns.append(column[1])
        df = pd.DataFrame(list_of_tuples, columns=list_of_columns)
        pd.set_option('display.expand_frame_repr', False)  # отображать весь набор данных
        con.commit()
        con.close()

        return df


    def restart_bot_account(self):
        # BotOperationID request:
        BotOperationID = self.get_previous_data_of_table_id() + 1
        OperationType = "tech"
        tr_type = "NA"
        enter_price = 0
        exit_price = 0
        fee= 0
        fin_res = 0
        is_sl = "NA"
        time_enter = datetime.now()
        time_enter = time_enter.strftime("%d.%m.%Y %H:%M:%S")
        time_exit = time_enter
        equity = 0
        win_loss = "NA"

        # make up tuple:
        tuple_ = (BotOperationID, OperationType, tr_type, self.robot_name, self.strategy_name, self.ticker,
                  self.time_frame, time_enter, time_exit, is_sl, win_loss, enter_price, exit_price,
                  fee, fin_res, equity)

        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO {self.__mock_account_db_table} VALUES {tuple_};")
        con.commit()
        con.close()


    def insert_trade_info_into_account(self, tr_type: str, time_enter: str,
                                       time_exit: str, is_sl: str, enter_price: float,
                                       exit_price: float, fee: float):
        """
        The procedure adds data about trade into  the database of mock trading.

        Columns: [BotOperationID, OperationType, TradingType,
        RobotName, StrategyName, Tiker, Timeframe, DateTimeEnter,
        DateTimeExit, StopLossExt, WinLoss, EnterPrice, ExitPrice,
        FeeSum, FinancialResultNet, BotEquity]
        """

        # BotOperationID request:
        BotOperationID = self.get_previous_data_of_table_id() + 1
        OperationType = "trade"
        if tr_type == "long":
            fin_res = exit_price - enter_price
        else:
            fin_res = enter_price - exit_price

        equity = self.calc_robot_equity() + fin_res

        if fin_res <= 0:
            win_loss = 'loss'
        else:
            win_loss = 'win'

        # equity calc request:
        # будет меняться на запрос.

        # make up tuple:
        tuple_ = (BotOperationID, OperationType, tr_type, self.robot_name, self.strategy_name, self.ticker,
                  self.time_frame, time_enter, time_exit, is_sl, win_loss, enter_price, exit_price,
                  fee, fin_res, equity)

        con = sqlite3.connect(self.db_name)
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO {self.__mock_account_db_table} VALUES {tuple_};")
        con.commit()
        con.close()


    def get_trades_info_from_account(self):
        df = self.read_data('TradePreferences')
        print(df.Tiker[0])


def test1(robot_name):
    print(robot_name + "_" + str(1))


if __name__ == '__main__':
    x = MockTradingDBOperations('Alpha','BWilliams Alligator','GAZR','5 min')
    #x.insert_trade_info_into_account('long','01.01.2022 09:00','03.01.2022 18:00','no',10000,10099,10.5)
    #for i in range(5):
    #    x.restart_bot_account()
    #x.deleting('TradingTable')
    x.print_data()


    input("Для продолжения нажмите Enter...")
