import os
import signal
import time
import threading
import logging
from queue import LifoQueue
from queue import Full
import sense_energy
#from tqdm import tqdm
from dotenv import load_dotenv
import led_strip
import oled


max_solar 	   = 10000
max_use   	   = 10000
flip_iterations= 5
data_queue    = None
led_panel        = None
screen			 = None
threads = list()
abort_threads = False

logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')

def main():
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)

	load_dotenv()

	launchAndWait()

	log.info("all done")

def launchAndWait():
	global led_panel, abort_threads, threads, screen, data_queue

	log.info("Launching threads")
	
	data_queue    = LifoQueue(maxsize=5)
	screen = oled.OLED()
	led_panel = led_strip.LedStrip()

	
	for function in [update_sense_data, update_led_panel]:
		logging.info("Main    : create and start thread %s.", function)
		x = threading.Thread(target=function, args=())
		threads.append(x)
		x.start()


	# this is where logic for healthy run is waiting.
	for index, thread in enumerate(threads):
		thread.join()
		logging.info("Main    : thread %d done", index)

	log.info("All threads rejoined, return to main")



def halt_threads():
	global abort_threads
	log.info("Halting threads")
	abort_threads = True



	
"""
Called by singla traps only, you should just call halt_threads()
"""
def exit_gracefully(signum, frame):
	log.info("Shutting down")
	halt_threads()
	time.sleep(1)



def update_sense_data():
	try:
		user = os.getenv("SENSE_USER")
		passwd = os.getenv("SENSE_PASSWD")	
		sense = sense_energy.Senseable()
		sense.rate_limit=10
		sense.authenticate(user,passwd)
		while True:
			global abort_threads, data_queue
			if abort_threads:
				log.info("Abort threads true, exiting Sense loop")
				break
			try:
				sense.update_realtime()
				data = sense.get_realtime()
				data_queue.put_nowait(data)
				if data_queue.qsize() > 1:
					log.debug("Queue size is %d", data_queue.qsize())
			except Full:
				log.debug("update_sense_data: Queue full, skipping write.")
				time.sleep(2)
				pass
			except:
				log.exception("update_sense_data: Error in Sense library call")
				pass
	except:
		log.exception("Exception in sense thread")
		halt_threads()

def update_led_panel():
	try:
		global data_queue, led_panel
		#solar = tqdm(total=max_solar, unit="watts",desc="From Solar", miniters=1, position=0, unit_scale=True, leave=True)
		#use = tqdm(total=max_use, unit="watts",desc="Consumption",miniters=1, position=1, unit_scale=True, leave=True)
		#grid = tqdm(total=max_use, unit="watts",desc="From Grid",miniters=1, position=2, unit_scale=True, leave=True)
		while True:
			global abort_threads
			if abort_threads:
				log.info("Abort threads true, exiting Display loop")
				break
			try:
				# non-blocking, if empty it jumps to exception
				data = data_queue.get_nowait()
				# log.debug("Display Data From: {}".format(time.ctime(data['epoch'])))
				# Set console indicators	
				# set_tqdm(solar,data['d_solar_w'])
				# set_tqdm(use,data['d_w'])
				# set_tqdm(grid,data['grid_w'])

				data['max_solar'] = max_solar
				data['max_use'] = max_use
				screen.present(data)
				# flash solar prohress
				if data['d_solar_w'] < 0:
					led_panel.show_sun(False)
					# no sun, energy flows grid to house to panels
					led_panel.flow_grid(data['grid_w'], max_use)
					led_panel.flow_solar(data['d_solar_w'], max_solar)
				elif data['d_solar_w'] >= 0:
					led_panel.show_sun(True)
					# making energy, flow starts at paenl (even if grid also feeds in)
					led_panel.flow_solar(data['d_solar_w'], max_solar)
					led_panel.flow_grid(data['grid_w'], max_use)
				data_queue.task_done()
			except:
				log.debug("Empty queue for display, loop continue")
				time.sleep(.5)
	except:
		log.exception("uncaught exception in display thread")
		halt_threads()

def set_tqdm(instance, new_value):
		instance.reset()
		instance.update(new_value)
		instance.refresh()





if __name__ == '__main__':
	print('Sense Show Starting...')
	main()