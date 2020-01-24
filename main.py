import os
import sense_energy
import signal
import time
import logging
import threading
from tqdm import tqdm, trange

from queue import Queue
from collections import deque
import led_strip


max_solar 	   = 8000
max_use   	   = 15000
flip_iterations= 5
keep_running   = True
data_queue    = Queue()
display = led_strip.LedStrip()

logging.basicConfig(filename='/var/log/sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')

def main():
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)

	
	display.draw_house()
	display.draw_panels()
	display.draw_grid()

	threads = list()
	for function in [update_display]:
		logging.info("Main    : create and start thread %s.", function)
		x = threading.Thread(target=function, args=())
		threads.append(x)
		x.start()

	while keep_running:	
		try:
			update_sense_data()
			sleep(5) #error here could be from initializing leds or authing with sense, back off high level ,restart it all again
		except KeyboardInterrupt:
			exit_gracefully()
		except:
			log.exception("Exception in main thread.")
			continue


	for index, thread in enumerate(threads):
		logging.info("Main    : before joining thread %d.", index)
		thread.join()
		logging.info("Main    : thread %d done", index)

def exit_gracefully(signum, frame):
	global data_queue, keep_running, display
	try:
		keep_running = False
		data_queue.put(None)
		display.clear()
	except Exception as ex:
		print("errors exiting")
		print(ex)
		exit()


def update_sense_data():
	global data_queue, keep_running, display
	user = os.getenv("SENSE_USER")
	passwd = os.getenv("SENSE_PASSWD")	
	sense = sense_energy.Senseable()
	sense.authenticate(user,passwd)
	sense.rate_limit=10
	display.reset()
	while keep_running:
		sense.update_realtime()
		data = sense.get_realtime()
		log.debug("Latest Data From: {}".format(time.ctime(data['epoch'])))
		#qDepth = solar_queue.qsize() + data_queue.qsize()
		#if qDepth > 0:
		#	tqdm.write("Queuedepth: " + str(qDepth))
		data_queue.put(data)
		time.sleep(1)

def update_display():
	global data_queue, keep_running, display
	solar = tqdm(total=max_solar, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	use = tqdm(total=max_use, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	grid = tqdm(total=max_use, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	while keep_running:
		while data_queue.qsize() > 5:
			data_queue.get()
			data_queue.task_done()
			tqdm.write("solar discard")
		data = data_queue.get()
		# Primary thread will send None when to kill
		if data == None:
			break

		# Set console indicators	
		set_tqdm(solar,data['d_solar_w'])
		set_tqdm(use,data['d_w'])
		set_tqdm(grid,data['grid_w'])

		# flash solar prohress
		if data['d_solar_w'] < 0:
			display.show_sun(False)
			display.flow(19,29, -data['d_solar_w'], max_solar, display.color_red)
		elif data['d_solar_w'] > 0:
			display.show_sun(True)
			display.flow(29,19, data['d_solar_w'], max_solar, display.color_orange)

		#flash grid
		if data['grid_w'] < 0:
			display.flow(14,4, -data['grid_w'], max_use, display.color_orange)
		elif data['grid_w'] > 0:
			display.flow(4,14, data['grid_w'], max_use, display.color_red)
	
		data_queue.task_done()

def set_tqdm(instance, new_value):
		instance.reset()
		instance.update(new_value)
		instance.refresh()





if __name__ == '__main__':
	print('Sense Show Starting...')
	main()