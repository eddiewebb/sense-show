import os
import logging
from PIL import Image, ImageFont, ImageDraw
logging.basicConfig(filename='sense-debug.log',level=logging.DEBUG)
log = logging.getLogger('senseshow.main')


class OLED:

	def __init__(self):
		# Startup
		self.config()
		self.write("Hello pi!")


	def config(self):	
		if os.getenv("SENSE_TEST"):
			log.debug("Using console printout instead of OLED screen")
			import mock_pixels
			self.oled = mock_OLED(128,32)
		else:
			log.debug("Using LED panel via neopixel")
			import board
			import busio			
			i2c = busio.I2C(board.SCL, board.SDA)
			import adafruit_ssd1306
			self.oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
			oled.fill(0)
			oled.show()
		self.font = ImageFont.load_default()

	def write(self, text):
		image = Image.new('1', (self.oled.width, self.oled.height))
		draw = ImageDraw.Draw(image)
		draw.text((0,0), text, font=self.font, fill=255)
		self.oled.image(image)
		self.oled.show()


class mock_OLED:

	def __init__(self,width,height):
		print("Mock OLED Printing to console.")
		self.width=width
		self.height=height

	def image(self, image):
		self.image = image
	def show(self):
		print(self.image)

