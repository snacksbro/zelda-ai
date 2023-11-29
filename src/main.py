import socket
import yaml
import json
import sys
import time

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

# Connect to socket server
server_address = ("0.0.0.0", 8886)

# Generate a client object
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect, if failure, terminate
try:
	client_sock.connect(server_address)
	print("Connection successful!")

except:
	print("Connection failed, is port not online?")
	sys.exit(0)

# Get time data
res = client_sock.recv(1024)
res = json.loads(res.decode("utf-8"))

if (res["type"] == "timer"):
	current_time = int(res["current"])
	max_time = int(res["max"])
	print("Time captured successfully!")
else:
	print("Got unexpected packet of type " + res["type"])

# Testing, send a B button every 5 seconds
while True:
	send_input("B")
	time.sleep(5)

# finally:
# 	client_sock.close()
# 	print("Connection terminated.")

