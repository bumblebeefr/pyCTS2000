# -*- coding: utf-8 -*-
from functools import wraps
import logging
import os.path
import serial
import re
import math
import requests

from const import *

logger = logging.getLogger(__name__)


def proxy(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if(args[0].proxy):
            resp = requests.post("%s/api/do" % args[0].proxy, json={
                "do": f.func_name,
                "args": args[1:],
                "kwargs": kwargs
            })
            return resp.json().get('response', None)
        return f(*args, **kwargs)

    return decorated_function


class CTS2000():

    def __init__(self, serialDevice=None, serialBaudrate=19200, usbDevice=None, proxy=None):
        '''
        Initialize the printer object you have to provide à valid SerialDevice (ex. /dev/ttyUSB0) or usbDevice (ex. /dev/usb/lpr1)
        '''
        self.usbDevice = None
        self.serialDevice = None
        self.serialBaudrate = None
        self.connection = None  # file or serial
        self.proxy = None

        if(proxy):
            self.proxy = proxy
        elif(serialDevice):
            self._init_serial(serialDevice, serialBaudrate)
        elif(usbDevice):
            self._init_usb(usbDevice)
        else:
            assert False, 'Unable to connect to printer device'

        self.encoding = 'ascii'

    def _init_usb(self, usbDevice):
        '''
            Initilize the printer object by using USB device (printer have to be installed).
        '''
        if(os.path.isfile(usbDevice)):
            logger.info("Connected to %s in text mode" % usbDevice)
            self.usbDevice = usbDevice
            self.connected = True
            self.connection = "file"

    def _init_serial(self, serialDevice, serialBaudrate):
        '''
            Initilize the printer object with a serial connection.
        '''
        self.serial = serial.Serial(port=serialDevice, baudrate=serialBaudrate)
        self.connection = "serial"

    @proxy
    def write(self, s):
        if(self.connection == 'file'):
            with open(self.usbDevice, "a") as f:
                f.write(s)
        elif self.connection == 'serial':
            self.serial.write(s)

    @proxy
    def feed(self, length=0):
        if(length):
            while length > 255:
                self.write(ESC + "J" + chr(255))
                length -= 255
            self.write(ESC + "J" + chr(length))
        else:
            self.write(LF)

    @proxy
    def cut(self, partial=False, lf_before=4, lf_after=1):
        line = []
        for k in range(lf_before):
            line.append(LF)
        if(partial):
            line.append(ESC + 'm')
        else:
            line.append(ESC + 'i')
        for k in range(lf_after):
            line.append(LF)
        self.write("".join(line))

    def _start_raster(self, mode, xL, xH, yL, yH):
        self.write(GS + 'v0')  # Printing of raster bit imag
        self.write(chr(mode))  # Print mode (0:normal, 1:double width, 2:double height, 3: quadruple size)
        self.write(chr(xL))  # xL
        self.write(chr(xH))  # xH
        self.write(chr(yL))  # yL
        self.write(chr(yH))  # yH

    @proxy
    def print_pbm_image(self, filename, mode=3):
        with open(filename, 'r') as f:
            while True:
                header = f.readline().strip()
                if header.startswith('#'):
                    continue
                elif header == 'P1':
                    assert False, 'ASCII format not supported'
                elif header == 'P4':
                    break
                else:
                    assert False, 'Bad format !'

            rows, cols = 0, 0
            while True:
                header = f.readline().strip()
                if header.startswith('#'):
                    continue
                else:
                    match = re.match('^(\d+) (\d+)$', header)
                    if match is None:
                        assert False, 'Bad size'
                    else:
                        cols, rows = match.groups()
                        break
            rows, cols = int(rows), int(cols)
            assert (rows, cols) != (0, 0)
            colbytes = int(math.ceil(cols / 8.0))

            xL, xH = colbytes % 256, int(math.floor(colbytes / 256.0))
            yL, yH = rows % 256, int(math.floor(rows / 256.0))

            if (xH > 255):
                assert False, "Image is too wide"

            if (yH > 8):
                assert False, "Image is too high"

            self._start_raster(mode, xL, xH, yL, yH)
            for n in range(0, rows):
                for m in range(0, colbytes):
                    mychar = f.read(1)
                    self.write(mychar)

    @proxy
    def beep(self, *args, **kwarg):
        self.write(ESC + BS)

    @proxy
    def select_font(self, size):
        self.write("".join([ESC, 'M', chr(size)]))

    @proxy
    def select_charset(self, charset=1):
        self.write("".join([ESC, 'R', chr(charset)]))

    @proxy
    def select_character_code_table(self, cct):
        self.encoding = ENCODINGS.get(cct, 'ascii')
        self.write("".join([ESC, 't', chr(cct)]))

    @proxy
    def echo(self, txt, autofeed=True, font=None, double_strike=None):
        '''
            Print the specified text, convert it to the correct character table if possible.
            If encoding error occurs, will try to select appropriate character table.
            A line feed is added by default, you can pass autofeed as False if you don't want it.
        '''
        if font is not None:
            self.select_font(font)

        if double_strike is not None:
            self.double_strike(double_strike)

        try:
            if isinstance(txt, unicode):
                self.write(txt.encode(self.encoding))
            else:
                self.write(txt.decode('utf8').encode(self.encoding))
        except:
            for letter in txt:
                for cct, encoding in ENCODINGS.items():
                    try:
                        if isinstance(letter, unicode):
                            encoded_letter = letter.encode(encoding)
                        else:
                            encoded_letter = letter.decode('utf8').encode(encoding)
                        self.select_character_code_table(cct)
                        self.write(encoded_letter)
                        logger.debug("'%s' letter sended as %s" % (letter, encoding))
                        break
                    except UnicodeEncodeError:
                        pass

        if autofeed:
            self.feed()

    @proxy
    def double_strike(self, double_strike=True):
        self.write("".join([ESC, 'G', chr(int(double_strike))]))
        