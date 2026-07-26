"""
Demo: from-scratch MLP trained on MNIST digit classification.
Downloads MNIST via sklearn's fetch_openml (requires internet on first run;
falls back to sklearn's smaller built-in digits dataset if unavailable).
Run with:  python demo.py
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from neural_net import NeuralNetworkClassifier

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_data():
    try:
        from sklearn.datasets import fetch_openml
        mnist = fetch_openml("mnist_784", version=1, as_frame=False)
        X = mnist.data.astype(float) / 255.0
        y = mnist.target.astype(int)
        print("Loaded full MNIST (70,000 images, 784 features).")
    except Exception as e:
        print(f"Could not fetch MNIST ({e}); falling back to sklearn digits dataset.")
        from sklearn.datasets import load_digits
        digits = load_digits()
        X = digits.data / 16.0
        y = digits.target
    return X, y


def main():
    X, y = load_data()
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(X))
    X, y = X[idx], y[idx]

    n_train = int(0.8 * len(X))
    X_train, y_train = X[:n_train], y[:n_train]
    X_val, y_val = X[n_train:], y[n_train:]

    n_features = X.shape[1]
    n_classes = len(np.unique(y))

    model = NeuralNetworkClassifier(
        layer_sizes=[n_features, 128, 64, n_classes],
        activation="relu", lr=0.1, seed=0,
    )
    model.fit(X_train, y_train, X_val, y_val, epochs=30, batch_size=64, verbose=True)

    final_val_acc = model.val_acc_history_[-1]
    print(f"\nFinal validation accuracy: {final_val_acc:.4f}")

    plt.figure(figsize=(6.5, 4.5))
    plt.plot(model.train_acc_history_, label="Train accuracy")
    plt.plot(model.val_acc_history_, label="Validation accuracy")
    plt.xlabel("Epoch"); plt.ylabel("Accuracy")
    plt.title("From-scratch MLP on MNIST")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "nn_training_curve.png"), dpi=130)
    plt.close()

    # A grid of sample predictions
    sample_idx = rng.choice(len(X_val), 12, replace=False)
    preds = model.predict(X_val[sample_idx])
    img_dim = int(np.sqrt(n_features))
    fig, axes = plt.subplots(2, 6, figsize=(11, 4))
    for ax, i, p in zip(axes.flatten(), sample_idx, preds):
        ax.imshow(X_val[i].reshape(img_dim, img_dim), cmap="gray")
        true_label = y_val[list(sample_idx).index(i)] if False else y_val[np.where(sample_idx == i)[0][0]]
        ax.set_title(f"pred={p}, true={true_label}", fontsize=9)
        ax.axis("off")
    plt.suptitle("Sample predictions on validation set")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "nn_sample_predictions.png"), dpi=130)
    plt.close()


if __name__ == "__main__":
    main()
