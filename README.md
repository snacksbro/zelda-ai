# Zelda Gymnasium
This project is an AI that uses reinforcement learning to battle the final boss the game, Dark Link.

## Dependencies
* [FCEUX](https://fceux.com/web/home.html), Windows version with LuaSocket pre-packaged
* [Python3](https://www.python.org/)
* Pip (should come with Python)
* Everything in `src/requirements.txt`
* (Optional) virtualenv (via `pip install virtualenv`)

## Installation
1. Clone the repo
2. Navigate to the `src/` folder
3. (Optional) Create a new virtual environment `virtualenv .`
4. (Optional) Enter the environment with `source bin/activate`
5. Run `pip install -r requirements.txt`

## Running
### Starting the Server/Emulator
1. Start FCEUX
2. Load up a Zelda II (PAL release) ROM (not provided)
3. Load the savestate located in the root directory `zelda2-darklink.sav`
4. In FCEUX, go to File, then Open Lua Script
5. Select `main.lua` and hit Run

### Starting the Client/AI
1. Navigate to `src/`
2. (Optional) Enter the environment with `source bin/activate`
3. Run `python3 client.py`

Both FCEUX and your terminal's consoles should begin producing output, and Link should begin doing random button presses to learn.

