import os
import signal
import time
import threading
import logging
from queue import Queue
from collections import deque
import sense_energy
from tqdm import tqdm
from dotenv import load_dotenv
import led_strip


max_solar 	   = 8000
max_use   	   = 15000
flip_iterations= 5
data_queue    = Queue()
led_panel        = None
threads = list()
keep_running = True

logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')

def main():
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)

	load_dotenv()

	try:
		launchAndWait()
	except: 
		log.exception("Exception encountered")
		exit_gracefully()
	log.info("all done")

def launchAndWait():
	global led_panel, abort_threads, threads

	log.info("Launching threads")
	
	#wait for all previous threads to die
	halt_threads() 
	abort_threads = False #let new ones run
	# discard any poison pills our led will try to eat
	while data_queue.qsize() > 0:
		data_queue.get()
		data_queue.task_done()
	
	# start brand new!
	led_panel = led_strip.LedStrip()

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
	# sense and non-blocking threas should respect this.
	abort_threads = True
	# q based threads need a poison pill since they block on empty queues.
	data_queue.put(None)


	

def exit_gracefully(signum, frame):
	global keep_running, led_panel
	log.info("Shutting down")
	keep_running = False
	halt_threads()
	time.sleep(1)	
	led_panel.clear()



def update_sense_data():
	try:
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
			time.sleep(3)
	except:
		log.exception("Exception in sense thread")
		halt_threads()

def update_led_panel():
	try:
		log.debug("led function")
		global data_queue, led_panel
		solar = tqdm(total=max_solar, unit="watts",desc="From Solar", miniters=1, position=0, unit_scale=True, leave=True)
		use = tqdm(total=max_use, unit="watts",desc="Consumption",miniters=1, position=1, unit_scale=True, leave=True)
		grid = tqdm(total=max_use, unit="watts",desc="From Grid",miniters=1, position=2, unit_scale=True, leave=True)
		while True:
			while data_queue.qsize() > 5:
				data_queue.get()
				data_queue.task_done()
				log.info("solar discard")
			data = data_queue.get()
			# Since queue.get is blocking, we can't use the commong boolean on the loop, instead a None item will kill us.
			if data == None:
				#we're being asked to shutdwn
				log.info("poison pill in queue, exiting LED thread")
				break
			else:
				log.debug("new dtata to show")
			# Set console indicators	
			set_tqdm(solar,data['d_solar_w'])
			set_tqdm(use,data['d_w'])
			set_tqdm(grid,data['grid_w'])

			# flash solar prohress
			if data['d_solar_w'] < 0:
				led_panel.show_sun(False)
			elif data['d_solar_w'] > 0:
				led_panel.show_sun(True)
		
			led_panel.flow_solar(data['d_solar_w'], max_solar)
			led_panel.flow_grid(data['grid_w'], max_use)
		
			data_queue.task_done()
	except:
		log.exception("led thread exception")
		halt_threads()

def set_tqdm(instance, new_value):
		instance.reset()
		instance.update(new_value)
		instance.refresh()





if __name__ == '__main__':
	print('Sense Show Starting...')
	main()