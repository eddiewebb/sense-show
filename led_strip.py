import os
import time
import math
import operator


class LedStrip:
	off=(0,0,0)
	color_green=(0,80,0)
	color_orange=(80,40,0)
	color_teal=(0,80,80)
	color_red=(80,0,0)
	color_purple=(128,0,128)



	def __init__(self):
		# Startup
		self.set_pixels()
		self.flow(1,32,8000,8000,self.color_orange)



	def reset(self):
		self.set_pixels()


	def set_pixels(self):
	
		if os.getenv("SENSE_TEST"):
			import mock_pixels
			self.pixels = mock_pixels.Pixels(256)
		else:
			import board
			import neopixel			
			self.pixels = neopixel.NeoPixel(board.D18, 256, auto_write=False, brightness=0.5)



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



		#time.sleep(.005)

	def waterfall(self):
		for x in range(1,32 + 3 + 1): # 32 columns, left to right, range expects 1 over ending,and  need to clear 3 tailing colors 
			for y in range(1, 8 + 1): # 8 rows, top down
				if x > 0 and x < 33:
					self.pixels[self.get_id_by_coordinates(x,y)] = (126,126,126) # green
				if x > 1  and x - 1 < 33:
					self.pixels[self.get_id_by_coordinates(x-1,y)] = (60,100,60) #red
				if x > 2  and x - 2 < 33:
					self.pixels[self.get_id_by_coordinates(x-2,y)] = (20,40,20) #blyue
				if x > 3  and x - 3 < 33:
					self.pixels[self.get_id_by_coordinates(x-3,y)] = (0,0,0) #off
			self.pixels.show()	

	def flow(self, start, end, rate, max_rate, color):
		#rate is rows we fillfor x in range(1,32 + 3 + 1): # 32 columns, left to right, range expects 1 over ending,and  need to clear 3 tailing colors 
		flock = math.floor((rate / max_rate) * 7) + 1
		if end > start:
			for x in range(start, end + 1 + flock): # 8 rows, top down, clear flock, 1 more to clear self		
				self.inner_flow(x, flock, color, start, end)
		elif end < start:
			for x in reversed(range(end-flock, start + 1)): # 8 rows, top down, clear flock, 1 more to clear self		
				self.inner_flow(x, flock, color, start, end, 1, operator.ge, operator.le)


	def inner_flow(self, x, flock, color, start, end, tail=-1, operat=operator.le, operat2=operator.ge):	
		for y in reversed(range(9-flock,9)):
			if operat(x, end):
				self.pixels[self.get_id_by_coordinates(x,y)] = color # red
			if operat2(x + tail*flock, start) and operat(x + tail*flock, end):
				self.pixels[self.get_id_by_coordinates(x + tail*flock,y)] = (0,0,0) #red
		self.pixels.show()

	"""
	Set certain LED positions to status.

	Must call leds.flush() or self.pixels.show() after all leds are marked!
	"""
	def mark(self, x,y,color):
		self.pixels[self.get_id_by_coordinates(x,y)] = color

	def show_sun(self, yes):	
		if yes:
			color = self.color_orange
		else:
			color = off
		self.mark(32,1, color)
		self.mark(32,2, color)
		self.pixels.show()

	def draw_house(self):
		for x in range(15,19):
			for y in reversed(range(5,9)):
				if x in (16,17) or y == 6:
					self.mark(x,y,self.color_teal)
		self.pixels.show()

	def draw_panels(self):
		for x in range(30,33):
			for y in reversed(range(1,9)):
				if x == 30 and y < 5:
					self.mark(x,y,self.color_teal)
				if x == 31 and y in (3,4,5,6):
					self.mark(x,y,self.color_teal)
				if x == 32 and y in (5,6,7,8):
					self.mark(x,y,self.color_teal)
		self.pixels.show()

	def draw_grid(self):
		for x in range(1,4):
			for y in reversed(range(4,9)):
				if x ==2 or y in (4,6):
					self.mark(x,y,self.color_purple)
		self.pixels.show()

	def flush(self):
		self.pixels.show()

	def clear(self):
		self.pixels.fill((0,0,0))
