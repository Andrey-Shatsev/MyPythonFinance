import smtplib

def send_notification(email, subject, txt):
    sender = 'TradingRobots.mail@yandex.ru'
    sender_password = 'Какой-то пароль)'
    mail_lib = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    mail_lib.login(sender, sender_password)
    for to_item in email:
        msg = 'From: %s\r\nTo: %s\r\nContent-Type: text/plain; charset="utf-8"\r\nSubject: %s\r\n\r\n' % (
        sender, to_item, subject)
        msg += txt
        mail_lib.sendmail(sender, to_item, msg.encode('utf8'))
    mail_lib.quit()

if __name__ == '__main__':
    send_notification(['a.g.shatsev@gmail.com'], "Гелиос.01.Long - тестовое сообщение", 'Hello!')