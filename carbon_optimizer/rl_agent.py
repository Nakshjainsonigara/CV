import numpy as np

class RLAgent:
    def __init__(self, num_actions):
        self.q_table = {}  # Action -> value mapping
        self.learning_rate = 0.1
        
    def update(self, action, reward):
        # Simple Q-learning update
        if action not in self.q_table:
            self.q_table[action] = 0
            
        self.q_table[action] = (1 - self.learning_rate) * self.q_table[action] + \
                              self.learning_rate * reward 