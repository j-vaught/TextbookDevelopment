#!/usr/bin/env python3
"""
Kalman Filter Radar Tracking Demonstration

Runs 5 parallel tracking systems, each using a different filter type.
Each track is color-coded by track ID (not filter type).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle

from targets import create_demo_targets
from radar import RadarSimulator
from tracker import MultiTargetTracker


FILTER_TYPES = ["Alpha-Beta", "Kalman Filter", "EKF", "UKF", "IMM"]


class RadarTrackingDemo:
    """Main demo class - runs N trackers in parallel."""

    def __init__(self):
        # Simulation parameters
        self.radar_range = 100.0
        self.dt = 0.5
        self.time = 0.0

        # Create radar simulator
        self.radar = RadarSimulator(
            radar_range=self.radar_range,
            pd=0.85,
            pfa=0.005,
            measurement_noise=3.0,
            n_clutter_cells=300
        )

        # Ground truth targets
        self.targets = create_demo_targets(self.radar_range)

        # Create one tracker per filter type
        self.trackers = {}
        for ft in FILTER_TYPES:
            self.trackers[ft] = MultiTargetTracker(filter_type=ft, gating_threshold=15.0)

        # Error tracking
        self.time_history = []
        self.error_history = {ft: {} for ft in FILTER_TYPES}  # ft -> {track_id -> [errors]}

        # Setup visualization
        self._setup_figure()
        self._setup_error_figure()

    def _setup_figure(self):
        """Create figure with 5 subplots - one per filter."""
        plt.style.use('dark_background')

        self.fig = plt.figure(figsize=(18, 10))
        self.fig.patch.set_facecolor('#0a0a0a')

        # 2 rows x 3 columns (5 radar plots + 1 info)
        self.axes = {}
        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]

        for i, ft in enumerate(FILTER_TYPES):
            row, col = positions[i]
            ax = self.fig.add_subplot(2, 3, row * 3 + col + 1)
            ax.set_facecolor('#0a0a0a')
            ax.set_aspect('equal')
            ax.set_xlim(-self.radar_range * 1.1, self.radar_range * 1.1)
            ax.set_ylim(-self.radar_range * 1.1, self.radar_range * 1.1)

            # Draw range rings
            for r in [25, 50, 75, 100]:
                circle = Circle((0, 0), r, fill=False, color='#1a3a1a',
                               linestyle='--', linewidth=0.5)
                ax.add_patch(circle)

            ax.axhline(y=0, color='#1a3a1a', linewidth=0.5, linestyle='--')
            ax.axvline(x=0, color='#1a3a1a', linewidth=0.5, linestyle='--')

            ax.set_title(ft, color='#00ff00', fontsize=11, fontweight='bold')
            ax.tick_params(colors='#2a4a2a', labelsize=7)
            for spine in ax.spines.values():
                spine.set_color('#1a3a1a')

            self.axes[ft] = ax

        # Info panel (bottom right)
        self.ax_info = self.fig.add_subplot(2, 3, 6)
        self.ax_info.set_facecolor('#0a0a0a')
        self.ax_info.axis('off')

        # Plot elements storage
        self.detection_scatters = {ft: [] for ft in FILTER_TYPES}
        self.track_lines = {ft: {} for ft in FILTER_TYPES}  # ft -> {track_id -> line}

    def _setup_error_figure(self):
        """Create separate figure for error plots."""
        self.fig_error = plt.figure(figsize=(14, 8))
        self.fig_error.patch.set_facecolor('#0a0a0a')
        self.fig_error.suptitle('Tracking Error by Filter Type', color='#00ff00', fontsize=14)

        self.error_axes = {}
        for i, ft in enumerate(FILTER_TYPES):
            ax = self.fig_error.add_subplot(2, 3, i + 1)
            ax.set_facecolor('#0a0a0a')
            ax.set_title(ft, color='#00ff00', fontsize=10)
            ax.set_xlabel('Time (s)', color='#888888', fontsize=8)
            ax.set_ylabel('Position Error', color='#888888', fontsize=8)
            ax.tick_params(colors='#444444', labelsize=7)
            ax.set_xlim(0, 50)
            ax.set_ylim(0, 30)
            ax.grid(True, alpha=0.2)
            for spine in ax.spines.values():
                spine.set_color('#333333')
            self.error_axes[ft] = ax

        # Summary plot (bottom right)
        self.ax_summary = self.fig_error.add_subplot(2, 3, 6)
        self.ax_summary.set_facecolor('#0a0a0a')
        self.ax_summary.set_title('Mean Error Comparison', color='#00ff00', fontsize=10)
        self.ax_summary.tick_params(colors='#444444', labelsize=7)
        for spine in self.ax_summary.spines.values():
            spine.set_color('#333333')

        self.error_lines = {ft: {} for ft in FILTER_TYPES}  # ft -> {track_id -> line}

    def update(self, frame):
        """Animation update function."""
        self.time += self.dt

        # Update ground truth targets
        for name, target, _ in self.targets:
            target.update(self.dt)

        # Generate detections
        detections = self.radar.generate_detections(self.targets)
        self.radar.update_history(detections)

        # Extract centroids
        centroids = []
        for det in detections['target_detections']:
            if det['detected'] and det['measured_pos']:
                centroids.append(det['measured_pos'])

        # Small chance clutter becomes a centroid
        for clutter_pos in detections['clutter']:
            if np.random.random() < 0.08:
                centroids.append(clutter_pos)

        # Process through all trackers (same detections)
        all_tracks = {}
        all_associations = {}
        for ft in FILTER_TYPES:
            tracks, assocs = self.trackers[ft].process_detections(centroids)
            all_tracks[ft] = tracks
            all_associations[ft] = assocs

        # Update displays
        self._update_displays(detections, all_tracks, all_associations, centroids)

        # Compute and update errors
        self.time_history.append(self.time)
        self._compute_errors(all_tracks)
        self._update_error_plots()

        return []

    def _update_displays(self, detections, all_tracks, all_associations, centroids):
        """Update all radar displays."""
        # Get blob pixels for each target detection
        target_blobs = {}  # centroid_idx -> list of pixels
        centroid_to_blob = {}

        # Map centroids to their blob pixels
        det_idx = 0
        for det in detections['target_detections']:
            if det['detected'] and det.get('blob_pixels'):
                centroid_to_blob[det_idx] = det['blob_pixels']
                det_idx += 1

        # Clutter pixels (not associated with any centroid)
        clutter_pixels = detections['clutter']

        for ft in FILTER_TYPES:
            ax = self.axes[ft]
            tracks = all_tracks[ft]
            associations = all_associations[ft]

            # Clear old detections
            if self.detection_scatters[ft]:
                for scatter in self.detection_scatters[ft]:
                    scatter.remove()
                self.detection_scatters[ft] = []

            scatters = []

            # Build map from detection index to track
            det_to_track = {}
            for det_idx, track_idx in associations:
                if track_idx < len(tracks):
                    det_to_track[det_idx] = tracks[track_idx]

            # Plot blob pixels colored by associated track
            for det_idx, blob_pixels in centroid_to_blob.items():
                if blob_pixels:
                    xs = [p[0] for p in blob_pixels]
                    ys = [p[1] for p in blob_pixels]

                    if det_idx in det_to_track:
                        color = det_to_track[det_idx].color
                    else:
                        color = '#444444'  # Unassociated = gray

                    scatter = ax.scatter(xs, ys, c=[color], s=2, marker='s', edgecolors='none')
                    scatters.append(scatter)

            # Plot clutter as dim gray
            if clutter_pixels:
                xs = [p[0] for p in clutter_pixels]
                ys = [p[1] for p in clutter_pixels]
                scatter = ax.scatter(xs, ys, c='#333333', s=2, marker='s', edgecolors='none')
                scatters.append(scatter)

            self.detection_scatters[ft] = scatters

            # Update track lines (thin, same color as blob)
            active_ids = set()

            for track in tracks:
                tid = track.id
                active_ids.add(tid)

                if tid not in self.track_lines[ft]:
                    line, = ax.plot([], [], color=track.color, linewidth=1.0, alpha=0.5)
                    self.track_lines[ft][tid] = line

                if len(track.track_history) > 1:
                    xs, ys = zip(*track.track_history[-150:])
                    self.track_lines[ft][tid].set_data(xs, ys)
                    self.track_lines[ft][tid].set_color(track.color)
                    alpha = 0.6 if track.state == "confirmed" else 0.2
                    self.track_lines[ft][tid].set_alpha(alpha)

            # Remove old tracks
            old_ids = set(self.track_lines[ft].keys()) - active_ids
            for tid in old_ids:
                self.track_lines[ft][tid].remove()
                del self.track_lines[ft][tid]

        # Update info panel
        self._update_info(all_tracks)

    def _compute_errors(self, all_tracks):
        """Compute tracking errors against ground truth."""
        # Get ground truth positions
        gt_positions = []
        for name, target, _ in self.targets:
            gt_positions.append(target.get_position())

        for ft in FILTER_TYPES:
            tracks = all_tracks[ft]

            for track in tracks:
                if track.state != "confirmed":
                    continue

                tid = track.id
                pos = track.get_position()
                if not pos:
                    continue

                # Find nearest ground truth
                min_dist = float('inf')
                for gt_pos in gt_positions:
                    dist = np.sqrt((pos[0] - gt_pos[0])**2 + (pos[1] - gt_pos[1])**2)
                    min_dist = min(min_dist, dist)

                # Only count if reasonably close (associated with a real target)
                if min_dist < 25:
                    if tid not in self.error_history[ft]:
                        self.error_history[ft][tid] = {'times': [], 'errors': [], 'color': track.color}
                    self.error_history[ft][tid]['times'].append(self.time)
                    self.error_history[ft][tid]['errors'].append(min_dist)

    def _update_error_plots(self):
        """Update error plot figure."""
        for ft in FILTER_TYPES:
            ax = self.error_axes[ft]

            # Update existing lines and add new ones
            for tid, data in self.error_history[ft].items():
                if tid not in self.error_lines[ft]:
                    line, = ax.plot([], [], color=data['color'], linewidth=1, alpha=0.8)
                    self.error_lines[ft][tid] = line

                if data['times']:
                    self.error_lines[ft][tid].set_data(data['times'], data['errors'])

            # Auto-scale x-axis
            if self.time_history:
                ax.set_xlim(0, max(self.time_history) + 5)

        # Update summary (mean error per filter)
        self.ax_summary.clear()
        self.ax_summary.set_facecolor('#0a0a0a')
        self.ax_summary.set_title('Mean Error Comparison', color='#00ff00', fontsize=10)

        filter_means = []
        filter_names = []
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD']

        for i, ft in enumerate(FILTER_TYPES):
            all_errors = []
            for tid, data in self.error_history[ft].items():
                all_errors.extend(data['errors'])

            if all_errors:
                mean_err = np.mean(all_errors)
            else:
                mean_err = 0

            filter_means.append(mean_err)
            filter_names.append(ft.replace(' ', '\n'))

        if any(filter_means):
            bars = self.ax_summary.bar(range(len(FILTER_TYPES)), filter_means, color=colors)
            self.ax_summary.set_xticks(range(len(FILTER_TYPES)))
            self.ax_summary.set_xticklabels(filter_names, fontsize=7, color='#888888')
            self.ax_summary.set_ylabel('Mean Error', color='#888888', fontsize=8)
            self.ax_summary.tick_params(colors='#444444', labelsize=7)

        self.fig_error.canvas.draw_idle()

    def _update_info(self, all_tracks):
        """Update info panel."""
        self.ax_info.clear()
        self.ax_info.set_facecolor('#0a0a0a')
        self.ax_info.axis('off')

        self.ax_info.text(0.5, 0.95, 'TRACKING COMPARISON', ha='center', va='top',
                         color='#00ff00', fontsize=12, fontweight='bold',
                         transform=self.ax_info.transAxes)

        info = f"""
Time: {self.time:.1f}s
Ground Truth Targets: {len(self.targets)}

Confirmed Tracks:
"""
        y = 0.65
        self.ax_info.text(0.1, 0.75, info, va='top', color='#888888', fontsize=10,
                         transform=self.ax_info.transAxes, family='monospace')

        for ft in FILTER_TYPES:
            confirmed = len([t for t in all_tracks[ft] if t.state == "confirmed"])
            total = len(all_tracks[ft])
            self.ax_info.text(0.1, y, f"  {ft}: {confirmed}/{total}",
                             color='#00aa00', fontsize=9,
                             transform=self.ax_info.transAxes, family='monospace')
            y -= 0.06

        self.ax_info.text(0.1, 0.25, "Track colors = unique track IDs\n(same across all filters)",
                         color='#666666', fontsize=8,
                         transform=self.ax_info.transAxes, family='monospace')

    def run(self):
        """Run the animation."""
        self.ani = FuncAnimation(
            self.fig, self.update,
            frames=None,
            interval=100,
            blit=False,
            cache_frame_data=False
        )
        plt.tight_layout()
        plt.show()


def main():
    print("Kalman Filter Comparison Demo")
    print("=" * 40)
    print("Running 5 parallel trackers, one per filter type.")
    print("Same detections fed to all trackers.")
    print()
    print("Track colors represent unique track IDs.")
    print()

    demo = RadarTrackingDemo()
    demo.run()


if __name__ == "__main__":
    main()
