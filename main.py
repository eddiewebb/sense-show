import os
import signal
import time
import threading
import logging
from queue import Queue
from collections import deque
import sense_energy
from tqdm import tqdm

import led_strip


max_solar 	   = 8000
max_use   	   = 15000
flip_iterations= 5
data_queue    = Queue()
led_panel        = None
threads = list()
keep_running = True

logging.basicConfig(filename='/var/log/sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')

def main():
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)



	while keep_running:	
		try:
			launchAndWait()
		except KeyboardInterrupt:
			exit_gracefully()
			#break
		except:
			# any other exception cshould trigger full restart
			log.exception("Exception in main thread, asking others to close for restart.")
			time.sleep(5) #error here could be from initializing leds or authing with sense, back off high level ,restart it all again
			#continue
	log.info("all done")

def launchAndWait():
	global led_panel, abort_threads, threads

	log.info("Launching threads")

	halt_threads() #wait for all previous threads to die
	abort_threads = False #let new ones run
	
	led_panel = led_strip.LedStrip()
	led_panel.draw_house()
	led_panel.draw_panels()
	led_panel.draw_grid()

	for function in [update_sense_data, update_led_panel]:
		logging.info("Main    : create and start thread %s.", function)
		x = threading.Thread(target=function, args=())
		threads.append(x)
		x.start()


	# this is where logic for healthy run is waiting.
	for index, thread in enumerate(threads):
		logging.info("Main    : before joining thread %d.", index)
		thread.join()
		logging.info("Main    : thread %d done", index)




def halt_threads():
	global data_queue, abort_threads, threads
	log.info("Halting threads")
	abort_threads = True
	data_queue.put(None)


	

def exit_gracefully(signum, frame):
	global keep_running, led_panel
	log.info("Shutting down")
	keep_running = False
	halt_threads()
	time.sleep(1)	
	led_panel.clear()



def update_sense_data():
	global data_queue, led_panel
	user = os.getenv("SENSE_USER")
	passwd = os.getenv("SENSE_PASSWD")	
	sense = sense_energy.Senseable()
	sense.rate_limit=10
	sense.authenticate(user,passwd)
	while True:
		global abort_threads
		if abort_threads:
			log.info("Abort threads true, exiting Sense loop")
			break
		sense.update_realtime()
		data = sense.get_realtime()
		log.debug("Latest Data From: {}".format(time.ctime(data['epoch'])))
		#qDepth = solar_queue.qsize() + data_queue.qsize()
		#if qDepth > 0:
		#	tqdm.write("Queuedepth: " + str(qDepth))
		data_queue.put(data)
		time.sleep(1)

def update_led_panel():
	global data_queue, led_panel
	solar = tqdm(total=max_solar, unit="watts",desc="From Solar", miniters=1, position=0, unit_scale=True, leave=True)
	use = tqdm(total=max_use, unit="watts",desc="Consumption",miniters=1, position=1, unit_scale=True, leave=True)
	grid = tqdm(total=max_use, unit="watts",desc="From Grid",miniters=1, position=2, unit_scale=True, leave=True)
	while True:
		global abort_threads
		if abort_threads:
			log.info("Abort threads true, exiting LED loop")
			break
		while data_queue.qsize() > 5:
			data_queue.get()
			data_queue.task_done()
			tqdm.write("solar discard")
		data = data_queue.get( )
		# Primary thread will send None when to kill
		if data == None:
			return

		# Set console indicators	
		set_tqdm(solar,data['d_solar_w'])
		set_tqdm(use,data['d_w'])
		set_tqdm(grid,data['grid_w'])

		# flash solar prohress
		if data['d_solar_w'] < 0:
			led_panel.show_sun(False)
			led_panel.flow(19,29, -data['d_solar_w'], max_solar, led_panel.color_red)
		elif data['d_solar_w'] > 0:
			led_panel.show_sun(True)
			led_panel.flow(29,19, data['d_solar_w'], max_solar, led_panel.color_orange)

		#flash grid
		if data['grid_w'] < 0:
			led_panel.flow(14,4, -data['grid_w'], max_use, led_panel.color_orange)
		elif data['grid_w'] > 0:
			led_panel.flow(4,14, data['grid_w'], max_use, led_panel.color_red)
	
		data_queue.task_done()
	log.debug("led function finishing")

def set_tqdm(instance, new_value):
		instance.reset()
		instance.update(new_value)
		instance.refresh()





if __name__ == '__main__':
	print('Sense Show Starting...')
	main()