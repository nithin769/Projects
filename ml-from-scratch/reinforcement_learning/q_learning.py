import numpy as np

class MDPEnvironment:
    def __init__(self, P: np.ndarray, R: np.ndarray, seed: int = 0):
        self.P = np.asarray(P, dtype=float)
        self.R = np.asarray(R, dtype=float)
        self.n_states = self.P.shape[0]
        self.n_actions = self.P.shape[1]
        self.rng = np.random.default_rng(seed)
        self.state = 0

    def reset(self, state: int = 0) -> int:
        self.state = state
        return self.state

    def step(self, action: int):
        probs = self.P[self.state, action]
        next_state = self.rng.choice(self.n_states, p=probs)
        reward = (self.R[self.state, action, next_state]
                  if self.R.ndim == 3 else self.R[self.state, action])
        self.state = next_state
        return next_state, reward

class QLearningAgent:
    def __init__(self, n_states, n_actions, alpha=0.1, gamma=0.9, epsilon=0.1, seed=0):
        self.Q = np.zeros((n_states, n_actions))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.rng = np.random.default_rng(seed)
        self.n_actions = n_actions

    def select_action(self, state: int) -> int:
        if self.rng.random() < self.epsilon:
            return self.rng.integers(self.n_actions)
        return int(np.argmax(self.Q[state]))

    def update(self, state, action, reward, next_state):
        best_next = np.max(self.Q[next_state])
        td_target = reward + self.gamma * best_next
        td_error = td_target - self.Q[state, action]
        self.Q[state, action] += self.alpha * td_error

    def greedy_policy(self) -> np.ndarray:
        return np.argmax(self.Q, axis=1)

    def train(self, env: MDPEnvironment, n_iterations=20000, start_state=0, track_history=True):
        state = env.reset(start_state)
        history = [] if track_history else None

        for _ in range(n_iterations):
            action = self.select_action(state)
            next_state, reward = env.step(action)
            self.update(state, action, reward, next_state)
            if track_history:
                history.append(self.Q.max(axis=1).copy())
            state = next_state

        return np.array(history) if track_history else None
