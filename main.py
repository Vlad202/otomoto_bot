import requests
from bs4 import BeautifulSoup
import time
from telebot import TeleBot
import threading
import datetime
from secrets import TELEGRAM_TOKEN
import os
import datetime
import shutil
from lxml import html
import re

app = TeleBot(TELEGRAM_TOKEN)

@app.message_handler(commands=['start'])
def example_command(message):
	geted_id = message.chat.id
	with open('telegram.txt', 'r', encoding='utf-8') as f:
		ids_list = f.read().split(',')
		ids = ids_list
	if str(geted_id) not in ids:
		ids.append(str(geted_id))
		# print(message)
		with open('telegram.txt', 'a') as f:
			f.write(f'{str(geted_id)},')
	msg = '''
	Здравствуйте!\nТеперь вам будут присылаться новые объявления из сайта otomoto.pl\n
	Чтоб отказатья от подписки, введите /stop
	'''
	app.send_message(geted_id, msg)

@app.message_handler(commands=['stop'])
def example_command(message):
	geted_id = message.chat.id
	with open('telegram.txt', 'r', encoding='utf-8') as f:
		ids_list = f.read().split(',')
	msg = '''
		ID пользователя не найдено, кажется что Вы ещё не подписаны на рассылку.Подписаться - /start
	'''
	if str(geted_id) in ids_list:
		ids_list.remove(str(geted_id))
		updated_ids_list = ','.join(str(x) for x in ids_list)
		with open('telegram.txt', 'w') as f:
			f.write(updated_ids_list)
		msg = '''
			Вам больше не будут рприходить сообщения от меня.\nЧто бы получать уведомления снова, введите команду /start
		'''
	app.send_message(geted_id, msg)

def send_zip(zip_name):
	with open('telegram.txt', 'r') as f:
		ids_list = f.read().split(',')
		for chat_id in ids_list:
			try:
				app.send_document(chat_id, open(zip_name+'.zip','rb'))
			except:
				pass

def fivth_parser(post_url):
	response_post = requests.get(post_url)
	post_soup = BeautifulSoup(response_post.text, 'html')
	table_items = post_soup.find_all('li', {'class': 'offer-params__item'})
	car_name = post_soup.find('span', {'class': 'offer-title'}).text.strip()
	text = f"{post_url}\n\n{car_name}\n{post_soup.find('span', {'class': 'offer-price__number'}).text.strip()}\n\n\n"
	car_name = 'otomoto - '+car_name
	os.mkdir(car_name)
	for li in table_items:
		text += f"{li.find('span').text.strip()} - {li.find('div').text.strip()}\n\n"
	with open(f'./{car_name}/'+car_name+'.txt', 'w') as f:
		f.write(text)
	slick_slides = post_soup.find_all('li', {'class': 'offer-photos-thumbs__item'})
	for slide in range(len(slick_slides)):
		url = slick_slides[slide].find('img').attrs['src'].split(';s=')[0]
		image = requests.get(url).content
		with open(f'./{car_name}/'+str(slide)+'.jpg', 'wb') as f:
			f.write(image)
	shutil.make_archive(car_name, 'zip', car_name)
	shutil.rmtree(f'{car_name}/')
	send_zip(car_name)
	os.remove(car_name+'.zip')

def bot_thread():
	print('### START TELEGRAM ###')
	app.polling()

def parser_thread():
	print('### START PARSER ###')
	old_fivth = ''
	while True:
		try:
			response_fivth = requests.get('https://www.otomoto.pl/osobowe/?search%5Bfilter_enum_damaged%5D=1&search%5Border%5D=created_at%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D=')
		except Exception as e:
			print(e)
			print('Exception in fivth parser')
			continue
		fivth_soup = BeautifulSoup(response_fivth.text, 'html')
		first_car_fivth = fivth_soup.find_all('a', {'class': 'offer-title__link'})[0]
		first_car_fivth_text = first_car_fivth.text.strip()
		if first_car_fivth_text != old_fivth:
			try:
				print('checkout ------- otomoto ------- ' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
				fivth_parser(first_car_fivth.attrs['href'])
			except Exception as e:
				print(e)
			old_fivth = first_car_fivth_text
		time.sleep(300)

if __name__ == '__main__':
	thr_bot = threading.Thread(target=bot_thread)
	thr_bot.start()
	thr_parser = threading.Thread(target=parser_thread)
	thr_parser.start()
