#!/usr/bin/env python3
# setup
import socket
import RPi.GPIO as GPIO

# GPIO setup
BS_LEFT = 16
BS_RIGHT = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup([BS_LEFT, BS_RIGHT], GPIO.OUT)

# socket setup
HOST, PORT = "192.168.4.1", 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# main loop
try:
	while True:
		# test if already connected to server
		try:
			recieved = sock.recv(1024)
			recieved = str(recieved.decode('ascii')) 
		# if not connected to server keep trying until it succeeds
		except OSError:
			print('trying to connect')	
			try:
				sock.connect((HOST, PORT))
				recieved = sock.recv(1024)
				recieved = str(recieved.decode('ascii')) 
				print('connection to {} succeded'.format((HOST, PORT)))
			except (OSError, ConnectionRefusedError):
				print('connection to {} failed'.format((HOST, PORT)))
				continue
		
		print('recieved {} from server'.format(recieved))

		# activate the appropriate warning light
		if int(recieved[0]) == 1:
			GPIO.output(BS_LEFT, GPIO.HIGH)
			#print("left light activated")
		else:
			GPIO.output(BS_LEFT, GPIO.LOW)
		if int(recieved[1]) == 1:
			GPIO.output(BS_RIGHT, GPIO.HIGH)
			#print("right light activated")
		else:
			GPIO.output(BS_RIGHT, GPIO.LOW)

# cleanup
except:
	sock.close()
	GPIO.cleanup()