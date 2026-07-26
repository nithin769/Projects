import numpy as np

def accuracy(y_true, y_pred) -> float:
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))

def add_bias(X: np.ndarray) -> np.ndarray:
    return np.hstack([np.ones((X.shape[0], 1)), X])

class LeastSquaresClassifier:
    """Binary classifier fit by treating {-1, +1} labels as regression targets."""

    def __init__(self):
        self.w = None

    def fit(self, X, y) -> "LeastSquaresClassifier":
        Xb = add_bias(np.asarray(X, dtype=float))
        y = np.asarray(y, dtype=float)
        self.w = np.linalg.lstsq(Xb, y, rcond=None)[0]
        return self

    def decision_function(self, X):
        return add_bias(np.asarray(X, dtype=float)) @ self.w

    def predict(self, X):
        return np.where(self.decision_function(X) >= 0, 1, -1)

class FisherDiscriminant:
    def __init__(self):
        self.w = None
        self.threshold = None

    def fit(self, X, y) -> "FisherDiscriminant":
        X, y = np.asarray(X, dtype=float), np.asarray(y)
        classes = np.unique(y)
        assert len(classes) == 2, "FisherDiscriminant supports binary classification"
        X0, X1 = X[y == classes[0]], X[y == classes[1]]
        mu0, mu1 = X0.mean(axis=0), X1.mean(axis=0)

        Sw = (X0 - mu0).T @ (X0 - mu0) + (X1 - mu1).T @ (X1 - mu1)
        self.w = np.linalg.solve(Sw, mu1 - mu0)
        self.classes_ = classes
        # Threshold: midpoint of projected class means
        self.threshold = 0.5 * (mu0 @ self.w + mu1 @ self.w)
        return self

    def project(self, X):
        return np.asarray(X, dtype=float) @ self.w

    def predict(self, X):
        proj = self.project(X)
        return np.where(proj >= self.threshold, self.classes_[1], self.classes_[0])


class Perceptron:
    def __init__(self, lr: float = 1.0, max_epochs: int = 1000):
        self.lr = lr
        self.max_epochs = max_epochs
        self.w = None

    def fit(self, X, y) -> "Perceptron":
        Xb = add_bias(np.asarray(X, dtype=float))
        y = np.asarray(y, dtype=float)
        w = np.zeros(Xb.shape[1])
        best_w, best_acc = w.copy(), 0.0

        for _ in range(self.max_epochs):
            misclassified = 0
            for xi, yi in zip(Xb, y):
                if yi * (xi @ w) <= 0:
                    w += self.lr * yi * xi
                    misclassified += 1
            acc = np.mean(y * (Xb @ w) > 0)
            if acc > best_acc:
                best_acc, best_w = acc, w.copy()
            if misclassified == 0:
                break

        self.w = best_w
        return self

    def predict(self, X):
        Xb = add_bias(np.asarray(X, dtype=float))
        return np.where(Xb @ self.w >= 0, 1, -1)

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

class LogisticRegressionIRLS:
    def __init__(self, max_iter: int = 50, tol: float = 1e-6, reg_lambda: float = 1e-6):
        self.max_iter = max_iter
        self.tol = tol
        self.reg_lambda = reg_lambda
        self.w = None

    def fit(self, X, y) -> "LogisticRegressionIRLS":
        Xb = add_bias(np.asarray(X, dtype=float))
        y = np.asarray(y, dtype=float)
        n_features = Xb.shape[1]
        w = np.zeros(n_features)

        for _ in range(self.max_iter):
            z = Xb @ w
            p = sigmoid(z)
            R = p * (1 - p)
            R = np.clip(R, 1e-6, None)
            grad = Xb.T @ (p - y) + self.reg_lambda * w
            H = Xb.T @ (Xb * R[:, None]) + self.reg_lambda * np.eye(n_features)
            step = np.linalg.solve(H, grad)
            w_new = w - step
            if np.linalg.norm(w_new - w) < self.tol:
                w = w_new
                break
            w = w_new
        self.w = w
        return self

    def predict_proba(self, X):
        Xb = add_bias(np.asarray(X, dtype=float))
        return sigmoid(Xb @ self.w)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

def _gaussian_pdf(X, mean, cov):
    d = X.shape[1]
    diff = X - mean
    cov_inv = np.linalg.inv(cov)
    exponent = -0.5 * np.sum(diff @ cov_inv * diff, axis=1)
    norm_const = 1.0 / np.sqrt((2 * np.pi) ** d * np.linalg.det(cov))
    return norm_const * np.exp(exponent)


class GaussianMixtureEM:
    def __init__(self, n_components: int = 2, max_iter: int = 100, tol: float = 1e-4, seed: int = 0):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.seed = seed

    def fit(self, X) -> "GaussianMixtureEM":
        X = np.asarray(X, dtype=float)
        n, d = X.shape
        k = self.n_components
        rng = np.random.default_rng(self.seed)

        # Initialize with random data points as means
        idx = rng.choice(n, k, replace=False)
        self.means_ = X[idx].copy()
        self.covs_ = [np.cov(X.T) + 1e-6 * np.eye(d) for _ in range(k)]
        self.weights_ = np.full(k, 1.0 / k)

        self.log_likelihood_history_ = []
        prev_ll = -np.inf

        for _ in range(self.max_iter):
            # E-step: responsibilities
            resp = np.zeros((n, k))
            for j in range(k):
                resp[:, j] = self.weights_[j] * _gaussian_pdf(X, self.means_[j], self.covs_[j])
            total = resp.sum(axis=1, keepdims=True)
            total[total == 0] = 1e-12
            resp /= total

            ll = np.sum(np.log(np.clip(total.flatten(), 1e-12, None)))
            self.log_likelihood_history_.append(ll)

            # M-step
            Nk = resp.sum(axis=0)
            for j in range(k):
                self.means_[j] = (resp[:, j] @ X) / Nk[j]
                diff = X - self.means_[j]
                self.covs_[j] = (resp[:, j][:, None] * diff).T @ diff / Nk[j]
                self.covs_[j] += 1e-6 * np.eye(d)
            self.weights_ = Nk / n

            if abs(ll - prev_ll) < self.tol:
                break
            prev_ll = ll

        self.resp_ = resp
        return self

    def predict(self, X=None):
        return np.argmax(self.resp_, axis=1)
