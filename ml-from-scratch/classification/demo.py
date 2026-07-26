"""
Demo: comparing least squares, Fisher's discriminant, perceptron, logistic
regression (robustness to outliers), and GMM-EM clustering.
Run with:  python demo.py
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from classifiers import (
    LeastSquaresClassifier, FisherDiscriminant, Perceptron,
    LogisticRegressionIRLS, GaussianMixtureEM, accuracy,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def two_gaussian_classes(n=200, seed=0):
    rng = np.random.default_rng(seed)
    mean1, cov1 = [1, 1], [[0.6, 0], [0, 0.6]]
    mean2, cov2 = [-1, -1], [[0.6, 0], [0, 0.6]]
    X1 = rng.multivariate_normal(mean1, cov1, n)
    X2 = rng.multivariate_normal(mean2, cov2, n)
    X = np.vstack([X1, X2])
    y_pm1 = np.hstack([np.ones(n), -np.ones(n)])
    y_01 = np.hstack([np.ones(n), np.zeros(n)])
    idx = rng.permutation(len(X))
    return X[idx], y_pm1[idx], y_01[idx]


def add_outliers(X, y_pm1, n_outliers=15, seed=1):
    rng = np.random.default_rng(seed)
    outliers = rng.normal(loc=[5, 5], scale=0.4, size=(n_outliers, 2))
    X_out = np.vstack([X, outliers])
    y_out = np.hstack([y_pm1, -np.ones(n_outliers)])  # far into class -1 territory
    return X_out, y_out


def robustness_to_outliers():
    X, y_pm1, _ = two_gaussian_classes()
    X_train, y_train = X[:300], y_pm1[:300]
    X_test, y_test = X[300:], y_pm1[300:]

    ls_clean = LeastSquaresClassifier().fit(X_train, y_train)
    perc_clean = Perceptron(lr=0.1, max_epochs=200).fit(X_train, y_train)
    acc_ls_clean = accuracy(y_test, ls_clean.predict(X_test))
    acc_perc_clean = accuracy(y_test, perc_clean.predict(X_test))

    X_train_out, y_train_out = add_outliers(X_train, y_train)
    ls_out = LeastSquaresClassifier().fit(X_train_out, y_train_out)
    perc_out = Perceptron(lr=0.1, max_epochs=200).fit(X_train_out, y_train_out)
    acc_ls_out = accuracy(y_test, ls_out.predict(X_test))
    acc_perc_out = accuracy(y_test, perc_out.predict(X_test))

    print(f"Least squares:  clean={acc_ls_clean:.3f}  with outliers={acc_ls_out:.3f}")
    print(f"Perceptron:     clean={acc_perc_clean:.3f}  with outliers={acc_perc_out:.3f}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, clf, name in [(axes[0], ls_out, "Least Squares"), (axes[1], perc_out, "Perceptron")]:
        xx, yy = np.meshgrid(np.linspace(-4, 8, 200), np.linspace(-4, 8, 200))
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
        ax.contourf(xx, yy, Z, alpha=0.3, cmap="coolwarm")
        ax.scatter(X_train_out[:, 0], X_train_out[:, 1], c=y_train_out, cmap="coolwarm",
                   edgecolor="k", s=15)
        ax.set_title(f"{name} (with outliers)")
        ax.set_xlim(-4, 8); ax.set_ylim(-4, 8)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "classification_outlier_robustness.png"), dpi=130)
    plt.close()


def fisher_projection():
    X, y_pm1, _ = two_gaussian_classes()
    fisher = FisherDiscriminant().fit(X, y_pm1)
    proj = fisher.project(X)

    plt.figure(figsize=(6, 4))
    plt.hist(proj[y_pm1 == 1], bins=25, alpha=0.6, label="Class +1")
    plt.hist(proj[y_pm1 == -1], bins=25, alpha=0.6, label="Class -1")
    plt.axvline(fisher.threshold, color="k", ls="--", label="Decision threshold")
    plt.xlabel("Projection onto Fisher direction"); plt.ylabel("Count")
    plt.title("Fisher's Discriminant: 1D class separation")
    plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "classification_fisher_projection.png"), dpi=130)
    plt.close()
    acc = accuracy(y_pm1, fisher.predict(X))
    print(f"Fisher discriminant training accuracy: {acc:.3f}")


def gmm_em_demo():
    rng = np.random.default_rng(0)
    means = [[0, 0], [4, 4], [0, 5]]
    covs = [[[0.5, 0.1], [0.1, 0.5]]] * 3
    X = np.vstack([rng.multivariate_normal(m, c, 150) for m, c in zip(means, covs)])

    gmm = GaussianMixtureEM(n_components=3, seed=0).fit(X)
    labels = gmm.predict()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].scatter(X[:, 0], X[:, 1], c=labels, cmap="viridis", s=12)
    axes[0].scatter(gmm.means_[:, 0], gmm.means_[:, 1], c="red", marker="x", s=100, label="Fitted means")
    axes[0].set_title("GMM-EM cluster assignments")
    axes[0].legend()

    axes[1].plot(gmm.log_likelihood_history_, marker="o", ms=3)
    axes[1].set_xlabel("EM iteration"); axes[1].set_ylabel("Log-likelihood")
    axes[1].set_title("Monotonic log-likelihood increase")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "classification_gmm_em.png"), dpi=130)
    plt.close()
    print(f"GMM-EM converged in {len(gmm.log_likelihood_history_)} iterations")


def logistic_regression_demo():
    X, _, y01 = two_gaussian_classes()
    X_train, y_train = X[:300], y01[:300]
    X_test, y_test = X[300:], y01[300:]
    clf = LogisticRegressionIRLS().fit(X_train, y_train)
    acc = accuracy(y_test, clf.predict(X_test))
    print(f"Logistic regression (IRLS) test accuracy: {acc:.3f}")


if __name__ == "__main__":
    robustness_to_outliers()
    fisher_projection()
    logistic_regression_demo()
    gmm_em_demo()
