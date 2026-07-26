# Q-Learning

A model-free tabular Q-learning agent, trained purely from sampled
transitions of an (otherwise unknown) Markov Decision Process, with an
epsilon-greedy behavior policy.

## Files
- `q_learning.py` — `MDPEnvironment` (transition/reward simulator), `QLearningAgent`
- `demo.py` — 3-state / 2-action toy MDP, convergence & exploration-rate experiments

## Run
```bash
python demo.py
```

## Key results

On a 3-state, 2-action toy MDP (states differ in how risky/rewarding their
actions are):

- `max_a Q(s,a)` fluctuates early due to epsilon-greedy exploration, then
  stabilizes as the agent's estimate of the environment sharpens — Q-learning
  converges to a fixed greedy policy without ever seeing the transition
  probabilities directly.
- **Exploration rate matters**: very low epsilon (0.01) converges slowly and
  can get stuck favoring a suboptimal action if early samples are unlucky;
  high epsilon (0.5) converges to the right values faster in expectation but
  with much noisier trajectories along the way.

![Convergence](../results/qlearning_convergence.png)
![Epsilon effect](../results/qlearning_epsilon_effect.png)
