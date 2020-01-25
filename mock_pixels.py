try:
    import _pixelbuf
except ImportError:
    import adafruit_pypixelbuf as _pixelbuf


class Pixels(_pixelbuf.PixelBuf):
	def __init__(self,n):
		self.n=n
		super().__init__(n, buf=bytearray(self.n * 3))

	def show(self):
		"""Shows the new colors on the pixels themselves if they haven't already
		been autowritten.
		The colors may or may not be showing after this function returns because
		it may be done asynchronously."""
		x=1

	def fill(self,color):
		x=1

