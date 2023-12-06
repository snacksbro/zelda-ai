import socket
import yaml
import json
import sys
import time

current_time = 0
max_time = 0
current_bitmap = ""
port = 8887

def screen_processor(image):
	pass

# send_input: Sends a button event to the server
# button: The button (string) to send
def send_input(button):
	data = {
		"type": "input",
		"button": button
	}

	# This is a surprise tool that will help us later
	json_str = json.dumps(data) + '\n' # Just kidding, socket needs a newline
	json_bytes = json_str.encode("utf-8")
	client_sock.sendall(json_bytes)
	print("Sent some input")

# update_time: Receives and parses the time packet
# returns: A tuple (current_time, max_time) on success, 0 on failure
def update_time():
	# Get time data
	res = client_sock.recv(1024)
	res = json.loads(res.decode("utf-8"))

	if (res["type"] == "timer"):
		current_time = int(res["current"])
		max_time = int(res["max"])
		print("Time captured successfully!")
		print("Got " + str(current_time) + " and " + str(max_time))
		return (current_time, max_time)
	else:
		print("Got unexpected packet of type " + res["type"])
		return 0

def recieve_bitmap():
	res = b""
	for i in range(541): # Lil magic number
		buf = client_sock.recv(1024) # 500KB
		res += buf
		if (i == 0 or i == 1 or i == 540):
			print("got a packet..", i, buf)

	res = json.loads(res.decode("utf-8"))

	if (res["type"] == "screen"):
		current_bitmap = res["raw_bitmap"]
		print("Bitmap recieved successfully!")
		return current_bitmap # May change this up to only set or return
	else:
		print("Got unexpected packet of type " + res["type"])
		return 0

def recieve_positions():
	buf = client_sock.recv(1024)
	res = json.loads(res.decode("utf-8"))

	if (res["type"] == "positions"):
		print("Positions recieved!\nGot", res["player"], res["enemy"])
		return (res[player], res[enemy])
	else:
		print("Got unexpected packet of type " + res["type"])
		return 0

def recieve_percept():
	res = b""
	for i in range(541): # Lil magic number
		buf = client_sock.recv(1024) # 500KB
		res += buf
		if (i == 0 or i == 1 or i == 540):
			print("got a packet..", i, buf)

	res = json.loads(res.decode("utf-8"))
	if (res["type"] == "percept"):
		current_bitmap = res["raw_bitmap"]
		print("Positions recieved!\nGot", res["player"], res["enemy"])
		print("got bitmap!")
		return (current_bitmap, res["player"], res["enemy"], res["player_is_crouching"], res["player_is_attacking"])
	else:
		print("Got unexpected packet of type " + res["type"])
		return 0

# Connect to socket server
server_address = ("0.0.0.0", port)

# Generate a client object
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect, if failure, terminate
try:
	client_sock.connect(server_address)
	print("Connection successful!")

except:
	print("Connection failed, is port not online?")
	sys.exit(0)

current_time, max_time = update_time()

# Testing, send a B button every 5 seconds
while True:
	current_time = (current_time + 1) % max_time
	if (current_time == 0):
		# bitmap = recieve_bitmap()
		# positions = recieve_positions()
		percept = recieve_percept()
		send_input("B")
		# time.sleep(5)

# finally:
# 	client_sock.close()
# 	print("Connection terminated.")

