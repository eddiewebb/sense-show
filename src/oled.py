import os
import time
from math import ceil
import logging
from PIL import Image, ImageFont, ImageDraw
logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')


class OLED:

	width = 128
	height = 32
	wheel_index = 0
	max_wheel_index = 16
	indicator_width = width / max_wheel_index


	def __init__(self):
		# Startup
		self.config()
		self.write("Hello pi!")


	def config(self):	
		if os.getenv("SENSE_TEST"):
			log.debug("Using console printout instead of OLED screen")
			from unittest.mock import Mock
			self.oled = Mock()
		else:
			log.debug("Using LED panel via neopixel")
			import board
			import busio			
			i2c = busio.I2C(board.SCL, board.SDA)
			import adafruit_ssd1306
			self.oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
			self.oled.fill(0)
			self.oled.show()
		self.font = ImageFont.load_default()
	
	def write(self, text):
		image = Image.new('1', (self.width, self.height))
		draw = ImageDraw.Draw(image)
		draw.text((10,0), text, font=self.font, fill=255)
		self.oled.image(image)
		self.oled.show()

	def clear(self):
		self.oled.fill(0)
		self.oled.show()


	def present(self, sense_data):
		image = Image.new('1', (self.width, self.height))
		draw = ImageDraw.Draw(image)
		now = int(time.time())
		if now % 10 == 0:
			# black box to clear every so often
			log.debug("Blacking screen to prevent burn in")
			self.clear()
		else:
			self.draw_charts(draw, sense_data)
		self.oled.image(image)
		self.oled.show()

	def draw_charts(self, draw, sense_data):
		y_start=21
		height = 10
		width = 50 
		text = "Usage: {}".format(self.scaled(sense_data['d_w']))
		pixs = draw.textsize(text,font=self.font)
		draw.text(((self.width - pixs[0])/2,0), text, font=self.font, fill=1)
		text = "> {} ".format(self.scaled(sense_data['grid_w']))
		draw.text((0,10), text, font=self.font, fill=1)
		text = "{} <".format(self.scaled(sense_data['d_solar_w']))		
		pixs = draw.textsize(text,font=self.font)
		draw.text((self.width - pixs[0],10), text, font=self.font, fill=1)

		# draw full empty box
		draw.rectangle((0,y_start, self.width-1, y_start + height),outline=1, fill=0)	

		y1 = y_start
		y2 = y_start + height
		if sense_data['grid_w'] > 0:
			# we are consuming, meter spins normal >>>>
			# draw triangle poiinting left
			self.wheel_index += 1
		elif sense_data['grid_w'] < 0:
			#we're giving back <<<<<<
			self.wheel_index -= 1
		if self.wheel_index > self.max_wheel_index:
			self.wheel_index = 0
		elif self.wheel_index < 0:
			self.wheel_index = self.max_wheel_index
		x1 = self.wheel_index * self.indicator_width
		x2 = x1 +  self.indicator_width
		#fill value left and or right with white 
		draw.rectangle((x1, y1, x2, y2),outline=1, fill=1)	

	def pixel_width_of(self, val, max, width):
		return ceil((val / max)*width)

	def scaled(self,val):
		if abs(val) > 1000:
			return "{} Kw".format(round(val/1000,1))
		else:
			return "{} w".format(val)


class mock_OLED:

	def __init__(self,width,height):
		print("Mock OLED Printing to console.")
		self.width=width
		self.height=height

	def image(self, image):
		self.image = image
	def show(self):
		print(self.image)

