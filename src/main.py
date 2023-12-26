import client
from zelda_ai import ZeldaBot  # I should really do this better

client.current_time, client.max_time = client.update_time()
env = ZeldaBot()

# Testing, send a B button every 5 seconds
while True:
    client.current_time = (client.current_time + 1) % client.max_time
    if client.current_time == 0:
        # bitmap = recieve_bitmap()
        # positions = recieve_positions()
        env.percept = client.recieve_percept()
        action = env.action_space.sample()
        obs, reward, done, _ = env.step(action)
        client.update_model_info(
            env.current_step, env.current_episode, env.current_reward
        )
        # send_input("B")
        # time.sleep(5)

# finally:
# 	client_sock.close()
# 	print("Connection terminated.")
