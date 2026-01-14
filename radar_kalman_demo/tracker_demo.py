#!/usr/bin/env python3
"""
Tracker Demo - Reads video and tracks blobs using different Kalman filters.

Includes error analysis against ground truth.
"""

import numpy as np
import cv2
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

from filters import (AlphaBetaFilter, KalmanFilter, ExtendedKalmanFilter,
                     UnscentedKalmanFilter, IMMFilter)


FILTER_TYPES = ["Alpha-Beta", "Kalman Filter", "EKF", "UKF", "IMM"]


def create_filter(filter_type):
    """Create a filter instance."""
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


class Track:
    """A tracked blob."""

    _id_counter = 0

    def __init__(self, x, y, filter_type):
        Track._id_counter += 1
        self.id = Track._id_counter
        self.filter = create_filter(filter_type)
        self.filter.initialize(x, y)
        self.history = [(x, y)]
        self.hits = 1
        self.misses = 0
        self.state = "tentative"
        self.color = self._make_color()

    def _make_color(self):
        np.random.seed(self.id * 17)
        hue = (self.id * 0.618033) % 1.0
        h = hue * 6
        c = 0.9
        x = c * (1 - abs(h % 2 - 1))
        if h < 1: r, g, b = c, x, 0
        elif h < 2: r, g, b = x, c, 0
        elif h < 3: r, g, b = 0, c, x
        elif h < 4: r, g, b = 0, x, c
        elif h < 5: r, g, b = x, 0, c
        else: r, g, b = c, 0, x
        return (r + 0.1, g + 0.1, b + 0.1)

    def predict(self, dt=1.0):
        self.filter.predict(dt)

    def update(self, x, y):
        self.filter.update(np.array([x, y]))
        pos = self.filter.get_position()
        if pos:
            self.history.append(pos)
        self.hits += 1
        self.misses = 0
        if self.state == "tentative" and self.hits >= 3:
            self.state = "confirmed"

    def miss(self):
        self.misses += 1
        pos = self.filter.get_position()
        if pos:
            self.history.append(pos)
        if self.state == "tentative" and self.misses >= 2:
            self.state = "deleted"
        elif self.state == "confirmed" and self.misses >= 5:
            self.state = "deleted"

    def get_position(self):
        return self.filter.get_position()


class BlobTracker:
    """Multi-target tracker for a single filter type."""

    def __init__(self, filter_type, gate=30.0):
        self.filter_type = filter_type
        self.gate = gate
        self.tracks = []

    def detect_blobs(self, frame):
        """Find blob centroids in binary frame."""
        contours, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centroids = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 20:  # Filter tiny noise
                M = cv2.moments(cnt)
                if M["m00"] > 0:
                    cx = M["m10"] / M["m00"]
                    cy = M["m01"] / M["m00"]
                    centroids.append((cx, cy))
        return centroids

    def process_frame(self, frame, dt=1.0):
        """Process one frame."""
        # Predict all tracks
        for track in self.tracks:
            track.predict(dt)

        # Detect blobs
        centroids = self.detect_blobs(frame)

        # Associate detections to tracks (greedy nearest neighbor)
        associations = self._associate(centroids)

        # Update associated tracks
        for det_idx, track_idx in associations:
            cx, cy = centroids[det_idx]
            self.tracks[track_idx].update(cx, cy)

        # Mark unassociated tracks as missed
        assoc_tracks = set(t for _, t in associations)
        for i, track in enumerate(self.tracks):
            if i not in assoc_tracks:
                track.miss()

        # Start new tracks for unassociated detections
        assoc_dets = set(d for d, _ in associations)
        for i, (cx, cy) in enumerate(centroids):
            if i not in assoc_dets:
                self.tracks.append(Track(cx, cy, self.filter_type))

        # Remove deleted tracks
        self.tracks = [t for t in self.tracks if t.state != "deleted"]

        return centroids

    def _associate(self, centroids):
        """Greedy nearest-neighbor association."""
        if not self.tracks or not centroids:
            return []

        associations = []
        used_dets = set()
        used_tracks = set()

        # Build cost matrix
        costs = []
        for i, (cx, cy) in enumerate(centroids):
            for j, track in enumerate(self.tracks):
                pos = track.get_position()
                if pos:
                    dist = np.sqrt((cx - pos[0])**2 + (cy - pos[1])**2)
                    if dist < self.gate:
                        costs.append((dist, i, j))

        # Greedy assignment
        costs.sort()
        for dist, det_idx, track_idx in costs:
            if det_idx not in used_dets and track_idx not in used_tracks:
                associations.append((det_idx, track_idx))
                used_dets.add(det_idx)
                used_tracks.add(track_idx)

        return associations


class TrackerDemo:
    """Main demo - runs all filter types on same video."""

    def __init__(self, video_path, ground_truth_path=None):
        self.cap = cv2.VideoCapture(video_path)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.n_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"Video: {self.width}x{self.height}, {self.n_frames} frames, {self.fps} fps")

        # Load ground truth
        self.ground_truth = None
        if ground_truth_path and os.path.exists(ground_truth_path):
            with open(ground_truth_path, 'r') as f:
                self.ground_truth = json.load(f)
            print(f"Loaded ground truth: {len(self.ground_truth['objects'])} objects")

        # Create one tracker per filter type
        self.trackers = {ft: BlobTracker(ft) for ft in FILTER_TYPES}

        # Track-to-ground-truth associations (built during first few frames)
        self.track_to_gt = {ft: {} for ft in FILTER_TYPES}  # ft -> {track_id -> gt_blob_id}

        # Error history
        self.error_history = {ft: [] for ft in FILTER_TYPES}  # ft -> [(frame, mean_error)]
        self.per_object_errors = {ft: {obj_id: [] for obj_id in self.ground_truth['objects']}
                                  for ft in FILTER_TYPES} if self.ground_truth else {}

        # Pre-load all frames
        print("Loading frames...")
        self.frames = []
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if len(frame.shape) == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.frames.append(frame)
        self.cap.release()
        print(f"Loaded {len(self.frames)} frames")

        self.frame_idx = 0
        self._setup_figure()
        self._setup_error_figure()

    def _setup_figure(self):
        """Setup matplotlib figure."""
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 9))
        self.fig.patch.set_facecolor('#0a0a0a')

        # 2x3 grid for 5 trackers + info
        self.axes = {}
        for i, ft in enumerate(FILTER_TYPES):
            ax = self.fig.add_subplot(2, 3, i + 1)
            ax.set_facecolor('#0a0a0a')
            ax.set_xlim(0, self.width)
            ax.set_ylim(self.height, 0)  # Flip y
            ax.set_aspect('equal')
            ax.set_title(ft, color='#00ff00', fontsize=10)
            ax.tick_params(colors='#333333', labelsize=6)
            self.axes[ft] = ax

        self.ax_info = self.fig.add_subplot(2, 3, 6)
        self.ax_info.set_facecolor('#0a0a0a')
        self.ax_info.axis('off')

        # Plot elements
        self.img_plots = {}
        self.track_lines = {ft: {} for ft in FILTER_TYPES}
        self.det_scatters = {ft: None for ft in FILTER_TYPES}

    def _setup_error_figure(self):
        """Setup error analysis figure."""
        self.fig_error = plt.figure(figsize=(14, 8))
        self.fig_error.patch.set_facecolor('#0a0a0a')
        self.fig_error.suptitle('Tracking Error Analysis', color='#00ff00', fontsize=14)

        # 2x3 grid: 5 error plots + summary bar chart
        self.error_axes = {}
        filter_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#DDA0DD']
        self.filter_colors = {ft: filter_colors[i] for i, ft in enumerate(FILTER_TYPES)}

        for i, ft in enumerate(FILTER_TYPES):
            ax = self.fig_error.add_subplot(2, 3, i + 1)
            ax.set_facecolor('#0a0a0a')
            ax.set_title(ft, color=self.filter_colors[ft], fontsize=10)
            ax.set_xlabel('Frame', color='#666666', fontsize=8)
            ax.set_ylabel('Error (pixels)', color='#666666', fontsize=8)
            ax.tick_params(colors='#444444', labelsize=7)
            ax.set_xlim(0, len(self.frames))
            ax.set_ylim(0, 30)
            ax.grid(True, alpha=0.2)
            for spine in ax.spines.values():
                spine.set_color('#333333')
            self.error_axes[ft] = ax

        # Summary bar chart
        self.ax_summary = self.fig_error.add_subplot(2, 3, 6)
        self.ax_summary.set_facecolor('#0a0a0a')
        self.ax_summary.set_title('Mean Error by Filter', color='#00ff00', fontsize=10)
        self.ax_summary.tick_params(colors='#444444', labelsize=7)
        for spine in self.ax_summary.spines.values():
            spine.set_color('#333333')

        self.error_plot_lines = {ft: {} for ft in FILTER_TYPES}  # ft -> {obj_id -> line}
        self.mean_error_line = {ft: None for ft in FILTER_TYPES}

    def _associate_track_to_gt(self, ft, track, frame_idx):
        """Associate a track with ground truth object based on position."""
        if not self.ground_truth or track.id in self.track_to_gt[ft]:
            return

        pos = track.get_position()
        if not pos:
            return

        frame_gt = self.ground_truth['frames'][frame_idx]
        best_dist = float('inf')
        best_obj = None

        for obj_id, obj_data in frame_gt['objects'].items():
            gt_x, gt_y = obj_data['x'], obj_data['y']
            dist = np.sqrt((pos[0] - gt_x)**2 + (pos[1] - gt_y)**2)
            if dist < best_dist and dist < 20:  # Must be within 20 pixels
                best_dist = dist
                best_obj = obj_id

        if best_obj:
            # Check if this gt object is already assigned
            if best_obj not in self.track_to_gt[ft].values():
                self.track_to_gt[ft][track.id] = best_obj

    def _compute_errors(self, ft, frame_idx):
        """Compute tracking errors for this filter type."""
        if not self.ground_truth or frame_idx >= len(self.ground_truth['frames']):
            return

        frame_gt = self.ground_truth['frames'][frame_idx]
        tracker = self.trackers[ft]
        errors = []

        for track in tracker.tracks:
            if track.state != "confirmed":
                continue

            # Associate track with GT if not done yet
            self._associate_track_to_gt(ft, track, frame_idx)

            if track.id not in self.track_to_gt[ft]:
                continue

            gt_obj_id = self.track_to_gt[ft][track.id]
            if gt_obj_id not in frame_gt['objects']:
                continue

            pos = track.get_position()
            if not pos:
                continue

            gt_data = frame_gt['objects'][gt_obj_id]
            gt_x, gt_y = gt_data['x'], gt_data['y']

            error = np.sqrt((pos[0] - gt_x)**2 + (pos[1] - gt_y)**2)
            errors.append(error)

            # Store per-object error
            self.per_object_errors[ft][gt_obj_id].append((frame_idx, error))

        # Store mean error for this frame
        if errors:
            self.error_history[ft].append((frame_idx, np.mean(errors)))

    def _update_error_plots(self):
        """Update the error figure."""
        for ft in FILTER_TYPES:
            ax = self.error_axes[ft]

            # Plot per-object errors
            for obj_id, err_list in self.per_object_errors[ft].items():
                if not err_list:
                    continue

                if obj_id not in self.error_plot_lines[ft]:
                    line, = ax.plot([], [], linewidth=0.8, alpha=0.5)
                    self.error_plot_lines[ft][obj_id] = line

                frames, errors = zip(*err_list)
                self.error_plot_lines[ft][obj_id].set_data(frames, errors)

            # Plot mean error (thicker line)
            if self.error_history[ft]:
                if self.mean_error_line[ft] is None:
                    self.mean_error_line[ft], = ax.plot([], [], color=self.filter_colors[ft],
                                                         linewidth=2, alpha=0.9, label='Mean')
                frames, errors = zip(*self.error_history[ft])
                self.mean_error_line[ft].set_data(frames, errors)

        # Update summary bar chart
        self.ax_summary.clear()
        self.ax_summary.set_facecolor('#0a0a0a')
        self.ax_summary.set_title('Mean Error by Filter', color='#00ff00', fontsize=10)

        mean_errors = []
        colors = []
        labels = []

        for ft in FILTER_TYPES:
            if self.error_history[ft]:
                _, errors = zip(*self.error_history[ft])
                mean_errors.append(np.mean(errors))
            else:
                mean_errors.append(0)
            colors.append(self.filter_colors[ft])
            labels.append(ft.replace(' ', '\n'))

        if any(mean_errors):
            bars = self.ax_summary.bar(range(len(FILTER_TYPES)), mean_errors, color=colors)
            self.ax_summary.set_xticks(range(len(FILTER_TYPES)))
            self.ax_summary.set_xticklabels(labels, fontsize=7, color='#888888')
            self.ax_summary.set_ylabel('Mean Error (px)', color='#888888', fontsize=8)
            self.ax_summary.tick_params(colors='#444444', labelsize=7)

        self.fig_error.canvas.draw_idle()

    def update(self, frame_num):
        """Process one frame."""
        if self.frame_idx >= len(self.frames):
            return []

        frame = self.frames[self.frame_idx]
        current_frame = self.frame_idx
        self.frame_idx += 1

        # Process through all trackers
        all_centroids = {}
        for ft in FILTER_TYPES:
            centroids = self.trackers[ft].process_frame(frame)
            all_centroids[ft] = centroids

            # Compute errors against ground truth
            self._compute_errors(ft, current_frame)

        # Update displays
        self._update_display(frame, all_centroids)

        # Update error plots
        if current_frame % 5 == 0:  # Update every 5 frames for performance
            self._update_error_plots()

        return []

    def _update_display(self, frame, all_centroids):
        """Update visualization."""
        for ft in FILTER_TYPES:
            ax = self.axes[ft]
            tracker = self.trackers[ft]
            centroids = all_centroids[ft]

            # Show frame as background (dim)
            if ft not in self.img_plots:
                self.img_plots[ft] = ax.imshow(frame, cmap='gray', vmin=0, vmax=255, alpha=0.5)
            else:
                self.img_plots[ft].set_data(frame)

            # Clear old detection scatter
            if self.det_scatters[ft]:
                self.det_scatters[ft].remove()

            # Plot detections colored by associated track
            det_colors = []
            det_xs = []
            det_ys = []

            # Map centroids to tracks for coloring
            for cx, cy in centroids:
                det_xs.append(cx)
                det_ys.append(cy)
                # Find which track owns this detection
                color = '#444444'  # Default gray
                for track in tracker.tracks:
                    pos = track.get_position()
                    if pos:
                        dist = np.sqrt((cx - pos[0])**2 + (cy - pos[1])**2)
                        if dist < 15:
                            color = track.color
                            break
                det_colors.append(color)

            if det_xs:
                self.det_scatters[ft] = ax.scatter(det_xs, det_ys, c=det_colors, s=30, marker='o')

            # Update track lines
            active_ids = set()
            for track in tracker.tracks:
                tid = track.id
                active_ids.add(tid)

                if tid not in self.track_lines[ft]:
                    line, = ax.plot([], [], color=track.color, linewidth=1.5, alpha=0.7)
                    self.track_lines[ft][tid] = line

                if len(track.history) > 1:
                    xs, ys = zip(*track.history[-100:])
                    self.track_lines[ft][tid].set_data(xs, ys)
                    alpha = 0.8 if track.state == "confirmed" else 0.3
                    self.track_lines[ft][tid].set_alpha(alpha)

            # Remove old track lines
            old_ids = set(self.track_lines[ft].keys()) - active_ids
            for tid in old_ids:
                self.track_lines[ft][tid].remove()
                del self.track_lines[ft][tid]

        # Update info
        self._update_info()

    def _update_info(self):
        """Update info panel."""
        self.ax_info.clear()
        self.ax_info.set_facecolor('#0a0a0a')
        self.ax_info.axis('off')

        self.ax_info.text(0.5, 0.95, f'Frame {self.frame_idx}/{len(self.frames)}',
                         ha='center', color='#00ff00', fontsize=12,
                         transform=self.ax_info.transAxes)

        y = 0.75
        self.ax_info.text(0.1, y, 'Confirmed Tracks:', color='#888888', fontsize=10,
                         transform=self.ax_info.transAxes)
        y -= 0.08

        for ft in FILTER_TYPES:
            n_conf = len([t for t in self.trackers[ft].tracks if t.state == "confirmed"])
            n_total = len(self.trackers[ft].tracks)
            self.ax_info.text(0.1, y, f"  {ft}: {n_conf}/{n_total}",
                             color='#00aa00', fontsize=9,
                             transform=self.ax_info.transAxes)
            y -= 0.06

    def run(self):
        """Run the demo."""
        self.ani = FuncAnimation(
            self.fig, self.update,
            frames=len(self.frames),
            interval=1000 / self.fps,
            blit=False,
            repeat=False
        )
        plt.tight_layout()
        plt.show()


def main():
    base_dir = os.path.dirname(__file__)
    video_path = os.path.join(base_dir, "radar_scene.mp4")
    gt_path = os.path.join(base_dir, "ground_truth.json")

    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        print("Run 'python generate_scene.py' first to create the video.")
        return

    print("Blob Tracker Demo with Error Analysis")
    print("=" * 40)

    demo = TrackerDemo(video_path, gt_path)
    demo.run()


if __name__ == "__main__":
    main()
