import os
import sense_energy
import time
import logging
import threading
from tqdm import tqdm, trange

from queue import Queue


def main():
	global solar_queue, use_queue

	solar_queue = Queue()
	use_queue = Queue()
	functions = list()
	functions.append(print_solar)
	functions.append(print_use)
	threads = list()
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
		except:
			tqdm.write("Exception encountered.")
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
	fails=0
	for data in sense.get_realtime_stream():
		try:
			event = data
			solar_queue.put(event['d_solar_w'])
			use_queue.put(event['w'])
			tqdm.write("Updated " + str(event['frame']) )
			time.sleep(5)
		except Exception as ex:
			print(ex)


def update_bar(bar, last_val, val):

	if val <= 0:
		first = -val
		snd = -last_val
	else:
		first = last_val
		snd = val

	if snd > first:
		bar.update(snd - first)
	elif snd < first:
		bar.update(-first)
		bar.update(snd)
	return bar



def print_solar():
	global solar_queue
	t = tqdm(total=15000, unit="watts",miniters=1, position=1, unit_scale=True)
	last_val=0
	while 1:
		val = round(solar_queue.get())
		t=update_bar(t,last_val,val)

		t.refresh()
		last_val=val 

def print_use():
	global use_queue
	t = tqdm(total=6000, unit="watts",miniters=1, position=2)
	last_val=0
	while 1:
		val = round(use_queue.get())
		t=update_bar(t,last_val,val)

		t.refresh()
		last_val=val 


if __name__ == '__main__':	

	main()