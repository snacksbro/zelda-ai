emu.speedmode("normal") -- Set emulator speed

while true do
	--up, down, left, right, A, B, start, select
	joypad.write(1, {nil, nil, nil, nil, "invert", nil, "invert", nil}) -- Spam a and start
	emu.frameadvance()
end

