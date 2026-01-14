"""
Target Motion Models

Simulates target trajectories for radar tracking demonstration.
- Constant Velocity target: Straight line motion
- Maneuvering target: Makes turns and speed changes
"""

import numpy as np
from abc import ABC, abstractmethod


class Target(ABC):
    """Base class for simulated targets."""

    def __init__(self, x: float, y: float, vx: float, vy: float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.trajectory = [(x, y)]

    @abstractmethod
    def update(self, dt: float):
        """Update target state by dt seconds."""
        pass

    def get_position(self):
        """Return current position."""
        return self.x, self.y

    def get_state(self):
        """Return full state [x, vx, y, vy]."""
        return np.array([self.x, self.vx, self.y, self.vy])


class ConstantVelocityTarget(Target):
    """Target moving in a straight line at constant speed."""

    def __init__(self, x: float, y: float, vx: float, vy: float):
        super().__init__(x, y, vx, vy)

    def update(self, dt: float):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trajectory.append((self.x, self.y))


class ManeuveringTarget(Target):
    """Target that makes coordinated turns and speed changes."""

    def __init__(self, x: float, y: float, vx: float, vy: float):
        super().__init__(x, y, vx, vy)
        self.time = 0.0
        self.turn_rate = 0.0  # Current turn rate (rad/s)
        self.maneuver_schedule = self._create_maneuver_schedule()

    def _create_maneuver_schedule(self):
        """Define when maneuvers occur."""
        return [
            (5.0, 0.08),    # At t=5s, start turning right
            (12.0, 0.0),    # At t=12s, stop turning
            (18.0, -0.12),  # At t=18s, turn left harder
            (25.0, 0.0),    # At t=25s, straighten out
            (32.0, 0.06),   # At t=32s, gentle right turn
            (40.0, 0.0),    # At t=40s, stop
        ]

    def update(self, dt: float):
        self.time += dt

        # Check for maneuver changes
        for trigger_time, new_turn_rate in self.maneuver_schedule:
            if abs(self.time - trigger_time) < dt:
                self.turn_rate = new_turn_rate

        # Apply coordinated turn dynamics
        if abs(self.turn_rate) > 1e-6:
            # Coordinated turn
            omega = self.turn_rate
            speed = np.sqrt(self.vx**2 + self.vy**2)
            heading = np.arctan2(self.vy, self.vx)

            # Update heading
            heading += omega * dt

            # Update velocity components
            self.vx = speed * np.cos(heading)
            self.vy = speed * np.sin(heading)

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.trajectory.append((self.x, self.y))


class CircularTarget(Target):
    """Target moving in a circle - good for testing."""

    def __init__(self, cx: float, cy: float, radius: float, speed: float):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.angular_speed = speed / radius
        self.angle = 0.0
        x = cx + radius
        y = cy
        vx = 0
        vy = speed
        super().__init__(x, y, vx, vy)

    def update(self, dt: float):
        self.angle += self.angular_speed * dt
        self.x = self.cx + self.radius * np.cos(self.angle)
        self.y = self.cy + self.radius * np.sin(self.angle)
        self.vx = -self.radius * self.angular_speed * np.sin(self.angle)
        self.vy = self.radius * self.angular_speed * np.cos(self.angle)
        self.trajectory.append((self.x, self.y))


def create_demo_targets(radar_range: float = 100.0):
    """Create 10 targets for the demo - mix of CV and maneuvering."""
    targets = []

    # 5 Constant velocity targets
    cv_configs = [
        (-0.8, -0.6, 3.0, 2.5),   # Bottom-left going up-right
        (0.9, 0.2, -2.0, 1.5),    # Right going left-up
        (-0.5, 0.7, 2.5, -1.0),   # Top-left going right-down
        (0.3, -0.8, 1.0, 3.0),    # Bottom going up
        (-0.7, 0.1, 2.0, 0.5),    # Left going right
    ]

    for i, (x_frac, y_frac, vx, vy) in enumerate(cv_configs):
        target = ConstantVelocityTarget(
            x=radar_range * x_frac,
            y=radar_range * y_frac,
            vx=vx,
            vy=vy
        )
        targets.append((f"CV_{i+1}", target, "#FFFFFF"))

    # 5 Maneuvering targets
    man_configs = [
        (0.7, -0.3, -2.5, 2.0),   # Right-bottom, turns left
        (-0.4, -0.5, 1.5, 2.5),   # Bottom-left, maneuvering up
        (0.5, 0.6, -1.5, -2.0),   # Top-right, going down-left
        (-0.6, 0.4, 2.0, -1.5),   # Left, heading right-down
        (0.2, 0.8, -0.5, -2.5),   # Top, coming down
    ]

    for i, (x_frac, y_frac, vx, vy) in enumerate(man_configs):
        target = ManeuveringTarget(
            x=radar_range * x_frac,
            y=radar_range * y_frac,
            vx=vx,
            vy=vy
        )
        targets.append((f"Maneuvering_{i+1}", target, "#FFFFFF"))

    return targets
