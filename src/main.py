import os
import signal
import time
import threading
import logging
from queue import Queue
from queue import Full
from queue import Empty
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

logging.basicConfig(filename='sense-debug.log')
log = logging.getLogger('senseshow.main')

def main():
	log.info("Sense show starting... as PID: %s", os.getpid())
	signal.signal(signal.SIGINT, exit_gracefully)
	signal.signal(signal.SIGTERM, exit_gracefully)
	signal.signal(signal.SIGUSR1, print_status)
	signal.signal(signal.SIGQUIT, print_status_tty)

	load_dotenv()
	LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
	log.setLevel(LOGLEVEL)
	log.info("Log level: %s",LOGLEVEL)

	launchAndWait()

	log.info("Program ended")


def launchAndWait():
	global led_panel, abort_threads, threads, screen, data_queue
	data_queue    = Queue(maxsize=5) # just big enough to act as a buffer between api and led speeds
	screen = oled.OLED()
	led_panel = led_strip.LedStrip()

	log.info("Launching threads")
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


def print_status_tty(signum, frame):
	print("Stats printed to log. To stop use ctrl+c")
	print_status(signum,frame)

'''
 Eats a data point and prints some sstats
'''
def print_status(signum, frame):
	log.warning("SIG USR1 receieved, pulling data for stats")
	global abort_threads, led_panel, data_queue
	try:
		# for stats it can be blocking since bg threads are still doing their thing
		data = data_queue.get()
		data_queue.task_done()
		now = time.time()
		log.info("depth: %d", data_queue.qsize())
		log.info("now: %d", now)
		log.info("data's: %d",data['epoch'])
		log.info("grid w: %s",data['grid_w'])
		log.info("solar w: %s",data['d_solar_w'])
		log.info("using: %s",data['d_w'])
		#log.info("%s",data)
	except:
		log.exception("Unknown exceoption")
		raise


def update_sense_data():
	try:
		user = os.getenv("SENSE_USER")
		passwd = os.getenv("SENSE_PASSWD")	
		sense = sense_energy.Senseable()
		sense.rate_limit=4 #seconds to wait between updating data from sense (they block more than 1/second from all sources for a user)
		sense.authenticate(user,passwd)
		while True:
			try:
				log.info("Establishing realtime API feed....")
				feed = sense.get_realtime_stream()
				while True:	
					global abort_threads, data_queue
					if abort_threads:
						log.info("Abort threads true, exiting Sense loop")
						return
					try:
						log.debug("reading live feed")
						data = next(feed)
						data_queue.put_nowait(data)
					except StopIteration:
						# i dont think we'll ever hit this
						log.info("exhausted realtime feed, renew API")
						break
					except Full:
						log.debug("update_sense_data: Queue full, dump oldest.")
						data_queue.get_nowait()
						data_queue.put_nowait(data)
						pass
			except:
				log.warning("Sense library error, likely too many api calls")
				time.sleep(2)
				pass
	except:
		log.exception("Exception in sense thread")
		halt_threads()


def update_led_panel():
	try:		 
		while True:
			global abort_threads, led_panel, data_queue
			if abort_threads:
				log.info("Abort threads true, exiting Display loop")
				break
			try:
				# non-blocking, if empty it jumps to exception
				data = data_queue.get_nowait()
				data_queue.task_done()
				log.debug("Display Data From: {}".format(time.ctime(data['epoch'])))
				
				now = time.time()
				if now - data['epoch'] > 20: #clocks will diverge a few seconds, so dont se too low
					log.warn("Time lagging > 20 seconds, discarding")
					log.info("now: %d", now)
					log.info("data: %d",data['epoch'])
					continue
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
			except Empty:
				log.debug("Empty queue for display, loop continue")
				time.sleep(.5)
			except:
				log.exception("Unknown exceoption")
				raise
	except:
		log.exception("uncaught exception in display thread")
		halt_threads()


def set_tqdm(instance, new_value):
		instance.reset()
		instance.update(new_value)
		instance.refresh()


if __name__ == '__main__':
	print('Sense Show Starting as PID: ',os.getpid())
	print('crtl+\\ will print stats to the log file @ sense-debug.log')
	print('ctrl+c will gracefully exit')
	main()