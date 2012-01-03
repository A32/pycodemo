# Echo client program
import socket

HOST = '192.168.0.107'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print 'connected'
msg = raw_input()
s.send(msg)
data = s.recv(1024)
s.close()
print 'Received', repr(data)
