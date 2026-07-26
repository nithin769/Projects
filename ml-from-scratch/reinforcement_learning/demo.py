"""
Demo: Q-learning on a 3-state, 2-action MDP (a toy "phone battery management"
style problem). Shows convergence of max_a Q(s,a) and the effect of epsilon.
Run with:  python demo.py
"""
import os
import numpy as np
import matplotlib.pyplot as plt

from q_learning import MDPEnvironment, QLearningAgent

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def build_toy_mdp():
    P = np.array([
        # state 0
        [[0.7, 0.2, 0.1], [0.3, 0.3, 0.4]],
        # state 1
        [[0.1, 0.8, 0.1], [0.2, 0.2, 0.6]],
        # state 2
        [[0.1, 0.1, 0.8], [0.6, 0.3, 0.1]],
    ])
    R = np.array([
        [1.0, 0.5],
        [1.0, 2.0],
        [1.0, -1.0],
    ])
    R = np.repeat(R[:, :, None], 3, axis=2)
    return P, R

def run_training(epsilon, n_iterations=20000, seed=0):
    P, R = build_toy_mdp()
    env = MDPEnvironment(P, R, seed=seed)
    agent = QLearningAgent(n_states=3, n_actions=2, alpha=0.1, gamma=0.9, epsilon=epsilon, seed=seed)
    history = agent.train(env, n_iterations=n_iterations)
    return agent, history

def convergence_plot():
    agent, history = run_training(epsilon=0.1)
    print("Learned greedy policy:", agent.greedy_policy())
    print("Final Q-table:\n", np.round(agent.Q, 2))

    plt.figure(figsize=(6.5, 4.5))
    for s in range(3):
        plt.plot(history[:, s], label=f"State {s+1}")
    plt.xlabel("Iteration"); plt.ylabel("max_a Q(s,a)")
    plt.title("Q-learning convergence (epsilon=0.1)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "qlearning_convergence.png"), dpi=130)
    plt.close()

def epsilon_comparison():
    plt.figure(figsize=(6.5, 4.5))
    for eps in [0.01, 0.1, 0.5]:
        _, history = run_training(epsilon=eps, n_iterations=15000)
        plt.plot(history[:, 2], label=f"epsilon={eps}")
    plt.xlabel("Iteration"); plt.ylabel("max_a Q(state 3, a)")
    plt.title("Effect of exploration rate epsilon on convergence")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "qlearning_epsilon_effect.png"), dpi=130)
    plt.close()

if __name__ == "__main__":
    convergence_plot()
    epsilon_comparison()
