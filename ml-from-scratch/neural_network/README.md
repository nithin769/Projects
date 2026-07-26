# Neural Networks

A fully-connected multi-layer perceptron with manual forward propagation,
backpropagation, and mini-batch gradient descent — no autodiff, no framework.

## Files
- `neural_net.py` — `NeuralNetworkClassifier` (ReLU/sigmoid hidden layers, softmax + cross-entropy output)
- `demo.py` — trains on MNIST digit classification (784 → 128 → 64 → 10)

## Run
```bash
python demo.py
```
Uses `sklearn.datasets.fetch_openml` to pull full MNIST (70,000 images) if
internet access is available; otherwise falls back automatically to
sklearn's bundled `digits` dataset (1,797 images, 8×8) so the demo still
runs fully offline.

## Key results

On full MNIST (784 → 128 → 64 → 10, ReLU, lr=0.1, batch size 64, 30 epochs):

- Training accuracy jumps from ~31% to ~87% within the first 5 epochs — the
  network picks up the core digit patterns quickly at this learning rate.
- Validation accuracy plateaus in the high-90s while training accuracy keeps
  climbing toward ~99% in later epochs — a visible, textbook sign of the
  network starting to overfit past that point, useful for reasoning about
  early stopping or regularization.

(On the offline fallback `digits` dataset the same architecture reaches
~98% validation accuracy, since the task is smaller and simpler.)

![Training curve](../results/nn_training_curve.png)
![Sample predictions](../results/nn_sample_predictions.png)
