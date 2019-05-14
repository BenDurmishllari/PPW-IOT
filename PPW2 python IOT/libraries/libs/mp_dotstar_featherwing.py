import time
from libs.mp_dotstar import DotStar 
class DotstarFeatherwing:
	blank_stripe = [(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0),(0,0,0)]
	def __init__(self,spi=None,*,cpin,dpin,brightness=1.0):
		self.rows=6
		self.columns=12
		self.display=DotStar(spi=spi,cpin=cpin,dpin=dpin,n=self.rows*self.columns,brightness=brightness,auto_write=False)
	def clear(self):
		self.display.fill((0,0,0))
	def fill(self,color):
		self.display.fill(color)
	def show(self):
		self.display.show()
	def set_color(self,row,column,color):
		self.display[row*self.columns+column]=color
	def shift_into_left(self,stripe):
		for r in range(self.rows):
			rightmost=r*self.columns
			for c in range(self.columns-1):
				self.display[rightmost+c]=self.display[rightmost+c+1]
			self.display[rightmost+self.columns-1]=stripe[r]
	def shift_into_right(self,stripe):
		for r in range(self.rows):
			leftmost=((r+1)*self.columns)-1
			for c in range(self.columns-1):
				self.display[leftmost-c]=self.display[(leftmost-c)-1]
			self.display[(leftmost-self.columns)+1]=stripe[r]
	def number_to_pixels(self,x,color):
		val=x
		pixels=[]
		for b in range(self.rows):
			if val&1==0:
				pixels.append((0,0,0))
			else:
				pixels.append(color)
			val=val>>1
		return pixels
	def character_to_numbers(self,font,char):
		return font[char]
	def shift_in_character(self,font,c,color=(0x00,0x40,0x00),delay=0.2):
		if c.upper() in font:
			matrix=self.character_to_numbers(font,c.upper())
		else:
			matrix=self.character_to_numbers(font,'UNKNOWN')
		for stripe in matrix:
			self.shift_into_right(self.number_to_pixels(stripe,color))
			self.show()
			time.sleep(delay)
		self.shift_into_right(self.blank_stripe)
		self.show()
		time.sleep(delay)
	def shift_in_string(self,font,s,color=(0x00,0x40,0x00), delay=0.2):
		for c in s:
			self.shift_in_character(font,c,color,delay)
	def display_image(self,image,color):
		self.display_colored_image(image,{'X':color})
	def display_colored_image(self,image,colors):
		for r in range(self.rows):
			for c in range(self.columns):
				index=r*self.columns+((self.columns-1)-c)
				key=image[r][c]
				if key in colors:
					self.display[index]=colors[key]
				else:
					self.display[index]=(0,0,0)
		self.display.show()
	def display_animation(self,animation,colors,count=1,delay=0.1):
		self.clear()
		first_frame=True
		while count>0:
			for frame in animation:
				if not first_frame:
					time.sleep(delay)
				first_frame=False
				self.display_colored_image(frame, colors)
			count=count-1
