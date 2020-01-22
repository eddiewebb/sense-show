import board
import neopixel
import time

#
#. our led is a strip essentially folded every 8 lights, zig zagging
# so the id at coordinates 0:0 is 0, but id at 1:0 (2nd column, first row) is 15 !
#

def __init__():
	pixels = neopixel.NeoPixel(board.D18, 256)
	waterfall()

def get_id_by_coordinates(x,y):
	id=0
	if x > 32 or y > 8:
		raise("invaliud coordinted, must be < 32:8, coordinates start top left")
	if x % 2 == 0:
		# even rows count up from bottom
		id=(x*8)-y
	else:
		# odd coordinates (first column, 3rd colunm, count down from top left.)
		id=((x-1)*8)+(y-1)
	return id

def chase():
	for i in range(0,259): # notice we go over!!
		if i > 0 and i < 256:
			pixels[i] = (0,255,0) # green
		if i > 1  and i-1 < 256:
			pixels[i-1] = (255,0,0) #red
		if i > 2  and i-2 < 256:
			pixels[i-2] = (0,0,255) #blyue
		if i > 3  and i-3 < 256:
			pixels[i-3] = (0,0,0) #off


	#time.sleep(.005)

def waterfall():
	for x in range(1,32):
		for y in range(1,8):
			id = get_id_by_coordinates(x,y)
			pixels[id] = (126,126,255)

