import os
import sense_energy
import signal
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
log 		   = logging.getLogger('senseshow.main')
keep_running   = True

def main():
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)
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

	while keep_running:	
		try:
			update_sense_data()
		except KeyboardInterrupt:
			exit_gracefully()
		except Exception as ex:
			tqdm.write("Exception encountered.")
			print(ex)
			continue


	for index, thread in enumerate(threads):
		logging.info("Main    : before joining thread %d.", index)
		thread.join()
		logging.info("Main    : thread %d done", index)

def exit_gracefully(signum, frame):
	global solar_queue, use_queue, keep_running
	try:
		keep_running = False
		use_queue.put(None)
		solar_queue.put(None)
		leds.clear()
	except Exception as ex:
		print("errors exiting")
		print(ex)
		exit()


def update_sense_data():
	global use_queue, solar_queue, keep_running
	user = os.getenv("SENSE_USER")
	passwd = os.getenv("SENSE_PASSWD")	
	sense = sense_energy.Senseable()
	sense.authenticate(user,passwd)
	sense.rate_limit=10
	sense.update_realtime()
	iterations=0
	while keep_running:
		try:
			data = sense.get_realtime()
			log.debug("Latest Data From: {}".format(time.ctime(data['epoch'])))
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
	global solar_queue, keep_running
	t = tqdm(total=max_solar, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	while keep_running:
		while solar_queue.qsize() > 1:
			trash = solar_queue.get()
			solar_queue.task_done()
			log.info("solar discard e:{}, solar:{}, use:{}".format(trash['epoch'], trash['d_solar_w'],trash['grid_w']))
		data = solar_queue.get()
		if data == None:
			break
		t.total = data['d_w']
		t.reset()
		t.update(data['d_solar_w'])
		t.refresh()
		if data['d_solar_w'] < 0:
			leds.show_sun(False)
			leds.flow(19,29, -data['d_solar_w'], max_solar_draw, leds.color_red)
		elif data['d_solar_w'] > 0:
			leds.show_sun(True)
			leds.flow(29,19, data['d_solar_w'], max_solar, leds.color_orange)
	
		solar_queue.task_done()

def print_use():
	global use_queue, keep_running
	t = tqdm(total=max_use, unit="watts",miniters=1, position=2, unit_scale=True, leave=True)
	while keep_running:
		while use_queue.qsize() > 1:
			use_queue.get()
			use_queue.task_done()
			tqdm.write("use discard")
		data = use_queue.get()
		if data == None:
			break
		t.reset()
		t.update(data['d_w'])
		t.refresh()
		leds.flow(4,14,data['d_w'],max_use, leds.color_red)
		use_queue.task_done()



if __name__ == '__main__':
	print('Sense Show Starting...')
	main()