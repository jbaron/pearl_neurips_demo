from pearl.api.environment import Environment
from pearl.utils.instantiations.spaces.discrete_action import DiscreteActionSpace
from pearl.api.action_result import ActionResult
import numpy as np
import random

import torch

device = torch.device("cpu")

class RecEnv(Environment):
    def __init__(self, actions, model):
        self.model = model.to(device)
        self.t = 0
        self.T = 20
        self.actions = [[torch.tensor(k) for k in random.sample(actions, 2)] for _ in range(self.T)]
        self.state = torch.zeros((8, 100)).to(device)

    def action_space(self):
        pass

    def reset(self, seed = None):
        self.state = torch.zeros((8, 100))
        self.t = 0
        self.action_space = DiscreteActionSpace(self.actions[self.t])
        return [0.0], self.action_space

    def step(self, action):
        action_rep = self.action_space.actions_batch[action]
        reward = self.model(self.state.unsqueeze(0).to(device), action_rep.to(device)) * 3 # To speed up learning
        true_reward = np.random.binomial(1, reward.item())
        self.state = torch.cat([self.state[1:, :].to(device), action_rep.to(device)], dim=0)

        self.t += 1
        if self.t < self.T:
            self.action_space = DiscreteActionSpace(self.actions[self.t])
        return ActionResult(
            observation = [float(true_reward)],
            reward = float(true_reward),
            terminated = self.t >= self.T,
            truncated = False,
            info = {},
            available_action_space = self.action_space,
        )
