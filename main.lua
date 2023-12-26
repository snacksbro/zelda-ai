-- luacheck: ignore emu
-- luacheck: ignore joypad
-- luacheck: ignore savestate
-- luacheck: ignore memory
-- luacheck: ignore gui
local socket = require("socket.core")
local json = require("json")

local server, ip, port -- Scoping
local _PORT = 8888
local sock = socket.tcp() -- "Master" object created

-- Use a random port offered by the OS, or a predetermined?
if not _PORT then
	server = assert(sock:bind("*", 0)) -- Binding master to port
else
	server = assert(sock:bind("*", _PORT)) -- Binding master to port
end

-- If the port was obtained...
if server then
	ip, port = sock:getsockname() -- Pulling out the ip/port listening
	print("Port opened!\nWaiting on " .. ip .. ":" .. port)
	sock:listen(-1) -- -1 means it can accept infinite clients. Now this is a "server" object
else
	print("Error occured attempting to bind to port")
end

-- print(server)
-- local ip, port = server:getsockname()

local function build_bitmap()
	local bitmap = {}
	-- Not indexing from zero
	for x = 1, 256 do
		bitmap[x] = {}
		for y = 1, 240 do
			local red, green, blue, palette = emu.getscreenpixel(x - 1, y - 1, true)
			bitmap[x][y] = string.format("%02x%02x%02x", red, green, blue)
			-- bitmap[x][y] = {
			-- 	r = red,
			-- 	g = green,
			-- 	b = blue
			-- }
		end
	end

	return bitmap
end

local function send_positions(client)
	local player_pos_addr = 0x004D
	local enemy_pos_addr = 0x0050

	local data = {
		type = "positions",
		player = memory.readbyte(player_pos_addr),
		enemy = memory.readbyte(enemy_pos_addr),
	}

	client:send(json.encode(data) .. "\n")
end

local function send_bitmap(client, bitmap)
	local data = {
		type = "screen",
		raw_bitmap = bitmap,
	}

	print("Sent bitmap of length " .. string.len(json.encode(data)))
	client:send(json.encode(data) .. "\n")
end

local function send_percept(client, bitmap)
	local player_pos_addr = 0x004D
	local enemy_pos_addr = 0x0050
	local player_crouch_addr = 0x0017 -- 0 = is, 1 = not
	local player_attack_addr = 0x020D -- o = can, ~0 = cooldown
	local player_health = 0x0774
	-- local enemy_health

	local data = {
		type = "percept",
		raw_bitmap = bitmap,
		player = memory.readbyte(player_pos_addr),
		enemy = memory.readbyte(enemy_pos_addr),
		player_is_crouching = memory.readbyte(player_crouch_addr),
		player_is_attacking = memory.readbyte(player_attack_addr),
		player_health = memory.readbyte(player_health),
	}

	client:send(json.encode(data) .. "\n")
end

local function print_bitmap(bitmap)
	for x = 0, #bitmap do
		for y = 0, #bitmap[x] do
			print(bitmap[x][y])
		end
	end
end

-- socket_start: Halts the program until a socket opens
-- returns: client object as referenced in https://w3.impa.br/~diego/software/luasocket/tcp.html
local function socket_start()
	print("Waiting for connection...")
	local client = sock:accept() -- Accept a new connection
	client:settimeout(5) -- Set timeout to 5 seconds
	print("New connection established")
	return client
end

-- reset_input: Resets all buttons to nil (off)
-- input_dict: The main input dictionary
local function reset_input(input_dict)
	for key, _ in pairs(input_dict) do
		input_dict[key] = nil
	end
end

-- set_timer: Sends a packet to the client to sync time
-- client: The client object
-- current_time: The current frame count
-- max_time: The highest the time can be before it "restarts"
local function set_timer(client, current_time, max_time)
	local data = {
		type = "timer",
		current = current_time,
		max = max_time,
	}

	client:send(json.encode(data) .. "\n")
end

-- execute_input: Sets parameter of buttons to be "down"
-- buttons[]: Strings of each button in relation to input dictionary
local function exectute_input(buttons)
	reset_input(input)
	-- for button in buttons do
	-- Doesn't quite support multiple buttons yet
	input[buttons] = true
	-- end
end

-- local function model_info.update(packet)
-- 	-- Updating max_reward if it's a new record
-- 	if packet.current_reward > model_info["max_reward"] then
-- 		model_info["max_reward"] = packet.current_reward
-- 	end
-- 	-- Updating the rest of the variables regardless
-- 	model_info["current_reward"] = packet.current_reward
-- 	model_info["episode_num"] = packet.episode_num
-- 	model_info["step_num"] = packet.step_num
-- 	-- TODO: Implement timing and have a function to convert to minutes
-- end

-- local function draw_model_info(model_info)
-- 	local model_string = "Step/Episode: "
-- 		.. model_info["step_num"]
-- 		.. "/"
-- 		.. model_info["episode_num"]
-- 		.. "\nCurrent/Max Reward: "
-- 		.. model_info["current_reward"]
-- 		.. "/"
-- 		.. model_info["max_reward"]
-- 		.. "\nEpisode/Total Time Elapsed: "
-- 		.. model_info["time_elapsed_episode"]
-- 		.. "/"
-- 		.. model_info["time_elapsed_total"]
-- 	gui.drawtext(0, 0, model_string)
-- end

-- parse_packet: Reads the "type" field of the JSON packet and calls appropriate functions
-- packet: A JSON string received from the client
local function parse_packet(packet)
	local packet_table = json.decode(packet)

	-- If there's model_info. With this, a packet can include both commands and keep the model updated
	if packet_table["model_info"] ~= nil then
		model_info:update(packet_table["model_info"])
	end

	-- Input packets...
	if packet_table["type"] == "input" then
		exectute_input(packet_table["button"])
	end

	if packet_table["type"] == "reset" then
		local state = savestate.object(10)
		savestate.load(state)
	end
end

-- socketRunner: Called at a set interval, locks program until input is received by client
-- client: The client object as generated from socket_start()
local function socketRunner(client)
	local line, err = client:receive("*l") -- Reading ONLY until a newline
	if not err then
		print("Received data from client: " .. line)
		-- Process the received data as needed
		parse_packet(line)

		-- Example: Send a response back to the client
		-- client:send("Server received your message: " .. line .. "\n")
	else
		print("Error encountered. Reconnecting...")
		socket_start()
	end
	-- client:close() -- Close the client connection
end
emu.speedmode("normal") -- Set emulator speed
-- The gamepad input table
local input = {
	up = nil,
	down = nil,
	left = nil,
	right = nil,
	A = nil,
	B = true,
	start = nil,
	select = nil,
}

-- The model information. Time is stored in seconds
model_info = {
	episode_num = 0,
	step_num = 0,
	current_reward = 0,
	max_reward = 0,
	time_elapsed_total = 0,
	time_elapsed_episode = 0,
	update = function(self, packet)
		-- Updating max_reward if it's a new record
		if packet.current_reward > self.max_reward then
			self.max_reward = packet.current_reward
		end
		-- Updating the rest of the variables regardless
		self.current_reward = packet.current_reward
		self.episode_num = packet.episode_num
		self.step_num = packet.step_num
		-- TODO: Implement timing and have a function to convert to minutes
	end,
	draw = function(self)
		local model_string = "Step/Episode: "
			.. self.step_num
			.. "/"
			.. self.episode_num
			.. "\nCurrent/Max Reward: "
			.. self.current_reward
			.. "/"
			.. self.max_reward
			.. "\nEpisode/Total Time Elapsed: "
			.. self.time_elapsed_episode
			.. "/"
			.. self.time_elapsed_total
		gui.drawtext(0, 0, model_string)
	end,
}

local client = socket_start()
local framecount = 0
local framelimit = 60

-- Ensuring Python is "aware" of the time
set_timer(client, framecount, framelimit)

-- Messing with OS. May just make a runfile instead...
-- local command = "dir"
-- local stdout = io.popen(command, "r")

-- if stdout then
-- 	local output = stdout:read("*a")
-- 	print(output)
-- 	stdout:close()
-- end

while true do
	framecount = (framecount + 1) % framelimit -- Rollover per second
	-- Once a second...
	if framecount == 0 then
		local bitmap = build_bitmap()
		-- send_bitmap(client, bitmap)
		-- send_positions(client)
		send_percept(client, bitmap)

		-- print_bitmap(bitmap)
		socketRunner(client)
		joypad.set(1, input) -- Spam a and start
	end
	emu.frameadvance()
	model_info:draw()
end
