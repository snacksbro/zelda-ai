import socket
import json
import sys

# import time

CURRENT_TIME = 0
MAX_TIME = 0
current_bitmap = ""
port = 8888
model_info = {"step_num": 0, "episode_num": 0, "current_reward": 0}


def execute_AI():
    pass


def screen_processor(image):
    pass


def player_is_dead():
    return False


def update_model_info(step_num, episode_num, current_reward):
    model_info["step_num"] = step_num
    model_info["episode_num"] = episode_num
    model_info["current_reward"] = current_reward


# send_input: Sends a button event to the server
# button: The button (string) to send
def send_input(button):
    data = {"type": "input", "button": button, "model_info": model_info}

    # This is a surprise tool that will help us later
    json_str = json.dumps(data) + "\n"  # Just kidding, socket needs a newline
    json_bytes = json_str.encode("utf-8")
    client_sock.sendall(json_bytes)
    print("Sent some input")


def send_reset():
    data = {"type": "reset"}
    json_str = json.dumps(data) + "\n"  # Just kidding, socket needs a newline
    json_bytes = json_str.encode("utf-8")
    client_sock.sendall(json_bytes)
    print("Sent some input")


# update_time: Receives and parses the time packet
# returns: A tuple (CURRENT_TIME, MAX_TIME) on success, 0 on failure
def update_time():
    # Get time data
    res = client_sock.recv(1024)
    res = json.loads(res.decode("utf-8"))

    if res["type"] == "timer":
        CURRENT_TIME = int(res["current"])
        MAX_TIME = int(res["max"])
        print("Time captured successfully!")
        print("Got " + str(CURRENT_TIME) + " and " + str(MAX_TIME))
        return (CURRENT_TIME, MAX_TIME)
    else:
        print("Got unexpected packet of type " + res["type"])
        return 0


def recieve_bitmap():
    res = b""
    for i in range(541):  # Lil magic number
        buf = client_sock.recv(1024)  # 500KB
        res += buf
        if i == 0 or i == 1 or i == 540:
            print("got a packet..", i, buf)

    res = json.loads(res.decode("utf-8"))

    if res["type"] == "screen":
        current_bitmap = res["raw_bitmap"]
        print("Bitmap recieved successfully!")
        return current_bitmap  # May change this up to only set or return
    else:
        print("Got unexpected packet of type " + res["type"])
        return 0


def recieve_positions():
    buf = client_sock.recv(1024)
    res = json.loads(res.decode("utf-8"))

    if res["type"] == "positions":
        print("Positions recieved!\nGot", res["player"], res["enemy"])
        return (res["player"], res["enemy"])
    else:
        print("Got unexpected packet of type " + res["type"])
        return 0


def recieve_percept():
    res = b""
    for i in range(541):  # Lil magic number
        buf = client_sock.recv(1024)  # 500KB
        res += buf
        if i == 0 or i == 1 or i == 540:
            print("got a packet..", i, buf)

    res = json.loads(res.decode("utf-8"))
    if res["type"] == "percept":
        current_bitmap = res["raw_bitmap"]
        print("Positions recieved!\nGot", res["player"], res["enemy"])
        print("Health: ", res["player_health"])
        print("got bitmap!")
        return res
        # return (current_bitmap, res["player"], res["enemy"], res["player_is_crouching"], res["player_is_attacking"], res["player_health"])
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
