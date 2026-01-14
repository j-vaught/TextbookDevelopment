"""
Radar Detection Simulation

Simulates binary radar detections with:
- Probability of detection (Pd) for targets
- Probability of false alarm (Pfa) for clutter
- Measurement noise
"""

import numpy as np


class RadarSimulator:
    """Simulates radar detections with noise and clutter."""

    def __init__(self,
                 radar_range: float = 100.0,
                 pd: float = 0.85,
                 pfa: float = 0.01,
                 measurement_noise: float = 2.0,
                 n_clutter_cells: int = 500,
                 blob_size: int = 12,
                 blob_spread: float = 3.0):
        """
        Args:
            radar_range: Maximum radar range
            pd: Probability of detection for real targets
            pfa: Probability of false alarm per clutter cell
            measurement_noise: Standard deviation of measurement noise
            n_clutter_cells: Number of resolution cells to check for clutter
            blob_size: Number of pixels per target blob
            blob_spread: Spread of blob pixels around target center
        """
        self.radar_range = radar_range
        self.pd = pd
        self.pfa = pfa
        self.measurement_noise = measurement_noise
        self.n_clutter_cells = n_clutter_cells
        self.blob_size = blob_size
        self.blob_spread = blob_spread

        # Detection history for visualization (just current scan, no decay)
        self.current_detections = []

    def _generate_blob(self, cx, cy):
        """Generate a solid filled ellipsoid blob of pixels."""
        pixels = []

        # Ellipse oriented radially from radar origin
        range_to_target = np.sqrt(cx**2 + cy**2)
        if range_to_target < 1:
            range_to_target = 1

        # Unit vector pointing from origin to target (range direction)
        ux, uy = cx / range_to_target, cy / range_to_target
        # Perpendicular (cross-range direction)
        px, py = -uy, ux

        # Circle radius
        a = self.blob_spread * 0.8
        b = a  # Equal for circle

        # Fill circle with grid of points - no holes, dense fill
        step = 0.35  # Pixel spacing (smaller = denser fill)
        for r in np.arange(-a, a + step, step):
            for c in np.arange(-b, b + step, step):
                # Check if inside ellipse
                if (r/a)**2 + (c/b)**2 <= 1.0:
                    # Transform to x,y coordinates
                    dx = r * ux + c * px
                    dy = r * uy + c * py
                    pixels.append((cx + dx, cy + dy))

        return pixels

    def generate_detections(self, targets):
        """
        Generate binary detections for current scan.

        Args:
            targets: List of (name, target_object, color) tuples

        Returns:
            dict with 'target_detections' and 'clutter' lists
        """
        target_detections = []
        clutter = []
        blob_pixels = []  # All pixels from target blobs

        # Check each target for detection
        for name, target, color in targets:
            x, y = target.get_position()

            # Check if in range
            r = np.sqrt(x**2 + y**2)
            if r > self.radar_range:
                continue

            # Binary detection based on Pd
            if np.random.random() < self.pd:
                # Generate blob of pixels around target
                blob = self._generate_blob(x, y)
                blob_pixels.extend(blob)

                # Centroid for tracking (with noise)
                if blob:
                    blob_x = np.mean([p[0] for p in blob])
                    blob_y = np.mean([p[1] for p in blob])
                else:
                    blob_x = x + np.random.normal(0, self.measurement_noise)
                    blob_y = y + np.random.normal(0, self.measurement_noise)

                target_detections.append({
                    'name': name,
                    'true_pos': (x, y),
                    'measured_pos': (blob_x, blob_y),
                    'detected': True,
                    'blob_pixels': blob
                })
            else:
                # Missed detection - maybe partial blob
                if np.random.random() < 0.3:  # Sometimes partial detection
                    partial_blob = self._generate_blob(x, y)
                    # Fewer pixels for partial
                    partial_blob = partial_blob[:len(partial_blob)//3]
                    blob_pixels.extend(partial_blob)

                target_detections.append({
                    'name': name,
                    'true_pos': (x, y),
                    'measured_pos': None,
                    'detected': False,
                    'blob_pixels': []
                })

        # Generate clutter (false alarms) - single pixels scattered
        n_clutter = np.random.binomial(self.n_clutter_cells, self.pfa)
        for _ in range(n_clutter):
            # Random position within radar coverage
            r = np.sqrt(np.random.random()) * self.radar_range
            theta = np.random.random() * 2 * np.pi
            x_clutter = r * np.cos(theta)
            y_clutter = r * np.sin(theta)
            clutter.append((x_clutter, y_clutter))

        return {
            'target_detections': target_detections,
            'clutter': clutter,
            'blob_pixels': blob_pixels
        }

    def update_history(self, detections):
        """Store current scan detections (no history/decay)."""
        self.current_detections = []

        # Add all blob pixels (these are the actual radar returns)
        for pixel in detections.get('blob_pixels', []):
            self.current_detections.append(pixel)

        # Add clutter pixels
        for clutter_pos in detections['clutter']:
            self.current_detections.append(clutter_pos)

    def get_current_detections(self):
        """Get current scan detections - binary on/off."""
        return self.current_detections
