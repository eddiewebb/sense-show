import os
from math import ceil
import logging
from PIL import Image, ImageFont, ImageDraw
logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')


class OLED:

	width = 128
	height = 32
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
	
	def present(self, sense_data):
		image = Image.new('1', (self.width, self.height))
		draw = ImageDraw.Draw(image)
		self.draw_charts(draw, sense_data)
		self.oled.image(image)
		self.oled.show()

	def draw_charts(self, draw, sense_data):
		y_start=21
		height = 10
		width = 50 # either half of chart
		#chart_start = self.width/4
		solar_pixels = round((sense_data['d_solar_w'] / sense_data['max_solar'])*width)
		#draw.rectangle((chart_start,0, chart_start + width, height),outline=1, fill=0)
		#draw.rectangle((chart_start,0, chart_start + solar_pixels, height),outline=1, fill=1)
		text = "Solar: {}".format(sense_data['d_solar_w'])
		draw.text((0,0), text, font=self.font, fill=1)
		use_pixels =round((sense_data['d_w'] / sense_data['max_use']) * width)
		#draw.rectangle((chart_start,10, chart_start + width, 10 + height),outline=1, fill=0)
		#draw.rectangle((chart_start,10, chart_start + use_pixels, 10 +  height),outline=1, fill=1)
		text = "Usage: {}   ({} from grid)".format(sense_data['d_w'], sense_data['grid_w'])
		draw.text((0,10), text, font=self.font, fill=1)

		# draw full empty box
		draw.rectangle((0,y_start, self.width-1, y_start + height),outline=1, fill=0)		
		y1 = y_start
		y2 = y_start + height
		x1 = x2 = self.width/2
		if sense_data['grid_w'] > 0:
			# we are consuming, show bar starting left of center
			x1 = x1 - self.pixel_width_of(sense_data['grid_w'], sense_data['max_use'], width)
			log.debug("plot x1 at %d",x1)
		if sense_data['d_solar_w'] > 0:
			#we're not consuing, we shouldbe prodincg
			x2 = x2 + self.pixel_width_of(sense_data['d_solar_w'], sense_data['max_solar'],width)
			log.debug("plot x2 at %d",x2)
		log.debug("use plot as (%d,%d),(%d,%d)",x1, y1, x2, y2)
		draw.rectangle((x1, y1, x2, y2),outline=1, fill=1)	
		draw.line((50,y_start, 50, y_start+height), fill=1, width=2)

	def pixel_width_of(self, val, max, width):
		return ceil((val / max)*width)

class mock_OLED:

	def __init__(self,width,height):
		print("Mock OLED Printing to console.")
		self.width=width
		self.height=height

	def image(self, image):
		self.image = image
	def show(self):
		print(self.image)

