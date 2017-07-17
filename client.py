# telnet program example
import socket, select, string, sys
import Queue
import threading
import time

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# 042317 rdutt adding threads and queues
# 042917 rdutt so the pi zero only has one core
# 070717 rdutt added update_display for micro display

def update_display(IP,tx,rx):
  # Create blank image for drawing.
  # Make sure to create image with mode '1' for 1-bit color.
  width = disp.width
  height = disp.height
  image = Image.new('1', (width, height))
  
  # Draw some shapes.
  # First define some constants to allow easy resizing of shapes.
  padding = -2
  top = padding
  bottom = height-padding
  # Move left to right keeping track of the current x position for drawing shapes.
  x = 0

  # Get drawing object to draw on image.
  draw = ImageDraw.Draw(image)
  # Load default font.
  font = ImageFont.load_default()

  # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
  # Some other nice fonts to try: http://www.dafont.com/bitmap.php
  # font = ImageFont.truetype('Minecraftia.ttf', 8)
  
  # Draw a black filled box to clear the image.
  draw.rectangle((0,0,width,height), outline=0, fill=0)
  
  # Write two lines of text.
  draw.text((x, top),       "IP: " + str(IP),  font=font, fill=255)
  draw.text((x, top+8),     tx, font=font, fill=255)
  draw.text((x, top+16),    rx, font=font, fill=255)
  #draw.text((x, top+25),    str(Disk),  font=font, fill=255)
  
  # Display image.
  disp.image(image)
  disp.display()
  time.sleep(.1)  



def talk(s, r_q, t_q):
  #user entered a message
  if not t_q.empty():
      msg = t_q.get()
      s.send(msg)
   
  socket_list = [sys.stdin, s]  
  # Get the list sockets which are readable
  read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

  if not disconnected:
    for sock in read_sockets:
      #incoming message from remote server
      if sock == s:
        data = sock.recv(4096)
        if not data :
            print >>sys.stderr, '\nDisconnected from chat server'
            return True
        else :
            #print data
            #print >>sys.stderr,"comloop recv %s"%(data)
            r_q.put(data);
            return False
  else:
    return False        
    
######################################################################
#main function
if __name__ == "__main__":
  disconnected = True
  
  #################################################################
  # Raspberry Pi pin configuration:
  RST = None     # on the PiOLED this pin isnt used
  
  # Note the following are only used with SPI:
  DC = 23
  SPI_PORT = 0
  SPI_DEVICE = 0
  
  # 128x32 display with hardware I2C:
  disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
  
  # Initialize library.
  disp.begin()
  
  # Clear display.
  disp.clear()
  disp.display()
  
  # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
  cmd = "hostname -I | cut -d\' \' -f1"
  IP = subprocess.check_output(cmd, shell = True )
  tx="tx"
  rx="rx"
  update_display(IP,tx,rx)
  #################################################################
  print >>sys.stderr, 'setup queues';
  r_queue = Queue.Queue()
  t_queue = Queue.Queue()
    
  print >>sys.stderr, "about to Start COMloop";
  print >>sys.stderr, "Start MAINloop";
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)
  
  

  while 1:    
    if disconnected :
      print >>sys.stderr,"connect to remote host"
      try :
          s.connect(('192.168.1.126', 5000))
          disconnected == False
          #self.s.settimeout(None)
      except :
          print >>sys.stderr, 'Unable to connect'
          disconnected = True
          #sys.exit()
    
    
    
    
    
    
    if not r_queue.empty():
      r_msg = r_queue.get()
      rx=str(r_msg).split('>')[1]
      update_display(IP,tx,rx)
      print >>sys.stderr, "MAINloop recv "
      print >>sys.stderr, "%s"%(r_msg)
    else :
      i, o, e = select.select( [sys.stdin], [], [], 1 )

      if (i):
        message =  sys.stdin.readline().strip()
        tx=str(message).split('>')[1]
        update_display(IP,tx,rx)
        t_queue.put(message)
    
    disconnected = talk(s, r_queue, t_queue)
       
    time.sleep(.25);
    

    
