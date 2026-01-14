"""
Multi-Target Tracker with Data Association

Handles:
- Track initiation from unassociated detections
- Data association (Global Nearest Neighbor)
- Track state management (tentative, confirmed, coasting, deleted)
- Track deletion after too many misses
"""

import numpy as np
from filters import (AlphaBetaFilter, KalmanFilter, ExtendedKalmanFilter,
                     UnscentedKalmanFilter, IMMFilter)


def create_filter_by_type(filter_type: str):
    """Create a single filter of the specified type."""
    if filter_type == "Alpha-Beta":
        return AlphaBetaFilter()
    elif filter_type == "Kalman Filter":
        return KalmanFilter()
    elif filter_type == "EKF":
        return ExtendedKalmanFilter()
    elif filter_type == "UKF":
        return UnscentedKalmanFilter()
    elif filter_type == "IMM":
        return IMMFilter()
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")


class Track:
    """A single track with one filter."""

    _next_id = 1
    _id_counters = {}  # Per-tracker ID counters

    def __init__(self, x: float, y: float, filter_type: str, tracker_id: int = 0):
        # Use per-tracker ID counter
        if tracker_id not in Track._id_counters:
            Track._id_counters[tracker_id] = 1
        self.id = Track._id_counters[tracker_id]
        Track._id_counters[tracker_id] += 1

        # Single filter for this track
        self.filter = create_filter_by_type(filter_type)
        self.filter.initialize(x, y)
        self.filter_type = filter_type

        # Track state
        self.hits = 1
        self.misses = 0
        self.age = 0
        self.state = "tentative"  # tentative, confirmed, deleted

        # Track history for visualization
        self.track_history = [(x, y)]

        # Unique color for this track
        self.color = self._generate_color()

    def _generate_color(self):
        """Generate a unique color for this track."""
        np.random.seed(self.id * 13 + 7)
        hue = (self.id * 0.618033988749895) % 1.0  # Golden ratio
        # Convert HSV to RGB
        h = hue * 6
        c = 0.9
        x = c * (1 - abs(h % 2 - 1))
        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return (r + 0.1, g + 0.1, b + 0.1)

    def predict(self, dt: float):
        """Predict filter forward."""
        self.filter.predict(dt)
        self.age += 1

    def update(self, z: np.ndarray):
        """Update filter with measurement."""
        self.filter.update(z)
        self.hits += 1
        self.misses = 0

        # Record position
        pos = self.get_position()
        if pos:
            self.track_history.append(pos)

        # Confirm track after enough hits
        if self.state == "tentative" and self.hits >= 3:
            self.state = "confirmed"

    def miss(self):
        """Called when track has no associated detection."""
        self.misses += 1

        # Still predict position for coasting
        pos = self.get_position()
        if pos:
            self.track_history.append(pos)

        # Delete track after too many misses
        if self.state == "tentative" and self.misses >= 2:
            self.state = "deleted"
        elif self.state == "confirmed" and self.misses >= 5:
            self.state = "deleted"

    def get_position(self):
        """Get estimated position."""
        return self.filter.get_position()

    def get_velocity(self):
        """Get estimated velocity."""
        state = self.filter.state
        if state is not None:
            return state[1], state[3]  # vx, vy
        return 0, 0


class MultiTargetTracker:
    """Manages multiple tracks with data association."""

    _tracker_counter = 0

    def __init__(self, filter_type: str = "Kalman Filter", gating_threshold: float = 20.0):
        """
        Args:
            filter_type: Type of filter to use for all tracks
            gating_threshold: Maximum distance for association
        """
        self.filter_type = filter_type
        self.tracks = []
        self.gating_threshold = gating_threshold
        self.dt = 0.5
        self.tracker_id = MultiTargetTracker._tracker_counter
        MultiTargetTracker._tracker_counter += 1

    def process_detections(self, detections: list):
        """
        Process a list of detection centroids.

        Args:
            detections: List of (x, y) tuples

        Returns:
            List of active tracks
        """
        # Predict all tracks forward
        for track in self.tracks:
            track.predict(self.dt)

        # Data association using Global Nearest Neighbor
        associations = self._associate(detections)

        # Update associated tracks
        for det_idx, track_idx in associations:
            z = np.array(detections[det_idx])
            self.tracks[track_idx].update(z)

        # Mark unassociated tracks as missed
        associated_tracks = set(t for _, t in associations)
        for i, track in enumerate(self.tracks):
            if i not in associated_tracks:
                track.miss()

        # Initialize new tracks from unassociated detections
        associated_dets = set(d for d, _ in associations)
        for i, det in enumerate(detections):
            if i not in associated_dets:
                new_track = Track(det[0], det[1], self.filter_type, self.tracker_id)
                self.tracks.append(new_track)

        # Remove deleted tracks
        self.tracks = [t for t in self.tracks if t.state != "deleted"]

        # Return tracks and association info for visualization
        return self.tracks, associations

    def _associate(self, detections: list):
        """
        Global Nearest Neighbor association.

        Returns list of (detection_idx, track_idx) pairs.
        """
        if not self.tracks or not detections:
            return []

        n_det = len(detections)
        n_trk = len(self.tracks)

        # Compute cost matrix (Euclidean distance)
        cost = np.full((n_det, n_trk), np.inf)

        for i, det in enumerate(detections):
            for j, track in enumerate(self.tracks):
                pos = track.get_position()
                if pos is None:
                    continue

                # Euclidean distance
                dist = np.sqrt((det[0] - pos[0])**2 + (det[1] - pos[1])**2)

                # Gating
                if dist < self.gating_threshold:
                    cost[i, j] = dist

        # Greedy assignment (simple but effective for well-separated targets)
        associations = []
        used_dets = set()
        used_trks = set()

        while True:
            # Find minimum cost
            min_cost = np.inf
            min_i, min_j = -1, -1

            for i in range(n_det):
                if i in used_dets:
                    continue
                for j in range(n_trk):
                    if j in used_trks:
                        continue
                    if cost[i, j] < min_cost:
                        min_cost = cost[i, j]
                        min_i, min_j = i, j

            if min_cost == np.inf:
                break

            associations.append((min_i, min_j))
            used_dets.add(min_i)
            used_trks.add(min_j)

        return associations

    def get_confirmed_tracks(self):
        """Return only confirmed tracks."""
        return [t for t in self.tracks if t.state == "confirmed"]

    def get_all_tracks(self):
        """Return all active tracks."""
        return self.tracks
