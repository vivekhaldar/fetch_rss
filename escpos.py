#!/usr/bin/python
'''
@author: Manuel F Martinez <manpaz@bashlinux.com>
@organization: Bashlinux
@copyright: Copyright (c) 2010 Bashlinux
@license: GPL
'''

import codecs
import Image
import time

from constants import *
from exceptions import *

class Escpos:
    """ ESC/POS Printer object """

    def __init__(self, filename):
        # self.prnfile = codecs.open(filename, encoding='utf-8', mode='w+')
        self.prnfile = open(filename, mode='w+')


    def _raw(self, msg):
        """ Print any of the commands above, or clear text """
        self.prnfile.write(msg)

    def _text(self, msg):
        self.prnfile.write(msg.encode('utf-8'))
        

    def _check_image_size(self, size):
        """Check and fix the size of the image to 32 bits"""
        if size % 32 == 0:
            return (0, 0)
        else:
            image_border = 32 - (size % 32)
            if (image_border % 2) == 0:
                return (image_border / 2, image_border / 2)
            else:
                return (image_border / 2, (image_border / 2) + 1)


    def _print_image(self, line, size):
        i = 0
        cont = 0
        buffer = ""
       
        self._raw(S_RASTER_N)
        buffer = "%02X%02X%02X%02X" % (((size[0]/size[1])/8), 0, size[1], 0)
        self._raw(buffer.decode('hex'))
        buffer = ""

        while i < len(line):
            hex_string = int(line[i:i+8],2)
            buffer += "%02X" % hex_string
            i += 8
            cont += 1
            if cont % 4 == 0:
                self._raw(buffer.decode("hex"))
                buffer = ""
                cont = 0

    def img2ascii(self, image):
        ascii_chars = [ '#', 'A', '@', '%', 'S', '+', '<', '*', ':', ',', '.']
	image_as_ascii = []
	all_pixels = list(image.getdata())
	for pixel_value in all_pixels:
		index = pixel_value / 25 # 0 - 10
		image_as_ascii.append(ascii_chars[index])
	return image_as_ascii	

    def asciiart(self, img):
	img = Image.open(img)
	width, heigth = img.size
	new_width = 32 
	new_heigth = int((heigth * new_width) / width)
	new_image = img.resize((new_width, new_heigth))
	new_image = new_image.convert("L") # convert to grayscale

	# now that we have a grayscale image with some fixed width we have to convert every pixel
	# to the appropriate ascii character from "ascii_chars"
	img_as_ascii = self.img2ascii(new_image)
	img_as_ascii = ''.join(ch for ch in img_as_ascii)
	for c in range(0, len(img_as_ascii), new_width):
            self._text(img_as_ascii[c:c+new_width])


    def image(self, img):
        """Parse image and then print it"""
        pixels   = []
        pix_line = ""
        im_left  = ""
        im_right = ""
        switch   = 0
        img_size = [ 0, 0 ]

        im_open = Image.open(img)
        im = im_open.convert("RGB")

        if im.size[0] > 512:
            print  "WARNING: Image is wider than 512 and could be truncated at print time "
        if im.size[1] > 255:
            raise ImageSizeError()

        im_border = self._check_image_size(im.size[0])
        for i in range(im_border[0]):
            im_left += "0"
        for i in range(im_border[1]):
            im_right += "0"

        for y in range(im.size[1]):
            img_size[1] += 1
            pix_line += im_left
            img_size[0] += im_border[0]
            for x in range(im.size[0]):
                img_size[0] += 1
                RGB = im.getpixel((x, y))
                im_color = (RGB[0] + RGB[1] + RGB[2])
                im_pattern = "1X0"
                pattern_len = len(im_pattern)
                switch = (switch - 1 ) * (-1)
                for x in range(pattern_len):
                    if im_color <= (255 * 3 / pattern_len * (x+1)):
                        if im_pattern[x] == "X":
                            pix_line += "%d" % switch
                        else:
                            pix_line += im_pattern[x]
                        break
                    elif im_color > (255 * 3 / pattern_len * pattern_len) and im_color <= (255 * 3):
                        pix_line += im_pattern[-1]
                        break 
            pix_line += im_right
            img_size[0] += im_border[1]

        self._print_image(pix_line, img_size)


    def barcode(self, code, bc, width, height, pos, font):
        """ Print Barcode """
        # Align Bar Code()
        self._raw(TXT_ALIGN_CT)
        # Height
        if height >=2 or height <=6:
            self._raw(BARCODE_HEIGHT)
        else:
            raise BarcodeSizeError()
        # Width
        if width >= 1 or width <=255:
            self._raw(BARCODE_WIDTH)
        else:
            raise BarcodeSizeError()
        # Font
        if font.upper() == "B":
            self._raw(BARCODE_FONT_B)
        else: # DEFAULT FONT: A
            self._raw(BARCODE_FONT_A)
        # Position
        if pos.upper() == "OFF":
            self._raw(BARCODE_TXT_OFF)
        elif pos.upper() == "BOTH":
            self._raw(BARCODE_TXT_BTH)
        elif pos.upper() == "ABOVE":
            self._raw(BARCODE_TXT_ABV)
        else:  # DEFAULT POSITION: BELOW 
            self._raw(BARCODE_TXT_BLW)
        # Type 
        if bc.upper() == "UPC-A":
            self._raw(BARCODE_UPC_A)
        elif bc.upper() == "UPC-E":
            self._raw(BARCODE_UPC_E)
        elif bc.upper() == "EAN13":
            self._raw(BARCODE_EAN13)
        elif bc.upper() == "EAN8":
            self._raw(BARCODE_EAN8)
        elif bc.upper() == "CODE39":
            self._raw(BARCODE_CODE39)
        elif bc.upper() == "ITF":
            self._raw(BARCODE_ITF)
        elif bc.upper() == "NW7":
            self._raw(BARCODE_NW7)
        else:
            raise BarcodeTypeError()
        # Print Code
        if code:
            self._raw(code)
        else:
            raise exception.BarcodeCodeError()

        
    def text(self, txt):
        """ Print alpha-numeric text """
        if txt:
            self._text(txt)
        else:
            raise TextError()

    def bigtext(self, txt):
       self.set(height=2, width=1)
       self.text(txt)
       self.set(type='normal')


    def set(self, align='left', font='a', type='normal', width=1, height=1):
        """ Set text properties """
        # Align
        if align.upper() == "CENTER":
            self._raw(TXT_ALIGN_CT)
        elif align.upper() == "RIGHT":
            self._raw(TXT_ALIGN_RT)
        elif align.upper() == "LEFT":
            self._raw(TXT_ALIGN_LT)
        # Font
        if font.upper() == "B":
            self._raw(TXT_FONT_B)
        else:  # DEFAULT FONT: A
            self._raw(TXT_FONT_A)
        # Type
        if type.upper() == "B":
            self._raw(TXT_BOLD_ON)
        elif type.upper() == "U":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL_ON)
        elif type.upper() == "U2":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL2_ON)
        elif type.upper() == "BU":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL_ON)
        elif type.upper() == "BU2":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL2_ON)
        elif type.upper == "NORMAL":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL_OFF)
        # Width
        if width == 2 and height != 2:
            self._raw(TXT_NORMAL)
            self._raw(TXT_2WIDTH)
        elif height == 2 and width != 2:
            self._raw(TXT_NORMAL)
            self._raw(TXT_2HEIGHT)
        elif height == 2 and width == 2:
            self._raw(TXT_2WIDTH)
            self._raw(TXT_2HEIGHT)
        else: # DEFAULT SIZE: NORMAL
            self._raw(TXT_NORMAL)


    def control(self, ctl):
        """ Feed control sequences """
        if ctl.upper() == "LF":
            self._raw(CTL_LF)
        elif ctl.upper() == "FF":
            self._raw(CTL_FF)
        elif ctl.upper() == "CR":
            self._raw(CTL_CR)
        elif ctl.upper() == "HT":
            self._raw(CTL_HT)
        elif ctl.upper() == "VT":
            self._raw(CTL_VT)


    def flush(self):
       self.prnfile.flush()


    def __del__(self):
        """ Release device interface """
        self.prnfile.close()
