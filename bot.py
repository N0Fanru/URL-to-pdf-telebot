import pdfkit
import telebot
from requests import get
from bs4 import BeautifulSoup
import string
import os
import zipfile
import re
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"))
url_pattern = r'https?://[^\s\)\]\}<>"]+'
MAX_URLS = 10
options = {
    'zoom': '1.8',
}

def convert_url_to_pdf(url, id, n, m):
    try:
        response = get(url)
        title = BeautifulSoup(response.content, 'html.parser').title.string
        if title is None:
            title = "Сайт в pdf"
        title = str(n) + ". " + title.translate(str.maketrans('', '', string.punctuation)) + ".pdf"
        pdfkit.from_url(url, title, options=options)
        return title
    except Exception as e:
        bot.edit_message_text(f'Процесс над файлом номер {n}\nПроизошла ошибка: {e}', id, m)
        print(f'Error: {e}')
        return False

        

@bot.message_handler(content_types=['text'])
def echo_message(message):
    urls = re.findall(url_pattern, message.text)
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_link":
                urls.append(entity.url)

    n = 0
    com = 0
    if len(urls) > 0 and len(urls) <= MAX_URLS:
        name = f'archive-{message.from_user.id}.zip'
        zipf = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
        for url in urls:
            n += 1
            m = bot.send_message(message.from_user.id, f"Процесс над файлом номер {n}").message_id
            file = convert_url_to_pdf(url, message.from_user.id, n, m)
            if file:
                zipf.write(file)
                os.remove(file)
                com += 1
        zipf.close()
        bot.send_document(message.from_user.id, open(name, 'rb'))
        os.remove(name)
        bot.send_message(message.from_user.id, f"Успешно сконвертировано {com} из {n} ссылок")
    elif len(urls) > MAX_URLS:
        bot.send_message(message.from_user.id, f"Максимальное количество ссылкон на обработку: {MAX_URLS}")
    else:
        bot.send_message(message.from_user.id, "Ни одного url не найдено")


bot.infinity_polling(none_stop=True)