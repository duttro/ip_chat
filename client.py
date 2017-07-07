# telnet program example
import socket, select, string, sys
import Queue
import threading
import time

# 042317 rdutt adding threads and queues
# 042917 rdutt so the pi zero only has one core

def talk(s, r_q, t_q):
  #user entered a message
  if not t_q.empty():
      msg = t_q.get()
      s.send(msg)
   
  socket_list = [sys.stdin, s]  
  # Get the list sockets which are readable
  read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

  for sock in read_sockets:
    #incoming message from remote server
    if sock == s:
      data = sock.recv(4096)
      if not data :
          print >>sys.stderr, '\nDisconnected from chat server'
          sys.exit()
      else :
          #print data
          #print >>sys.stderr,"comloop recv %s"%(data)
          r_q.put(data);
    
######################################################################
#main function
if __name__ == "__main__":
 
  print >>sys.stderr, 'setup queues';
  r_queue = Queue.Queue()
  t_queue = Queue.Queue()
    
  print >>sys.stderr, "about to Start COMloop";
  print >>sys.stderr, "Start MAINloop";
  
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.settimeout(20)
  
  print >>sys.stderr,"connect to remote host"
  try :
      s.connect(('192.168.1.126', 5000))
      #self.s.settimeout(None)
  except :
      print >>sys.stderr, 'Unable to connect'
      sys.exit()

  while 1:    
    if not r_queue.empty():
      r_msg = r_queue.get()
      print >>sys.stderr, "MAINloop recv "
      print >>sys.stderr, "%s"%(r_msg)
    else :
      i, o, e = select.select( [sys.stdin], [], [], 1 )

      if (i):
        message =  sys.stdin.readline().strip()
        t_queue.put(message)
    
    talk(s, r_queue, t_queue)
       
    time.sleep(.25);
    

    
