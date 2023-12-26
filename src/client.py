"""
This is the client module. It is responsible for interacting with the Lua
server to send/recieve data
"""

import socket
import json
import sys

# import time

CURRENT_TIME = 0
MAX_TIME = 0
CURRENT_BITMAP = ""
PORT = 8888
model_info = {
    "step_num": 0,
    "episode_num": 0,
    "current_reward": 0,
}


def update_model_info(step_num, episode_num, current_reward):
    """
    This function will update the model_info global
    Args:
        step_num (int): The step number to set it to
        episode_num (int): The episode number to set it to
        current_reward (int): The reward to set it to
    Returns:
        None
    """
    model_info["step_num"] = step_num
    model_info["episode_num"] = episode_num
    model_info["current_reward"] = current_reward


def send_input(button):
    """
    This function will send the button input to the Lua socket server
    Args:
        button (str): The button's name to send
    Returns:
        None
    """
    data = {"type": "input", "button": button, "model_info": model_info}

    # This is a surprise tool that will help us later
    json_str = json.dumps(data) + "\n"  # Just kidding, socket needs a newline
    json_bytes = json_str.encode("utf-8")
    client_sock.sendall(json_bytes)
    print("Sent some input")


def send_reset():
    """
    This function will tell the socket server to reset the emulator
    Args:
        None
    Returns:
        None
    """
    data = {"type": "reset"}
    json_str = json.dumps(data) + "\n"  # Just kidding, socket needs a newline
    json_bytes = json_str.encode("utf-8")
    client_sock.sendall(json_bytes)
    print("Sent some input")


# update_time: Receives and parses the time packet
# returns: A tuple (CURRENT_TIME, MAX_TIME) on success, 0 on failure
def update_time():
    """
    This function will recieve the time from the Lua server so both are in sync
    Args:
        None
    Returns:
        A tuple containing the current time and the max time (to rollover)
    """
    # Get time data
    res = client_sock.recv(1024)
    res = json.loads(res.decode("utf-8"))

    if res["type"] == "timer":
        CURRENT_TIME = int(res["current"])
        MAX_TIME = int(res["max"])
        print("Time captured successfully!")
        print("Got " + str(CURRENT_TIME) + " and " + str(MAX_TIME))
        return (CURRENT_TIME, MAX_TIME)
    print("Got unexpected packet of type " + res["type"])
    return 0


def recieve_bitmap():
    """
    This function will recieve bitmap of the entire game screen from the server
    Args:
        None
    Returns:
        A matrix containing hexcodes of each pixel in the screen
    """
    res = b""
    for i in range(541):  # Lil magic number
        buf = client_sock.recv(1024)  # 500KB
        res += buf
        # Selective printing for debug purposes
        if i in (0, 1, 540):
            print("got a packet..", i, buf)

    res = json.loads(res.decode("utf-8"))

    if res["type"] == "screen":
        CURRENT_BITMAP = res["raw_bitmap"]
        print("Bitmap recieved successfully!")
        return CURRENT_BITMAP  # May change this up to only set or return
    print("Got unexpected packet of type " + res["type"])
    return 0


def recieve_positions():
    """
    This function will recieve the positions from the Lua server
    Args:
        None
    Returns:
        A tuple containing a the player and enemies positions
    """
    res = client_sock.recv(1024)
    res = json.loads(res.decode("utf-8"))

    if res["type"] == "positions":
        print("Positions recieved!\nGot", res["player"], res["enemy"])
        return (res["player"], res["enemy"])
    print("Got unexpected packet of type " + res["type"])
    return 0


def recieve_percept():
    """
    This function will recieve the percept (in the form of what's on the
    screen, player health, and player positions) and return it
    Args:
        None
    Returns:
        A table containing raw_bitmap (the screen), player (player position),
        enemy (enemy position), and player_health (player health)
    """
    res = b""
    for i in range(541):  # Lil magic number
        buf = client_sock.recv(1024)  # 500KB
        res += buf
        if i in (0, 1, 540):
            print("got a packet..", i, buf)

    res = json.loads(res.decode("utf-8"))
    if res["type"] == "percept":
        CURRENT_BITMAP = res["raw_bitmap"]
        print("Positions recieved!\nGot", res["player"], res["enemy"])
        print("Health: ", res["player_health"])
        print("got bitmap!")
        return res
        # return (
        #     current_bitmap,
        #     res["player"],
        #     res["enemy"],
        #     res["player_is_crouching"],
        #     res["player_is_attacking"],
        #     res["player_health"],
        # )
    print("Got unexpected packet of type " + res["type"])
    return 0


# Connect to socket server
server_address = ("0.0.0.0", PORT)

# Generate a client object
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Attempt to connect, if failure, terminate
try:
    client_sock.connect(server_address)
    print("Connection successful!")

except EnvironmentError:
    print("Connection failed, is port not online?")
    sys.exit(0)
