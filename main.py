import os
import sense_energy
import time
import logging
import threading
from tqdm import tqdm, trange

from queue import Queue
from collections import deque
import leds


max_solar 	   = 2000
max_solar_draw = 300
max_use   	   = 15000
flip_iterations= 5


def main():
	global solar_queue, use_queue

	solar_queue = Queue()
	use_queue = Queue()
	functions = list()
	functions.append(print_solar)
	functions.append(print_use)
	threads = list()

	leds.draw_house()
	leds.draw_panels()
	leds.draw_grid()

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


def update_sense_data():
	global use_queue, solar_queue
	user = os.getenv("SENSE_USER")
	passwd = os.getenv("SENSE_PASSWD")	
	sense = sense_energy.Senseable()
	sense.authenticate(user,passwd)
	sense.rate_limit=10
	sense.update_realtime()
	iterations=0
	while True:
		try:
			data = sense.get_realtime()
			tqdm.write("Latest: {}".format(time.ctime(data['epoch'])))
			#qDepth = solar_queue.qsize() + use_queue.qsize()
			#if qDepth > 0:
			#	tqdm.write("Queuedepth: " + str(qDepth))
			solar_queue.put(data)
			use_queue.put(data)
		except Exception as ex:
			print(ex)
		sense.update_realtime()
		time.sleep(1)

def print_solar():
	viz_flipper=0
	global solar_queue
	t = tqdm(total=max_solar, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	while 1:
		while solar_queue.qsize() > 1:
			trash = solar_queue.get()
			solar_queue.task_done()
			tqdm.write("solar discard e:{}, solar:{}, use:{}".format(trash['epoch'], trash['d_solar_w'],trash['grid_w']))
		data = solar_queue.get()
		t.total = data['d_w']
		t.reset()
		t.update(data['d_solar_w'])
		t.refresh()
		viz_flipper += 1
		if True: #viz_flipper <= flip_iterations:
			if data['d_solar_w'] < 0:
				leds.show_sun(False)
				leds.flow(19,29,-data['d_solar_w'],max_solar_draw,leds.color_red)
			elif data['d_solar_w'] > 0:
				leds.show_sun(True)
				leds.flow(29,19,data['d_solar_w'],max_solar,leds.color_orange)
		else:
			tqdm.write(str(data['d_solar_w']))
			#leds.display(data['from_solar'], 19)
		if viz_flipper > 9:
			viz_flipper = 0
		solar_queue.task_done()

def print_use():
	global use_queue
	t = tqdm(total=max_use, unit="watts",miniters=1, position=2, unit_scale=True, leave=True)
	while 1:
		while use_queue.qsize() > 1:
			use_queue.get()
			use_queue.task_done()
			tqdm.write("use discard")
		data = use_queue.get()
		t.reset()
		t.update(data['d_w'])
		t.refresh()
		leds.flow(4,14,data['d_w'],max_use, leds.color_red)
		use_queue.task_done()



if __name__ == '__main__':	

	main()