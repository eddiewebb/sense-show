import os
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
		width = 50
		height = 10
		solar_pixels = round((sense_data['d_solar_w'] / sense_data['max_solar'])*width)
		draw.rectangle((self.width/4,0, width, height),outline=1, fill=0)
		draw.rectangle((self.width/4,0, solar_pixels, height),outline=1, fill=1)
		text = "Solar: {}".format(sense_data['d_solar_w'])
		draw.text((0,0), text, font=self.font, fill=1)
		use_pixels =round((sense_data['d_w'] / sense_data['max_use']) * width)
		draw.rectangle((self.width/4,10, width, height),outline=1, fill=0)
		draw.rectangle((self.width/4,10, use_pixels, height),outline=1, fill=1)
		text = "Usage: {}".format(sense_data['d_solar_w'])
		draw.text((0,10), text, font=self.font, fill=1)


class mock_OLED:

	def __init__(self,width,height):
		print("Mock OLED Printing to console.")
		self.width=width
		self.height=height

	def image(self, image):
		self.image = image
	def show(self):
		print(self.image)

