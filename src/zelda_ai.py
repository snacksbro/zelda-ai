import gym
from gym import spaces
import numpy as np

# from main import send_input
import client


class ZeldaBot(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self):
        self.percept = {}
        self.screen_width = 256
        self.screen_height = 240
        self.current_episode = 0
        self.current_step = 0
        self.current_reward = 0

        # We have 4 actions, corresponding to:
        # "move left", "move right", "attack", "crouch"
        self.action_space = spaces.Discrete(4)
        self.player_location = 0
        self.enemy_location = 0
        self.player_is_crouching = False
        self.player_is_attacking = False

    # Get Observation
    def _get_obs(self):
        return self.percept  # Used to be a numpy array here
        # return {"agent": self._agent_location, "target": self._target_location}

    # Get info? I guess obs is just the raw data but info is computing it?
    def _get_info(self):
        return {
            # "distance": np.linalg.norm(
            #     self._agent_location - self._target_location, ord=1
            # )
        }

    # All that really needs to happen here is to send the reset packet
    # Which will load the savestate, restart the server script,
    # and spawn the python client again
    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        print("Attempting reset!")
        super().reset(seed=seed)

        observation = self._get_obs()
        info = self._get_info()
        client.send_reset()

        return observation, info

    def step(self, action):
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        # direction = self._action_to_direction[action]
        # TODO: I should *probably* decouple this and just have main do it
        if action == 0:
            client.send_input("left")
        elif action == 1:
            client.send_input("right")
        elif action == 2:
            client.send_input("down")
        elif action == 3:
            client.send_input("B")

        # Episode endings
        # Death, win

        terminated = (
            True if int(self.percept["player_health"]) <= 0 else False
        )  # client.player_is_dead()
        print("Terminated status:", terminated)
        if not terminated:
            reward = 1.0
        else:
            reward = 0.0
            self.reset()

        observation = self._get_obs()  # Should read from percept packet
        # info = self._get_info()

        # if self.render_mode == "human":
        #     self._render_frame()
        self.current_reward = reward  # May refactor this later

        return observation, reward, terminated, {}  # False, info

    def render(self):
        pass

    def _render_frame(self):
        pass

    def close(self):
        pass
