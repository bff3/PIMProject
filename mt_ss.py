#Libraries
import RPi.GPIO as GPIO
import time
import socket
#import serial
import re
# import thread module 
from _thread import *
import threading

# gpio pins used
TRIGGER_PINS = [4, 27, 5, 13]
BS_T_R = 18
BS_T_L = 24
ECHO_PINS = [17, 22, 6, 19]
BS_E_R = 25
BS_E_L = 23

# time between sensor readings
CYCLE_TIME = 2

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#size of moving average sample
N = 40

#Bounds for signal magnitude
UPPER = 200
LOWER = 4

# min distance a vehicle can get to your car
MIN_BS_DIST = 20
MAX_BS_DIST = 125 

# distance function from https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
# returns distance measured by ultrasonic proximity sensor
def distance(trig, echo):
	#set GPIO direction (IN / OUT)
	GPIO.setup(trig, GPIO.OUT)
	GPIO.setup(echo, GPIO.IN)
	# set Trigger to HIGH
	GPIO.output(trig, True)

	# set Trigger after 0.01ms to LOW
	time.sleep(0.00001)
	GPIO.output(trig, False)
	
	StartTime = time.time()
	StopTime = time.time()

	# save StartTime
	while GPIO.input(echo) == 0:
		StartTime = time.time()

	# save time of arrival
	while GPIO.input(echo) == 1:
		StopTime = time.time()

	# time difference between start and arrival
	TimeElapsed = StopTime - StartTime
	# multiply with the sonic speed (34300 cm/s)
	# and divide by 2, because there and back
	distance = (TimeElapsed * 34300) / 2
	
	time.sleep(CYCLE_TIME)
	return distance

# returns a list of distances from each sensor
def multi_distance(trig_pins, echo_pins):
	print('mtd')
	dlist = []
	for i, t in enumerate(trig_pins):
		dlist.append(distance(t, echo_pins[i]))
	print(dlis)
	return dlist

# read values from the probes, filter them with moving average, and send them on cntn
def read_filter_send(cnctn, trig_pins, echo_pins):
	print("rfs")
	sig_sample = []
	probe_average = 1  
	while True:
		# read distance from probe(s)
		readings = multi_distance(trig_pins, echo_pins)
		print(readings)
		distance_list = []
		for dist in readings:
			# filter in pass band
			if (dist < UPPER) and (dist > LOWER):
				# add sample to sample array
				sig_sample.append(dist)
				# if max number of samples is reached, pop off oldest sample
				if (len(sig_sample) > N):
					sig_sample.pop(0)
			# calculate average of samples
			filtered_dist = int(round(sum(sig_sample)/len(sig_sample)))
			distance_list.append(filtered_dist)
		#send on cnctn socket
		cnctn.send((str(min(distance_list)) + '\n').encode())

# listens for connection, if connection fails, continue listening for one
def rear_proximity_multi(s):
	while True:
		s.listen(5) 
		print("sockets are listening") 

		# establish connection with client 
		c, addr = s.accept()
		print('Connected to :', addr[0], ':', addr[1])
		try:
			read_filter_send(c, TRIGGER_PINS, ECHO_PINS)
		except:  
			c.close()


# basically read_filter_send and rear_proximity_multi but for blind spot sensors
def blind_spot(s):
	while True:
		s.listen(5) 
		print("sockets are listening") 

		# establish connection with client 
		c, addr = s.accept()
		print('Connected to :', addr[0], ':', addr[1])	
		try:
			BS_state = '00'
			sig_sample = []
			probe_average = 1
			while True:
				# read distance from blind spot sensors
				dist_L = distance(BS_T_L, BS_E_L)
				print(dist_L)
				dist_R = distance(BS_T_R, BS_E_R)
				filtered_dist = [1, 1]
				for i, dist in enumerate([dist_L]):
					# filter in pass band
					if (dist < UPPER) and (dist > LOWER):
						# add sample to sample array
						sig_sample.append(dist)
						# if max number of samples is reached, pop off oldest sample
						if (len(sig_sample) > N):
							sig_sample.pop(0)
					# calculate average of samples
					probe_average = sum(sig_sample)/len(sig_sample)
					filtered_dist[i] = int(round(probe_average))
				
				# Switch statement for distance values
				if (filtered_dist[0] > MIN_BS_DIST) and (filtered_dist[0] < MAX_BS_DIST):
					BS_state = '1' + BS_state[1]
				else:
					BS_state = '0' + BS_state[1]
				if (filtered_dist[1] > MIN_BS_DIST) and (filtered_dist[1] < MAX_BS_DIST):
					BS_state = BS_state[0] + '1'
				else:
					BS_state = BS_state[0] + '0'

				c.send((BS_state + '\n').encode())
			
		except Exception as e:
			print(e)
			c.close()
			print("socket closed")

def Main(): 
	host = "" 
	# reverse a port on your computer 
	port0 = 9999
	port1 = 12345
	Main.s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	Main.s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	Main.s0.bind((host, port0))
	print("socket binded to post", port0)
	Main.s1.bind((host, port1)) 
	print("socket binded to post", port1) 
	
	# start server functions
	start_new_thread(rear_proximity_multi, (Main.s0,))
	blind_spot(Main.s1)


if __name__ == '__main__': 
	try:
		Main()
	except KeyboardInterrupt:
		GPIO.cleanup()
		Main.s0.close()
		Main.s1.close()
		exit()
    
