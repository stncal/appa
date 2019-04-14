#!/usr/bin/python3
import argparse
import sys
from PIL import Image, ImageMath

# COLOR CODES
CRESET = '\33[0m'
CGREEN = '\33[32m'
CRED   = '\33[31m'


# Purpose:	attempt to get the image with the PIL module 
# Returns:	a copy of the image so the original image doesn't change at all
def get_image(img):
	try:
		# open the image in read only mode so we don't modify the original image
		image = Image.open(img, 'r')
	except IOError:
		print("[-] Error opening image {}".format(img))
		sys.exit()
	return image.copy()


# Purpose:	see if the message passed to appa can actually fit in the image 
# Returns:	status of this check
def text_fits(message, image):
	image_size = get_pixel_count(image)
	if len(message)*3 > image_size:
		if debug:
			print(CRED + "[!] Image not large enough for the message!" + CRESET)
			print("Image size: {}".format(image_size))
			print("Pixels needed for message: {}".format(len(message*3)))
		return False
	else:			
		print("==> Image data")
		print("\tImage size: {}".format(image_size))
		print("\tPixels needed for message: {}\n".format(len(message*3)))
		return True


# Purpose:	get the number of pixels in the image to ensure the message we are trying to 
#			inject will fit 
# Returns:	the number of pixels in the image
def get_pixel_count(image):
	width, height = image.size
	return width * height


# Purpose:	convert the message provided to appa to binary 
# Returns:	the binary version of the message with a space separating each letter 
def get_binary_string(msg):
	bin_list = [bin(ord(x))[2:].zfill(8) for x in msg]
	print("==> Binary string data")
	print("\tLetters from message [{}] in binary:".format(msg))
	for bin_string in bin_list:
		print("\t{}".format(bin_string))
	binary_msg = ''.join(bin_list)
	return binary_msg


# Purpose:	get the specific pixels from the image that we are going to modify
# Notes:	we need 3 * the length of the message pixels because letters are 8 bit 
def get_pixels(pixel_count, image):
	pixels = list(image.getdata())[0:pixel_count]
	if debug: print_status("PIXELS TO BE MODIFIED:\n", pixels)
	print("==> Pixel data")
	print("\tPixels to be modified:\n{}\n".format(pixels))
	return pixels


# Purpose:	get the bitmaps for every letter in the message we are encoding 
# Yields:	a list of every set of pixels that needs to be changed  
def get_bitmaps(pixels):
	start = 0
	end = 3
	ascii_len = int(len(pixels) / 3)
	
	for x in range(0, ascii_len):
		bitmap = pixels[start:end]
		if debug: print_status("", bitmap)
		
		yield list(bitmap[0])
		yield list(bitmap[1])
		yield list(bitmap[2])
		
		start+=3
		end+=3

	return


def mod_bitmap(bitmap, bstring):
	print("==> Bitmap modification")

	bitmap = list(bitmap)

	# for parsing through the binary string that is 8 bit 0's and 1's
	bstring_start = 0
	bstring_end   = 8

	# for parsing through the current substring that maps to the pixel list
	substring_start = 0
	substring_end   = 3

	# keep track of when we are at the end of the pixel list for a single letter
	end_pixel_list = 0
	
	for x in range(0, len(bitmap)):
		p = 0

		if x%3 == 0: 
			substring = bstring[bstring_start:bstring_end]
			bstring_start+=8
			bstring_end+=8
			substring_start = 0
			substring_end   = 3
			print("\t(", end="")

		for y in substring[substring_start:substring_end]:
			if y == "0":
				if is_even(bitmap[x][p]):
					print("{}".format(bitmap[x][p]), end=", ")
				else:
					bitmap[x][p] -= 1
					print(CGREEN + "{}".format(bitmap[x][p]) + CRESET, end=", ")
				if debug:
					print("Needs to be even ", end=", ")
					print(bitmap[x][p])
			else:
				if is_even(bitmap[x][p]):
					bitmap[x][p] -= 1
					print(CGREEN + "{}".format(bitmap[x][p]) + CRESET, end=", ")
				else:
					print("{}".format(bitmap[x][p]), end=", ")
				if debug:
					print("Needs to be odd ", end="")
					print(bitmap[x][p])
			p+=1
			
		if end_pixel_list == 2:
			# set the last bit of the pixel list
			# odd: end of changes
			# even: more changes to be made

			# we are on the last bit value - make it odd
			if x == len(bitmap)-1:
				# change to odd to terminate changes
				if is_even(bitmap[x][2]):
					bitmap[x][2]-=1
					print(CGREEN + "{}".format(bitmap[x][2]) + CRESET + ")")
				else:
					print("{})".format(bitmap[x][2]))
			elif is_even(bitmap[x][2]):
				print("{})".format(bitmap[x][2]))
			else:
				bitmap[x][2]-=1
				print(CGREEN + "{}".format(bitmap[x][2]) + CRESET + ")")
			end_pixel_list = 0
		else:
			end_pixel_list+=1
		
		substring_end+=3
		substring_start+=3

		if debug: 
			print(bitmap[x][0])
			print(bitmap[x][1])
			print(bitmap[x][2])
	
	return bitmap



def is_even(num):
	if num % 2 == 0:
		return True
	else:
		return False


# Purpose:	print the status to the screen when in debug mode 
#			with fancy formatting that now doesn't have to be copied & pasted a ton
def print_status(message, value):
	print(CGREEN + "\n[!] " + CRESET, end="")
	print("{} {}\n".format(message, value))
	return


if __name__ == "__main__":
	global debug
	global report
	debug = False
	report = False

	parser = argparse.ArgumentParser(description="Interactive steganography")

	parser.add_argument("message",
			help="Message to inject in the image")
	parser.add_argument("image",
			help="Image to inject a message into")
	parser.add_argument("-d", "--debug", action="store_true",
			help="Debug mode")

	args = parser.parse_args()

	if args.debug:
		debug = True

	image = get_image(args.image)

	if not text_fits(args.message, image):
		print("Message too large for image. Please find a bigger image")
		sys.exit()

	pixel_count = len(args.message)*3
	pixels = get_pixels(pixel_count, image)
	bstring = get_binary_string(args.message)
	bitmap = get_bitmaps(pixels)
	mod_bitmap(bitmap, bstring)
