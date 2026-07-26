import numpy as np

def relu(z):
    return np.maximum(0, z)

def relu_grad(z):
    return (z > 0).astype(float)

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def sigmoid_grad(z):
    s = sigmoid(z)
    return s * (1 - s)

def softmax(z):
    z_shifted = z - np.max(z, axis=1, keepdims=True)
    exp_z = np.exp(z_shifted)
    return exp_z / np.sum(exp_z, axis=1, keepdims=True)

_ACTIVATIONS = {
    "relu": (relu, relu_grad),
    "sigmoid": (sigmoid, sigmoid_grad),
}

class NeuralNetworkClassifier:
    def __init__(self, layer_sizes, activation="relu", lr=0.1, seed=0):
        self.layer_sizes = layer_sizes
        self.lr = lr
        self.act, self.act_grad = _ACTIVATIONS[activation]
        rng = np.random.default_rng(seed)

        self.weights, self.biases = [], []
        for n_in, n_out in zip(layer_sizes[:-1], layer_sizes[1:]):
            # He-style initialization scaled for stability across activations
            limit = np.sqrt(2.0 / n_in)
            self.weights.append(rng.normal(0, limit, size=(n_in, n_out)))
            self.biases.append(np.zeros(n_out))

        self.train_loss_history_ = []
        self.train_acc_history_ = []
        self.val_acc_history_ = []

    def _forward(self, X):
        activations = [X]
        pre_activations = []
        a = X
        n_layers = len(self.weights)
        for i, (W, b) in enumerate(zip(self.weights, self.biases)):
            z = a @ W + b
            pre_activations.append(z)
            a = softmax(z) if i == n_layers - 1 else self.act(z)
            activations.append(a)
        return pre_activations, activations

    def predict_proba(self, X):
        _, activations = self._forward(np.asarray(X, dtype=float))
        return activations[-1]

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def _one_hot(self, y, n_classes):
        oh = np.zeros((len(y), n_classes))
        oh[np.arange(len(y)), y] = 1
        return oh

    def _backward(self, pre_activations, activations, y_onehot):
        n = y_onehot.shape[0]
        n_layers = len(self.weights)
        grads_W = [None] * n_layers
        grads_b = [None] * n_layers

        # Output layer: softmax + cross-entropy has the clean gradient (p - y)
        delta = (activations[-1] - y_onehot) / n

        for l in reversed(range(n_layers)):
            grads_W[l] = activations[l].T @ delta
            grads_b[l] = delta.sum(axis=0)
            if l > 0:
                delta = (delta @ self.weights[l].T) * self.act_grad(pre_activations[l - 1])

        return grads_W, grads_b

    def fit(self, X, y, X_val=None, y_val=None, epochs=30, batch_size=64, verbose=False):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        n_classes = self.layer_sizes[-1]
        y_onehot = self._one_hot(y, n_classes)
        n = X.shape[0]
        rng = np.random.default_rng(0)

        for epoch in range(epochs):
            perm = rng.permutation(n)
            X_shuf, y_shuf = X[perm], y_onehot[perm]

            for start in range(0, n, batch_size):
                Xb = X_shuf[start:start + batch_size]
                yb = y_shuf[start:start + batch_size]
                pre_acts, acts = self._forward(Xb)
                grads_W, grads_b = self._backward(pre_acts, acts, yb)
                for l in range(len(self.weights)):
                    self.weights[l] -= self.lr * grads_W[l]
                    self.biases[l] -= self.lr * grads_b[l]

            probs = self.predict_proba(X)
            loss = -np.mean(np.sum(y_onehot * np.log(np.clip(probs, 1e-12, 1)), axis=1))
            acc = np.mean(np.argmax(probs, axis=1) == y)
            self.train_loss_history_.append(loss)
            self.train_acc_history_.append(acc)

            if X_val is not None:
                val_acc = np.mean(self.predict(X_val) == y_val)
                self.val_acc_history_.append(val_acc)

            if verbose:
                msg = f"Epoch {epoch+1}/{epochs}  loss={loss:.4f}  train_acc={acc:.4f}"
                if X_val is not None:
                    msg += f"  val_acc={val_acc:.4f}"
                print(msg)

        return self
