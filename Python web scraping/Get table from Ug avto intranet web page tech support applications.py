from selenium.webdriver.common.by import By
from selenium import webdriver  # требуется установка модуля
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC # для определения завершения загрузки страницы
from selenium.webdriver.support.ui import WebDriverWait # для определения завершения загрузки страницы
import time
import re
from bs4 import BeautifulSoup  # требуется установка модуля
import pandas as pd
import tkinter  # интерфейсы python для обозревателя для выбора папки сохранения файла. Требуется установка модуля
from tkinter import filedialog
import getpass

pwd = getpass.getpass('Введите пароль пользователя для доступа на сайт: ')
page_count = input('Введите кол-во страниц таблицы закрытых заявок, которые нужно достать (1 страница = 20 заявкам): ')

def get_proper_html(request_password, page_count):
    # чтобы браузер не открывался при запуске
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    driver.get("https://portal.yug-avto.ru/adm/techsupport_admin/?login=yes")

    username = driver.find_element(By.NAME, "USER_LOGIN")
    password = driver.find_element(By.NAME, "USER_PASSWORD")

    username.send_keys("shacev_a")

    password.send_keys(request_password)

    driver.find_element(By.NAME, "Login").click()

    # ждем загрузки страницы:
    time.sleep(10)

    # нас интересуют закрытые заявки:
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[1]/div[1]/button[3]/div[1]").click()

    # ждем прогрузки страницы:
    time.sleep(10)

    # ждем загрузки данных на странице (появления кнопки "Еще"):
    delay = 300 # seconds
    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH,
                            "/html/body/div[2]/div/div/div[3]/div[1]/table[2]/tfoot/tr/td/div/button[1]")))


    print("Страница загрузилась.")
    counter = 0

    # нажатие на кнопку "Еще" n раз для вытаскивания данных:
    pages_for_open = int(page_count)
    for i in range(pages_for_open):
        driver.find_element(By.XPATH,
                            "/html/body/div[2]/div/div/div[3]/div[1]/table[2]/tfoot/tr/td/div/button[1]").click()
        # ждем полной загрузки:
        time.sleep(3)
        counter += 1
        print(f"Страниц c заявками просмотрено: {counter} из {pages_for_open}")

    time.sleep(15)
    html = driver.page_source

    return html


def parse_data(html_code):
    parsed_html = BeautifulSoup(html_code, 'html.parser')

    # парсинг построчно данных:
    number = []
    date = []
    theme = []
    content = []
    sender = []
    resposible = []

    # таблица закрытых заявок (у нее не будет скрытия в стиле оформления таблицы)
    closed_table = parsed_html.find('table', {'class':'_request-list'}, style="")

    for tr in closed_table.findAll('tr', {'class': '_request-list-item'}):
        # номера заявки:
        number.append(tr.find('div', {'class': '_request-list-item-number'}).text)

        # парсинг даты и времени:
        date.append(tr.find('div', {'class': '_request-list-item-date'}).text)

        # парсинг темы заявки:
        theme.append(tr.find('div', {'class': '_request-list-item-name'}).text)

        # парсинг тела заявки:
        content.append(tr.find('div', {'class': '_request-list-item-description'}).text)

        # парсинг заявителя:
        sender.append(tr.find("a", class_="_request-list-item-sender", href=True).text)

        # парсинг заявителя:
        if tr.find("a", class_="_request-list-item-asssigned-by", href=True) is None:
            resposible.append("нет данных")
        else:
            resposible.append(tr.find("a", class_="_request-list-item-asssigned-by", href=True).text)

    # создание таблицы pandas:
    dictionary = {'Номер заявки': number, 'Дата': date, 'Наименование заявки': theme, 'Текст заявки': content,
                  'Инициатор заявки': sender, 'Ответственный сотрудник поддержки': resposible}

    ## проверка что кол-во строк во всех столбцах словаря - совпадают
    # for i in dictionary:
    #    print(i," -> ", len(dictionary[i]))

    df = pd.DataFrame(dictionary)
    #print(df)

    def replace_extra_spaces_before(x):
        return re.sub(' +', ' ', x)

    # обработка текстовых полей:
    # ответственный сотрудник
    df['Ответственный сотрудник поддержки'] = \
        df['Ответственный сотрудник поддержки'].apply(replace_extra_spaces_before)  # удаление лишних пробелов через
    # регулярные выражения
    df['Ответственный сотрудник поддержки'] = \
        df['Ответственный сотрудник поддержки'].replace('\n', '', regex=True)  # удаление перевода каретки
    df['Ответственный сотрудник поддержки'] = \
        df['Ответственный сотрудник поддержки'].apply(
            lambda x: x.strip())  # удаление пробелов в начале и в конце строки

    # инициатор заявки
    df['Инициатор заявки'] = df['Инициатор заявки'].apply(replace_extra_spaces_before)  # удаление лишних пробелов через
    # регулярные выражения
    df['Инициатор заявки'] = df['Инициатор заявки'].replace('\n', '', regex=True)  # удаление перевода каретки
    df['Инициатор заявки'] = df['Инициатор заявки'].apply(
        lambda x: x.strip())  # удаление пробелов в начале и в конце строки

    # наименование заявки
    df['Наименование заявки'] = df['Наименование заявки'].apply(
        replace_extra_spaces_before)  # удаление лишних пробелов через
    # регулярные выражения
    df['Наименование заявки'] = df['Наименование заявки'].replace('\n', '', regex=True)  # удаление перевода каретки
    df['Наименование заявки'] = df['Наименование заявки'].apply(
        lambda x: x.strip())  # удаление пробелов в начале и в конце строки

    # Текст заявки
    df['Текст заявки'] = df['Текст заявки'].apply(replace_extra_spaces_before)  # удаление лишних пробелов через
    # регулярные выражения
    df['Текст заявки'] = df['Текст заявки'].replace('\n', ' ', regex=True)  # удаление перевода каретки
    df['Текст заявки'] = df['Текст заявки'].replace('	', ' ', regex=True)  # замена табуляции на пробел
    df['Текст заявки'] = df['Текст заявки'].apply(lambda x: x.strip())  # удаление пробелов в начале и в конце строки

    tkinter.Tk().withdraw()  # prevents an empty tkinter window from appearing
    folder_path = filedialog.askdirectory()
    file_name = 'выгрузка запросов из техподдержки.xlsx'

    df.to_excel(folder_path + "/" + file_name)


if __name__ == '__main__':
    parse_data(get_proper_html(pwd, page_count))