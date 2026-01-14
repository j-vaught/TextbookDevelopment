"""
Kalman Filter Implementations for Radar Tracking

Five filter variants:
1. Alpha-Beta Filter - Simple fixed-gain tracker
2. Standard Kalman Filter - Linear KF with constant velocity model
3. Extended Kalman Filter - Handles polar radar measurements
4. Unscented Kalman Filter - Sigma-point approach for nonlinear systems
5. IMM Filter - Interacting Multiple Model for maneuvering targets
"""

import numpy as np
from abc import ABC, abstractmethod


class BaseTracker(ABC):
    """Base class for all trackers."""

    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.state = None  # [x, vx, y, vy]
        self.initialized = False
        self.track_history = []  # List of (x, y) positions

    @abstractmethod
    def predict(self, dt: float):
        """Predict state forward by dt seconds."""
        pass

    @abstractmethod
    def update(self, z: np.ndarray):
        """Update state with measurement z = [x, y]."""
        pass

    def get_position(self):
        """Return current estimated position (x, y)."""
        if self.state is None:
            return None
        return self.state[0], self.state[2]

    def initialize(self, x: float, y: float):
        """Initialize tracker at position."""
        self.state = np.array([x, 0.0, y, 0.0])
        self.initialized = True
        self.track_history = [(x, y)]


class AlphaBetaFilter(BaseTracker):
    """Simple fixed-gain alpha-beta filter."""

    def __init__(self, alpha: float = 0.5, beta: float = 0.1):
        super().__init__("Alpha-Beta", "#FF6B6B")  # Red
        self.alpha = alpha
        self.beta = beta

    def predict(self, dt: float):
        if not self.initialized:
            return
        # Simple constant velocity prediction
        self.state[0] += self.state[1] * dt  # x += vx * dt
        self.state[2] += self.state[3] * dt  # y += vy * dt

    def update(self, z: np.ndarray):
        if not self.initialized:
            self.initialize(z[0], z[1])
            return

        # Residuals
        rx = z[0] - self.state[0]
        ry = z[1] - self.state[2]

        # Update position
        self.state[0] += self.alpha * rx
        self.state[2] += self.alpha * ry

        # Update velocity (assume dt=1 for simplicity)
        self.state[1] += self.beta * rx
        self.state[3] += self.beta * ry

        self.track_history.append((self.state[0], self.state[2]))


class KalmanFilter(BaseTracker):
    """Standard linear Kalman filter with constant velocity model."""

    def __init__(self, process_noise: float = 1.0, measurement_noise: float = 10.0):
        super().__init__("Kalman Filter", "#4ECDC4")  # Teal
        self.Q_scale = process_noise
        self.R = np.eye(2) * measurement_noise
        self.P = np.eye(4) * 100  # Initial covariance
        self.H = np.array([[1, 0, 0, 0],
                          [0, 0, 1, 0]])  # Measurement matrix

    def _get_F(self, dt: float):
        """State transition matrix."""
        return np.array([[1, dt, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, dt],
                        [0, 0, 0, 1]])

    def _get_Q(self, dt: float):
        """Process noise matrix."""
        q = self.Q_scale
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt
        return np.array([[dt4/4, dt3/2, 0, 0],
                        [dt3/2, dt2, 0, 0],
                        [0, 0, dt4/4, dt3/2],
                        [0, 0, dt3/2, dt2]]) * q

    def predict(self, dt: float):
        if not self.initialized:
            return
        F = self._get_F(dt)
        Q = self._get_Q(dt)
        self.state = F @ self.state
        self.P = F @ self.P @ F.T + Q

    def update(self, z: np.ndarray):
        if not self.initialized:
            self.initialize(z[0], z[1])
            self.P = np.eye(4) * 100
            return

        # Kalman gain
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        # Update
        y = z - self.H @ self.state
        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

        self.track_history.append((self.state[0], self.state[2]))


class ExtendedKalmanFilter(BaseTracker):
    """Extended Kalman filter for polar radar measurements."""

    def __init__(self, process_noise: float = 1.0, range_noise: float = 5.0, bearing_noise: float = 0.02):
        super().__init__("EKF", "#45B7D1")  # Blue
        self.Q_scale = process_noise
        self.range_noise = range_noise
        self.bearing_noise = bearing_noise
        self.P = np.eye(4) * 100

    def _get_F(self, dt: float):
        return np.array([[1, dt, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, dt],
                        [0, 0, 0, 1]])

    def _get_Q(self, dt: float):
        q = self.Q_scale
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt
        return np.array([[dt4/4, dt3/2, 0, 0],
                        [dt3/2, dt2, 0, 0],
                        [0, 0, dt4/4, dt3/2],
                        [0, 0, dt3/2, dt2]]) * q

    def _h(self, state):
        """Measurement function: state -> [range, bearing]."""
        x, vx, y, vy = state
        r = np.sqrt(x*x + y*y)
        theta = np.arctan2(y, x)
        return np.array([r, theta])

    def _H_jacobian(self, state):
        """Jacobian of measurement function."""
        x, vx, y, vy = state
        r = np.sqrt(x*x + y*y)
        r2 = r * r
        if r < 1e-6:
            r = 1e-6
            r2 = r * r
        return np.array([[x/r, 0, y/r, 0],
                        [-y/r2, 0, x/r2, 0]])

    def predict(self, dt: float):
        if not self.initialized:
            return
        F = self._get_F(dt)
        Q = self._get_Q(dt)
        self.state = F @ self.state
        self.P = F @ self.P @ F.T + Q

    def update(self, z: np.ndarray):
        """z is in Cartesian [x, y], we convert to polar internally."""
        if not self.initialized:
            self.initialize(z[0], z[1])
            self.P = np.eye(4) * 100
            return

        # Convert measurement to polar
        z_polar = np.array([np.sqrt(z[0]**2 + z[1]**2),
                           np.arctan2(z[1], z[0])])

        R = np.diag([self.range_noise**2, self.bearing_noise**2])
        H = self._H_jacobian(self.state)

        # Predicted measurement
        z_pred = self._h(self.state)

        # Innovation with angle wrapping
        y = z_polar - z_pred
        y[1] = np.arctan2(np.sin(y[1]), np.cos(y[1]))  # Wrap angle

        # Kalman gain
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update
        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ H) @ self.P

        self.track_history.append((self.state[0], self.state[2]))


class UnscentedKalmanFilter(BaseTracker):
    """Unscented Kalman filter using sigma points."""

    def __init__(self, process_noise: float = 1.0, measurement_noise: float = 10.0):
        super().__init__("UKF", "#96CEB4")  # Green
        self.Q_scale = process_noise
        self.R = np.eye(2) * measurement_noise
        self.P = np.eye(4) * 100

        # UKF parameters - use more stable values
        self.n = 4  # State dimension
        self.alpha = 0.5  # Larger alpha for better stability
        self.beta = 2
        self.kappa = 3 - self.n  # Common choice
        self.lambda_ = self.alpha**2 * (self.n + self.kappa) - self.n

        # Weights
        self.Wm = np.zeros(2 * self.n + 1)
        self.Wc = np.zeros(2 * self.n + 1)
        self.Wm[0] = self.lambda_ / (self.n + self.lambda_)
        self.Wc[0] = self.Wm[0] + (1 - self.alpha**2 + self.beta)
        for i in range(1, 2 * self.n + 1):
            self.Wm[i] = 1 / (2 * (self.n + self.lambda_))
            self.Wc[i] = self.Wm[i]

    def _ensure_positive_definite(self, P):
        """Ensure covariance matrix is positive definite."""
        # Symmetrize
        P = (P + P.T) / 2
        # Eigenvalue decomposition to fix negative eigenvalues
        eigvals, eigvecs = np.linalg.eigh(P)
        eigvals = np.maximum(eigvals, 1e-6)
        return eigvecs @ np.diag(eigvals) @ eigvecs.T

    def _get_sigma_points(self):
        """Generate sigma points."""
        n = self.n
        sigma_points = np.zeros((2 * n + 1, n))
        sigma_points[0] = self.state

        # Ensure P is positive definite
        P_safe = self._ensure_positive_definite(self.P)
        scale = n + self.lambda_

        try:
            sqrt_P = np.linalg.cholesky(scale * P_safe)
        except np.linalg.LinAlgError:
            # Fallback: use eigenvalue decomposition
            eigvals, eigvecs = np.linalg.eigh(scale * P_safe)
            eigvals = np.maximum(eigvals, 1e-6)
            sqrt_P = eigvecs @ np.diag(np.sqrt(eigvals))

        for i in range(n):
            sigma_points[i + 1] = self.state + sqrt_P[:, i]
            sigma_points[n + i + 1] = self.state - sqrt_P[:, i]

        return sigma_points

    def _get_Q(self, dt: float):
        q = self.Q_scale
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt
        return np.array([[dt4/4, dt3/2, 0, 0],
                        [dt3/2, dt2, 0, 0],
                        [0, 0, dt4/4, dt3/2],
                        [0, 0, dt3/2, dt2]]) * q

    def predict(self, dt: float):
        if not self.initialized:
            return

        # Get sigma points
        sigma_points = self._get_sigma_points()

        # Propagate sigma points through motion model
        F = np.array([[1, dt, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, dt],
                     [0, 0, 0, 1]])

        sigma_points_pred = np.zeros_like(sigma_points)
        for i in range(2 * self.n + 1):
            sigma_points_pred[i] = F @ sigma_points[i]

        # Compute predicted mean and covariance
        self.state = np.sum(self.Wm[:, np.newaxis] * sigma_points_pred, axis=0)

        self.P = np.zeros((self.n, self.n))
        for i in range(2 * self.n + 1):
            diff = sigma_points_pred[i] - self.state
            self.P += self.Wc[i] * np.outer(diff, diff)
        self.P += self._get_Q(dt)

    def update(self, z: np.ndarray):
        if not self.initialized:
            self.initialize(z[0], z[1])
            self.P = np.eye(4) * 100
            return

        # Get sigma points
        sigma_points = self._get_sigma_points()

        # Transform sigma points to measurement space
        H = np.array([[1, 0, 0, 0],
                     [0, 0, 1, 0]])
        z_sigma = np.zeros((2 * self.n + 1, 2))
        for i in range(2 * self.n + 1):
            z_sigma[i] = H @ sigma_points[i]

        # Predicted measurement mean
        z_pred = np.sum(self.Wm[:, np.newaxis] * z_sigma, axis=0)

        # Innovation covariance
        S = np.zeros((2, 2))
        for i in range(2 * self.n + 1):
            diff = z_sigma[i] - z_pred
            S += self.Wc[i] * np.outer(diff, diff)
        S += self.R

        # Cross covariance
        Pxz = np.zeros((self.n, 2))
        for i in range(2 * self.n + 1):
            diff_x = sigma_points[i] - self.state
            diff_z = z_sigma[i] - z_pred
            Pxz += self.Wc[i] * np.outer(diff_x, diff_z)

        # Kalman gain
        K = Pxz @ np.linalg.inv(S)

        # Update
        self.state = self.state + K @ (z - z_pred)
        self.P = self.P - K @ S @ K.T
        # Ensure P stays positive definite
        self.P = self._ensure_positive_definite(self.P)

        self.track_history.append((self.state[0], self.state[2]))


class IMMFilter(BaseTracker):
    """Interacting Multiple Model filter with CV and CT (Coordinated Turn) models."""

    def __init__(self, process_noise: float = 1.0, measurement_noise: float = 10.0):
        super().__init__("IMM", "#DDA0DD")  # Plum/Purple

        # Two models: Constant Velocity (CV) and Coordinated Turn (CT)
        self.n_models = 2
        self.mu = np.array([0.8, 0.2])  # Model probabilities [CV, CT]

        # Markov transition matrix
        self.p_trans = np.array([[0.95, 0.05],   # CV -> CV, CV -> CT
                                 [0.10, 0.90]])   # CT -> CV, CT -> CT

        # States and covariances for each model
        self.states = [None, None]
        self.Ps = [np.eye(4) * 100, np.eye(4) * 100]

        self.Q_scale = process_noise
        self.R = np.eye(2) * measurement_noise
        self.H = np.array([[1, 0, 0, 0],
                          [0, 0, 1, 0]])

        # Turn rate for CT model
        self.omega = 0.1  # rad/s

    def _get_F_cv(self, dt: float):
        """Constant velocity transition matrix."""
        return np.array([[1, dt, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, dt],
                        [0, 0, 0, 1]])

    def _get_F_ct(self, dt: float):
        """Coordinated turn transition matrix."""
        w = self.omega
        if abs(w) < 1e-6:
            return self._get_F_cv(dt)
        sin_wt = np.sin(w * dt)
        cos_wt = np.cos(w * dt)
        return np.array([[1, sin_wt/w, 0, -(1-cos_wt)/w],
                        [0, cos_wt, 0, -sin_wt],
                        [0, (1-cos_wt)/w, 1, sin_wt/w],
                        [0, sin_wt, 0, cos_wt]])

    def _get_Q(self, dt: float):
        q = self.Q_scale
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt3 * dt
        return np.array([[dt4/4, dt3/2, 0, 0],
                        [dt3/2, dt2, 0, 0],
                        [0, 0, dt4/4, dt3/2],
                        [0, 0, dt3/2, dt2]]) * q

    def initialize(self, x: float, y: float):
        super().initialize(x, y)
        self.states = [self.state.copy(), self.state.copy()]
        self.Ps = [np.eye(4) * 100, np.eye(4) * 100]

    def predict(self, dt: float):
        if not self.initialized:
            return

        # Mixing step
        c_bar = self.p_trans.T @ self.mu
        mu_ij = np.zeros((self.n_models, self.n_models))
        for i in range(self.n_models):
            for j in range(self.n_models):
                mu_ij[i, j] = self.p_trans[i, j] * self.mu[i] / (c_bar[j] + 1e-10)

        # Mixed initial states
        mixed_states = []
        mixed_Ps = []
        for j in range(self.n_models):
            x_mixed = np.zeros(4)
            for i in range(self.n_models):
                x_mixed += mu_ij[i, j] * self.states[i]
            mixed_states.append(x_mixed)

            P_mixed = np.zeros((4, 4))
            for i in range(self.n_models):
                diff = self.states[i] - x_mixed
                P_mixed += mu_ij[i, j] * (self.Ps[i] + np.outer(diff, diff))
            mixed_Ps.append(P_mixed)

        # Model-specific predictions
        Fs = [self._get_F_cv(dt), self._get_F_ct(dt)]
        Q = self._get_Q(dt)

        for j in range(self.n_models):
            self.states[j] = Fs[j] @ mixed_states[j]
            self.Ps[j] = Fs[j] @ mixed_Ps[j] @ Fs[j].T + Q

        # Combined state
        self.state = self.mu[0] * self.states[0] + self.mu[1] * self.states[1]

    def update(self, z: np.ndarray):
        if not self.initialized:
            self.initialize(z[0], z[1])
            return

        # Model-specific updates
        likelihoods = np.zeros(self.n_models)

        for j in range(self.n_models):
            # Innovation
            y = z - self.H @ self.states[j]
            S = self.H @ self.Ps[j] @ self.H.T + self.R

            # Likelihood
            det_S = np.linalg.det(S)
            if det_S > 1e-10:
                likelihoods[j] = np.exp(-0.5 * y @ np.linalg.inv(S) @ y) / np.sqrt(det_S)
            else:
                likelihoods[j] = 1e-10

            # Kalman update
            K = self.Ps[j] @ self.H.T @ np.linalg.inv(S)
            self.states[j] = self.states[j] + K @ y
            self.Ps[j] = (np.eye(4) - K @ self.H) @ self.Ps[j]

        # Update model probabilities
        c_bar = self.p_trans.T @ self.mu
        self.mu = c_bar * likelihoods
        self.mu /= (np.sum(self.mu) + 1e-10)

        # Combined state
        self.state = self.mu[0] * self.states[0] + self.mu[1] * self.states[1]

        self.track_history.append((self.state[0], self.state[2]))


def create_all_filters():
    """Create instances of all filter types."""
    return [
        AlphaBetaFilter(alpha=0.5, beta=0.1),
        KalmanFilter(process_noise=1.0, measurement_noise=10.0),
        ExtendedKalmanFilter(process_noise=1.0, range_noise=5.0, bearing_noise=0.02),
        UnscentedKalmanFilter(process_noise=1.0, measurement_noise=10.0),
        IMMFilter(process_noise=1.0, measurement_noise=10.0),
    ]
