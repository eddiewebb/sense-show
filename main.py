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
			stats = dict()
			stats['from_grid']=data['grid_w']
			stats['from_solar']=data['d_solar_w']
			stats['use']=data['d_w']
			solar_queue.put(stats)
			use_queue.put(stats)
			# also 'grid_w' which is how many of d_w' comes from grid, not solar
			tqdm.write("Updated " + str(data['frame']) )
			time.sleep(1)
		except Exception as ex:
			print(ex)


def update_bar(bar, last_val, val, total):
	bar.total=total
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
	t = tqdm(total=15000, unit="watts",miniters=1, position=1, unit_scale=True, leave=True)
	last_val=0
	while 1:
		val = solar_queue.get()
		#t=update_bar(t,last_val,val['from_solar'],val['use'])
		t.reset()
		t.update(val['from_solar'])
		t.refresh()
		last_val=val['from_solar'] 

def print_use():
	global use_queue
	t = tqdm(total=15000, unit="watts",miniters=1, position=2, unit_scale=True)
	last_val=0
	while 1:
		val = use_queue.get()
		t=update_bar(t,last_val,val['use'],15000)

		t.refresh()
		last_val=val['use'] 


if __name__ == '__main__':	

	main()