import socket
import yaml
import sys
import time

def send_input(button):
	data = {
		"type": "input",
		"button": button
	}

	yaml_str = yaml.dump(data)
	yaml_bytes = yaml_str.encode("utf-8")
	client_sock.sendall(yaml_bytes)

# Connect to socket server
server_address = ("0.0.0.0", 8881)

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	client_sock.connect(server_address)
	print("Connection successful!")

except:
	print("Connection failed, is port not online?")
	sys.exit(0)

# Testing, send a B button every 5 seconds
while True:
	send_input("B")
	time.sleep(5)

# finally:
# 	client_sock.close()
# 	print("Connection terminated.")

