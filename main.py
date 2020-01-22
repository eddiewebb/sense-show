import os
import sense_energy
import time
import logging
import threading
from tqdm import tqdm, trange

from queue import Queue
import leds


def main():
	global solar_queue, use_queue

	solar_queue = Queue()
	use_queue = Queue()
	functions = list()
	functions.append(print_solar)
	functions.append(print_use)
	threads = list()

	draw_house()
	draw_panels()
	draw_grid()

	for function in functions:
		logging.info("Main    : create and start thread %s.", function)
		x = threading.Thread(target=function, args=())
		threads.append(x)
		x.start()

	while 1:	
		try:
			update_sense_data()
		except KeyboardInterrupt:
			solar_queue.put(None)
			use_queue.put(None)
			exit()
		except Exception as ex:
			tqdm.write("Exception encountered.")
			print(ex)
			continue


	for index, thread in enumerate(threads):
		logging.info("Main    : before joining thread %d.", index)
		thread.join()
		logging.info("Main    : thread %d done", index)

def show_sun(yes):	
	if yes:
		color = leds.color_orange
	else:
		color = leds.off
	leds.mark(32,1, color)
	leds.mark(32,2, color)

def draw_house():
	for x in range(15,19):
		for y in reversed(range(5,9)):
			if x in (16,17) or y == 6:
				leds.mark(x,y,leds.color_teal)

def draw_panels():
	for x in range(30,33):
		for y in reversed(range(1,9)):
			if x == 30 and y < 5:
				leds.mark(x,y,leds.color_teal)
			if x == 31 and y in (3,4,5,6):
				leds.mark(x,y,leds.color_teal)
			if x == 32 and y in (5,6,7,8):
				leds.mark(x,y,leds.color_teal)

def draw_grid():
	for x in range(1,4):
		for y in reversed(range(4,9)):
			if x ==2 or y in (4,6):
				leds.mark(x,y,leds.color_purple)

def update_sense_data():
	global use_queue, solar_queue
	user = os.getenv("SENSE_USER")
	passwd = os.getenv("SENSE_PASSWD")	
	sense = sense_energy.Senseable()
	sense.authenticate(user,passwd)
	fails=0
	for data in sense.get_realtime_stream():
		try:
			stats = dict()
			stats['from_grid']=data['grid_w']
			stats['from_solar']=data['d_solar_w']
			stats['use']=data['d_w']
			solar_queue.put(stats)
			use_queue.put(stats)
			time.sleep(1)
		except Exception as ex:
			print(ex)

def print_solar():
	global solar_queue
	t = tqdm(total=15000, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	while 1:
		data = solar_queue.get()
		t.total = data['use']
		t.reset()
		t.update(data['from_solar'])
		t.refresh()
		if data['from_solar'] < 0:
			show_sun(False)
			leds.flow(19,29,-data['from_solar'],320,leds.color_red)
		elif data['from_solar'] > 0:
			show_sun(True)
			leds.flow(29,19,data['from_solar'],10000,leds.color_orange)

def print_use():
	global use_queue
	t = tqdm(total=15000, unit="watts",miniters=1, position=2, unit_scale=True, leave=True)
	while 1:
		data = use_queue.get()
		t.reset()
		t.update(data['use'])
		t.refresh()
		leds.flow(4,14,data['use'],8000, leds.color_red)



if __name__ == '__main__':	

	main()