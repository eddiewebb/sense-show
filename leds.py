import board
import neopixel
import time

leds = list()
leds.append([0,1])
leds.append([15,14])


pixels = neopixel.NeoPixel(board.D18, 256)
for i in range(0,258): # notice we go over!!
	if i > 0 and i < 256:
		pixels[i-1] = (0,255,0)
	if i > 1  and i < 256:
		pixels[i-2] = (255,0,0)
	if i > 2  and i < 256:
		pixels[i-3] = (0,0,255)
	if i > 3  and i < 256:
		pixels[i-4] = (0,0,0)
	time.sleep(.05)




