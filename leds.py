import board
import neopixel

leds = list()
leds.append([0,1])
leds.append([15,14])


pixels = neopixel.NeoPixel(board.D18, 256)
for i in range(0,255):
	pixel[i] = (0,0,0)
