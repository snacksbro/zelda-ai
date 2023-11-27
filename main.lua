local socket = require("socket.core")
print("socket working?")
-- TODO: Investigate why running this crashes since installing it (correctly?). There may be other example scripts using it, first step is to REPL test
local server, ip, port -- Scoping
local _PORT = 8881

sock = socket.tcp() -- "Master" object created
-- Use a random port offered by the OS, or a predetermined?
if not _PORT then
	server = assert(sock:bind("*", 0)) -- Binding master to port
else
	server = assert(sock:bind("*", _PORT)) -- Binding master to port
end

if (server) then
	ip, port = sock:getsockname() -- Pulling out the ip/port listening
	print("Port opened!\nWaiting on " .. ip .. ":" .. port)
	sock:listen(-1) -- -1 means it can accept infinite clients. Now this is a "server" object
else
	print("Error occured attempting to bind to port")
end

-- print(server)
-- local ip, port = server:getsockname()

function socketRunner()
	print("Waiting for connection...")
	local client = sock:accept() -- Accept a new connection
	print("New connection established")

	local line, err = client:receive()
		if not err then
			print("Received data from client: " .. line)
			-- Process the received data as needed

			-- Example: Send a response back to the client
			client:send("Server received your message: " .. line .. "\n")
		end

	client:close() -- Close the client connection
end

-- while true do
-- end

emu.speedmode("normal") -- Set emulator speed

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
	framecount = (framecount + 1) % 60
	--up, down, left, right, A, B, start, select
	--joypad.set(1, {nil, nil, nil, nil, true, nil, "invert", nil}) -- Spam a and start
	if (framecount >= 30) then
		joypad.set(1, input) -- Spam a and start
	end
	socketRunner()
	emu.frameadvance()
end


