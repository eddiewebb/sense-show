#
# This class is a local mock of neopxels API
# https://github.com/adafruit/Adafruit_CircuitPython_NeoPixel/blob/master/neopixel.py
# Modified by Edward A. Webb, original authors copyright below
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Damien P. George
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from blessings import Terminal
import time
import logging
logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')


# Pixel color order constants
RGB = (0, 1, 2)
"""Red Green Blue"""
GRB = (1, 0, 2)
"""Green Red Blue"""
RGBW = (0, 1, 2, 3)
"""Red Green Blue White"""
GRBW = (1, 0, 2, 3)
"""Green Red Blue White"""

class Pixels():



	def __init__(self,n):
		self.n=n
		self.bpp=3
		self.order = RGB
		self.buf = bytearray(self.n * self.bpp)
		self.fill((0,0,0))
		self.t = Terminal()

	def show(self):
		for y in range(1,9):
			row = "|"
			for x in range(1, 33):
				cell = self.__getitem__(self.get_id_by_coordinates(x,y))
				#color=[str(x) for x in cell]
				#log.debug("printing cell {}",color)
				if cell > (0,0,0):
					row+="-X-|"
				else:
					row+="   |"
			with self.t.location(0, self.t.height - (14-y)):
				print(row)
		time.sleep(.10)	

	def fill(self,color):
		for y in range(1,9):
			for x in range(1, 33):
				if color > (0,0,0):
					print('| X ', end='')
				else:
					print('| O ', end='')
			print('|')
				

	def deinit(self):
		self.fill((0,0,0))


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


	def __len__(self):
		return len(self.buf) // self.bpp

		
	def _set_item(self, index, value):
		if index < 0:
			index += len(self)
		if index >= self.n or index < 0:
			raise IndexError
		offset = index * self.bpp
		r = 0
		g = 0
		b = 0
		w = 0
		if isinstance(value, int):
			if value>>24:
				raise ValueError("only bits 0->23 valid for integer input")
			r = value >> 16
			g = (value >> 8) & 0xff
			b = value & 0xff
			w = 0
			# If all components are the same and we have a white pixel then use it
			# instead of the individual components.
			if self.bpp == 4 and r == g and g == b:
				w = r
				r = 0
				g = 0
				b = 0
		elif (len(value) == self.bpp) or ((len(value) == 3) and (self.bpp == 4)):
			if len(value) == 3:
				r, g, b = value
			else:
				r, g, b, w = value
		else:
			raise ValueError("Color tuple size does not match pixel_order.")

		self.buf[offset + self.order[0]] = r
		self.buf[offset + self.order[1]] = g
		self.buf[offset + self.order[2]] = b
		if self.bpp == 4:
			self.buf[offset + self.order[3]] = w

	def __setitem__(self, index, val):
		if isinstance(index, slice):
			start, stop, step = index.indices(len(self.buf) // self.bpp)
			length = stop - start
			if step != 0:
				length = math.ceil(length / step)
			if len(val) != length:
				raise ValueError("Slice and input sequence size do not match.")
			for val_i, in_i in enumerate(range(start, stop, step)):
				self._set_item(in_i, val[val_i])
		else:
			self._set_item(index, val)


	def __getitem__(self, index):
		if isinstance(index, slice):
			out = []
			for in_i in range(*index.indices(len(self.buf) // self.bpp)):
				out.append(tuple(self.buf[in_i * self.bpp + self.order[i]]
								 for i in range(self.bpp)))
			return out
		if index < 0:
			index += len(self)
		if index >= self.n or index < 0:
			raise IndexError
		offset = index * self.bpp
		return tuple(self.buf[offset + self.order[i]]
					 for i in range(self.bpp))
