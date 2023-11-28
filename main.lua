local socket = require("socket.core")
local json = require("json")

local server, ip, port -- Scoping
local _PORT = 8886
local sock = socket.tcp() -- "Master" object created

-- Use a random port offered by the OS, or a predetermined?
if not _PORT then
	server = assert(sock:bind("*", 0)) -- Binding master to port
else
	server = assert(sock:bind("*", _PORT)) -- Binding master to port
end

-- If the port was obtained...
if (server) then
	ip, port = sock:getsockname() -- Pulling out the ip/port listening
	print("Port opened!\nWaiting on " .. ip .. ":" .. port)
	sock:listen(-1) -- -1 means it can accept infinite clients. Now this is a "server" object
else
	print("Error occured attempting to bind to port")
end

-- print(server)
-- local ip, port = server:getsockname()

-- socket_start: Halts the program until a socket opens
-- returns: client object as referenced in https://w3.impa.br/~diego/software/luasocket/tcp.html
function socket_start()
	print("Waiting for connection...")
	local client = sock:accept() -- Accept a new connection
	client:settimeout(5) -- Set timeout to 5 seconds
	print("New connection established")
	return client
end

-- reset_input: Resets all buttons to nil (off)
-- input_dict: The main input dictionary
function reset_input(input_dict)
	for key, _ in pairs(input_dict) do
		input_dict[key] = nil
	end
end

-- execute_input: Sets parameter of buttons to be "down"
-- buttons[]: Strings of each button in relation to input dictionary
function exectute_input(buttons)
	reset_input(input)
	-- for button in buttons do
		-- Doesn't quite support multiple buttons yet
		input[buttons] = true
	-- end
end

-- parse_packet: Reads the "type" field of the JSON packet and calls appropriate functions
-- packet: A JSON string received from the client
function parse_packet(packet)
	packet_table = json.decode(packet)

	-- Input packets...
	if (packet_table["type"] == "input") then
		exectute_input(packet_table["button"])
	end
end

-- socketRunner: Called at a set interval, locks program until input is received by client
-- client: The client object as generated from socket_start()
function socketRunner(client)
	local line, err = client:receive("*l") -- Reading ONLY until a newline
	if not err then
		print("Received data from client: " .. line)
		-- Process the received data as needed
		parse_packet(line)

		-- Example: Send a response back to the client
		client:send("Server received your message: " .. line .. "\n")
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
	select = nil
}

local client = socket_start()

-- Messing with OS. May just make a runfile instead...
-- local command = "dir"
-- local stdout = io.popen(command, "r")

-- if stdout then
-- 	local output = stdout:read("*a")
-- 	print(output)
-- 	stdout:close()
-- end

local framecount = 0

while true do
	framecount = (framecount + 1) % 60 -- Rollover per second
	-- Once a second...
	if (framecount == 30) then
		socketRunner(client)
		joypad.set(1, input) -- Spam a and start
	end
	emu.frameadvance()
end

