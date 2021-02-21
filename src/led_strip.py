import os
import time
import math
import operator
from datetime import datetime


import logging
logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')
brightness = 0.5

GRID=[1,2,3]
GFLOW=[3,4,5,6,7,8,9,10,11,12,13,14,15]
HOUSE=[14,15,16,17,18]
SFLOW=[17,18,19,20,21,22,24,25,26,27,28,29,30,31]
SOLAR=[30,31,32]

class LedStrip:


	off=(0,0,0)
	color_green=(0,80,0)
	color_gold=(255,215,0)
	color_orange=(80,40,0)
	color_teal=(0,80,80)
	color_red=(80,0,0)
	color_purple=(128,0,128)
	color_gray=(112,128,144)
	color_wood=(139,69,19)



	def __init__(self):
		log.debug("intializinfg LED matrix..")
		# Startup
		self.set_pixels()
		self.flow(1,32,8000,8000,self.color_teal, False)
		self.flow(32,1,8000,8000,self.color_purple, False)
		self.waterfall(1,8)
		self.draw_grid()
		self.flow(32,24,8000,8000,self.color_orange, False)
		self.draw_panels()		
		self.flow(16,19,8000,8000,self.color_green, False)
		self.flow(16,13,8000,8000,self.color_green, False)
		self.draw_plug()

		log.debug("LED ready!")


	def reset(self):
		log.debug("pixels reset")
		self.set_pixels()


	def set_pixels(self):	
		if os.getenv("SENSE_TEST"):
			log.debug("Using console printout instead of LEDs")
			import mock_pixels
			self.pixels = mock_pixels.Pixels(256)
		else:
			log.debug("Using LED panel via neopixel")
			import board
			import neopixel			
			self.pixels = neopixel.NeoPixel(board.D18, 256, auto_write=False, brightness=0.5)
			self.pixels.fill(self.off)


	def get_id_by_coordinates(self,x,y):
		id=0
		if x > 32 or y > 8:
			raise BaseException("invaliud coordinted, must be < 32:8, coordinates start top left")
		if x % 2 == 0:
			# even rows count up from bottom
			id=(x*8)-y
		else:
			# odd coordinates (first column, 3rd colunm, count down from top left.)
			id=((x-1)*8)+(y-1)
		return id


	def chase(self):
		for i in range(0,259): # notice we go over!!
			if i > 0 and i < 256:
				self.pixels[i] = (0,255,0) # green
			if i > 1  and i-1 < 256:
				self.pixels[i-1] = (255,0,0) #red
			if i > 2  and i-2 < 256:
				self.pixels[i-2] = (0,0,255) #blyue
			if i > 3  and i-3 < 256:
				self.pixels[i-3] = (0,0,0) #off
			self.pixels.show()


	def waterfall(self, start, end):
		stop = end + 1
		for x in range(start, stop + 3): # 32 columns, left to right, range expects 1 over ending,and  need to clear 3 tailing colors 
			for y in range(1, 8 + 1): # 8 rows, top down
				if x > 0 and x < stop:
					self.pixels[self.get_id_by_coordinates(x,y)] = (255,0,0) # red
				if x > 1  and x - 1 < stop:
					self.pixels[self.get_id_by_coordinates(x-1,y)] = (255,99,71) #tomato
				if x > 2  and x - 2 < stop:
					self.pixels[self.get_id_by_coordinates(x-2,y)] = (255,127,80) #coral
				if x > 3  and x - 3 < stop:
					self.pixels[self.get_id_by_coordinates(x-3,y)] = (0,0,0) #off
			self.pixels.show()	


	def flow(self, start, end, rate, max_rate, color, safe_set=True):
		#rate is rows we fillfor x in range(1,32 + 3 + 1): # 32 columns, left to right, range expects 1 over ending,and  need to clear 3 tailing colors 
		flock = math.floor((rate / max_rate) * 7) + 1
		if end > start:
			for x in range(start, end + 1 + flock): # 8 rows, top down, clear flock, 1 more to clear self		
				self.inner_flow(x, flock, color, start, end)
		elif end < start:
			for x in reversed(range(end-flock, start + 1)): # 8 rows, top down, clear flock, 1 more to clear self		
				self.inner_flow(x, flock, color, start, end, 1, operator.ge, operator.le)


	def inner_flow(self, x, flock, color, start, end, tail=-1, lessThan=operator.le, greaterThan=operator.ge, safe_set=True):	
		marker = self.mark
		if safe_set:
			marker = self.safe_set
		for y in reversed(range(9-flock,9)):
			if lessThan(x, end):
				marker(x,y,color)
			if greaterThan(x + tail*flock, start) and lessThan(x + tail*flock, end):
				try:
					marker(x + tail*flock,y,self.off, color) #off
				except:
					marker(x + tail*flock,y,self.off) #off

		self.pixels.show()

	def safe_set(self, x, y, color, only=(0,0,0)):
		id=self.get_id_by_coordinates(x,y)
		now = self.pixels[id]
		if isinstance(now, list):
			#log.debug("converting leist")
			now = tuple(int(i*(1/brightness)) for i in now)
		#log.debug("Pixel currently %s, will only replace if %s",now, only)
		if now != only:
			#log.debug("will not repalce with %s", color)
			return
		#log.debug("will replace with %s", color)
		self.pixels[id] = color



	"""
	Set certain LED positions to status.

	Must call leds.flush() or self.pixels.show() after all leds are marked!
	"""
	def mark(self, x,y,color):
		self.pixels[self.get_id_by_coordinates(x,y)] = color

	def show_sun(self, yes):	
		if yes:
			color = self.color_gold
		else:
			color = self.off
		self.mark(32,1, color)
		self.mark(32,2, color)
		self.pixels.show()

	def flow_solar(self,value,max):
		if value > 0:
			self.flow(SFLOW[-1],SFLOW[0], value, max, self.color_orange)
		else:
			self.flow(SFLOW[0],SFLOW[-1], -value, max, self.color_red)

	def flow_grid(self,value,max):
		if value > 0:
			self.flow(GFLOW[0],GFLOW[-1], value, max, self.color_red)
		else:
			self.flow(GFLOW[-1],GFLOW[0], -value, max, self.color_green)


	def draw_house(self):
		for x in HOUSE:
			for y in reversed(range(4,9)):
				if (y == 5) or ((y > 5 or y==4) and x > HOUSE[0] and x < HOUSE[4])  :
					self.mark(x,y,self.color_wood)
			self.mark(HOUSE[2],3,self.color_wood)
		self.pixels.show()

	def draw_plug(self):
		for x in HOUSE:
			for y in reversed(range(1,9)):
				if y == 4 or ( y in range(2,7) and x in(HOUSE[1],HOUSE[-2]) ) or ( y > 3 and x == HOUSE[2] ) :
					self.mark(x,y,self.color_wood)
		self.pixels.show()

	def draw_panels(self):
		for x in SOLAR:
			for y in reversed(range(1,9)):
				if x in (32,31) and y in(3,6,9):
					self.mark(x,y,self.color_gray)
				if x in (31,30) and y in (2,5,8):
					self.mark(x,y,self.color_gray)
		self.pixels.show()

	def draw_grid(self):
		for x in GRID:
			for y in reversed(range(2,9)):
				if x ==2 or y in (2,4):
					self.mark(x,y,self.color_purple)
		self.pixels.show()

	def flush(self):
		self.pixels.show()

	def clear(self):
		self.pixels.fill((0,0,0))
