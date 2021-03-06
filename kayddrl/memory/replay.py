import random
from collections import namedtuple

import numpy as np

from kayddrl.configs.default import default
from kayddrl.memory.base import Memory
from kayddrl.utils.logging import logger
from kayddrl.utils.utils import tensorify, describe


class ReplayBuffer(Memory):
    r"""
    Stores agent experiences and samples from them for agent training

    An experience consists of
        - state: representation of a state
        - action: action taken
        - reward: scalar value
        - next state: representation of next state (should be same as state)
        - done: 0 / 1 representing if the current state is the last in an episode

    The memory has a size of N. When capacity is reached, the oldest experience
    is deleted to make space for the latest experience.
        - This is implemented as a circular buffer so that inserting experiences are O(1)
        - Each element of an experience is stored as a separate array of size N * element dim

    When a batch of experiences is requested, K experiences are sampled according to a random uniform distribution.

    config example:
    "memory": {
        "name": "ReplayBuffer",
        "batch_size": 32,
        "buffer_size": 10000,
        "device": cpu
    }
    """

    def __init__(self, config=default()):
        super().__init__(config)
        self.experience = namedtuple("Experience", field_names=["state", "action", "reward", "next_state", "done"])
        logger.info(describe(self))
        self.clear()

    def update(self, state, action, reward, next_state, done):
        e = self.experience(state, action, reward, next_state, done)
        self.memory.append(e)

    def sample(self):
        sample_size = self.batch_size if self.batch_size <= len(self) else len(self)
        experiences = random.sample(self.memory, k=sample_size)

        states = tensorify(np.array([e.state for e in experiences if e is not None]), self.device)
        actions = tensorify(np.array([e.action for e in experiences if e is not None]), self.device)
        rewards = tensorify(np.array([e.reward for e in experiences if e is not None]), self.device)
        next_states = tensorify(np.array([e.next_state for e in experiences if e is not None]), self.device)
        dones = tensorify(np.array([e.done for e in experiences if e is not None]).astype(np.uint8), self.device)

        return (states, actions, rewards, next_states, dones)


rb = ReplayBuffer()
