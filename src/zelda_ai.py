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

        # We have 4 actions, corresponding to "move left", "move right", "attack", "crouch"
        self.action_space = spaces.Discrete(4)
        self.player_location = 0
        self.enemy_location = 0
        self.player_is_crouching = False
        self.player_is_attacking = False

        # self.size = size  # The size of the square grid
        # self.window_size = 512  # The size of the PyGame window

        # # Observations are dictionaries with the agent's and the target's location.
        # # Each location is encoded as an element of {0, ..., `size`}^2, i.e. MultiDiscrete([size, size]).
        # self.observation_space = spaces.Dict(
        #     {
        #         "agent": spaces.Box(0, size - 1, shape=(2,), dtype=int),
        #         "target": spaces.Box(0, size - 1, shape=(2,), dtype=int),
        #     }
        # )



        # """
        # The following dictionary maps abstract actions from `self.action_space` to
        # the direction we will walk in if that action is taken.
        # I.e. 0 corresponds to "right", 1 to "up" etc.
        # """
        # TODO: This v
        # self._action_to_direction = {
        #     0: np.array([1, 0]),
        #     1: np.array([0, 1]),
        #     2: np.array([-1, 0]),
        #     3: np.array([0, -1]),
        # }

        # assert render_mode is None or render_mode in self.metadata["render_modes"]
        # self.render_mode = render_mode

        # """
        # If human-rendering is used, `self.window` will be a reference
        # to the window that we draw to. `self.clock` will be a clock that is used
        # to ensure that the environment is rendered at the correct framerate in
        # human-mode. They will remain `None` until human-mode is used for the
        # first time.
        # """
        # self.window = None
        # self.clock = None

    # Get Observation
    def _get_obs(self):
        return self.percept # Used to be a numpy array here
        # return {"agent": self._agent_location, "target": self._target_location}

    # Get info? I guess obs is just the raw data but info is computing it?
    def _get_info(self):
        return {
            "distance": np.linalg.norm(
                self._agent_location - self._target_location, ord=1
            )
        }

    # All that really needs to happen here is to send the reset packet
    # Which will load the savestate, restart the server script, and spawn the python client again
    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        # Choose the agent's location uniformly at random
        self._agent_location = self.np_random.integers(0, self.size, size=2, dtype=int)

        # We will sample the target's location randomly until it does not coincide with the agent's location
        self._target_location = self._agent_location
        while np.array_equal(self._target_location, self._agent_location):
            self._target_location = self.np_random.integers(
                0, self.size, size=2, dtype=int
            )

        observation = self._get_obs()
        info = self._get_info()

        # Wat
        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        # Map the action (element of {0,1,2,3}) to the direction we walk in
        # direction = self._action_to_direction[action]
        if (action == 0):
            client.send_input("left")
        elif (action == 1):
            client.send_input("right")
        elif (action == 2):
            client.send_input("down")
        elif (action == 3):
            client.send_input("B")

        # We use `np.clip` to make sure we don't leave the grid
        # self._agent_location = np.clip(
        #     self._agent_location + direction, 0, self.size - 1
        # )
        # An episode is done iff the agent has reached the target

        # Episode endings
        # Death, win

        terminated = True if self.percept["player_health"] <= 0 else False #client.player_is_dead()
        if not terminated:
            reward = 1.0
        else:
            reward = 0.0

        observation = self._get_obs() # Should read from percept packet
        # info = self._get_info()

        # if self.render_mode == "human":
        #     self._render_frame()

        return observation, reward, terminated, {} #False, info

    def render(self):
        # if self.render_mode == "rgb_array":
        #     return self._render_frame()
        pass

    def _render_frame(self):
        pass

    def close(self):
        pass
        # if self.window is not None:
        #     pygame.display.quit()
        #     pygame.quit()

