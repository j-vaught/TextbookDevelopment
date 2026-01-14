#!/usr/bin/env python3
"""
Scene Generator - Creates MP4 video of moving blobs and speckle noise.

Outputs:
- MP4 video (binary black/white)
- JSON file with ground truth positions per frame
"""

import numpy as np
import cv2
import json
import os


class Blob:
    """A moving blob in the scene."""

    def __init__(self, x, y, vx, vy, radius=4, turn_rate=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.turn_rate = turn_rate

    def update(self):
        """Move the blob one frame."""
        if abs(self.turn_rate) > 0.001:
            speed = np.sqrt(self.vx**2 + self.vy**2)
            heading = np.arctan2(self.vy, self.vx)
            heading += self.turn_rate
            self.vx = speed * np.cos(heading)
            self.vy = speed * np.sin(heading)

        self.x += self.vx
        self.y += self.vy

    def render(self, frame, pd=0.9):
        """Render blob onto frame with probability of detection."""
        if np.random.random() > pd:
            return  # Missed detection

        h, w = frame.shape[:2]
        cv2.circle(frame, (int(self.x), int(self.y)), int(self.radius), 255, -1)


def generate_video(
    output_path,
    ground_truth_path,
    width=400,
    height=400,
    n_frames=300,
    fps=15,
    n_blobs=10,
    speckle_density=0.003,
    blob_pd=0.85,
    seed=42
):
    """
    Generate MP4 video with moving blobs and speckle noise.
    Also saves ground truth positions to JSON.
    """
    np.random.seed(seed)

    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=False)

    # Ground truth storage
    ground_truth = {
        "metadata": {
            "width": width,
            "height": height,
            "n_frames": n_frames,
            "fps": fps,
            "n_blobs": n_blobs,
            "seed": seed
        },
        "objects": {},
        "frames": []
    }

    # Create blobs
    blobs = []
    for i in range(n_blobs):
        blob_id = f"blob_{i}"
        edge = np.random.randint(4)
        if edge == 0:  # Top
            x = np.random.uniform(50, width - 50)
            y = 30
            vx = np.random.uniform(-2, 2)
            vy = np.random.uniform(1, 3)
        elif edge == 1:  # Bottom
            x = np.random.uniform(50, width - 50)
            y = height - 30
            vx = np.random.uniform(-2, 2)
            vy = np.random.uniform(-3, -1)
        elif edge == 2:  # Left
            x = 30
            y = np.random.uniform(50, height - 50)
            vx = np.random.uniform(1, 3)
            vy = np.random.uniform(-2, 2)
        else:  # Right
            x = width - 30
            y = np.random.uniform(50, height - 50)
            vx = np.random.uniform(-3, -1)
            vy = np.random.uniform(-2, 2)

        turn_rate = 0.0
        maneuvering = False
        if np.random.random() < 0.4:
            turn_rate = np.random.uniform(-0.03, 0.03)
            maneuvering = True

        radius = np.random.uniform(4, 8)
        blobs.append((blob_id, Blob(x, y, vx, vy, radius, turn_rate)))

        # Store object metadata
        ground_truth["objects"][blob_id] = {
            "radius": float(radius),
            "maneuvering": maneuvering,
            "initial_position": [float(x), float(y)],
            "initial_velocity": [float(vx), float(vy)]
        }

    # Generate frames
    for f in range(n_frames):
        frame = np.zeros((height, width), dtype=np.uint8)
        frame_gt = {"frame": f, "objects": {}}

        # Add speckle noise
        n_speckles = int(width * height * speckle_density)
        speckle_x = np.random.randint(0, width, n_speckles)
        speckle_y = np.random.randint(0, height, n_speckles)
        frame[speckle_y, speckle_x] = 255

        # Render blobs and record ground truth
        for blob_id, blob in blobs:
            # Record true position before rendering (which may miss)
            frame_gt["objects"][blob_id] = {
                "x": float(blob.x),
                "y": float(blob.y),
                "vx": float(blob.vx),
                "vy": float(blob.vy),
                "visible": True  # Will update if outside bounds
            }

            blob.render(frame, pd=blob_pd)
            blob.update()

            # Bounce at edges
            if blob.x < 20 or blob.x >= width - 20:
                blob.vx *= -1
                blob.x = np.clip(blob.x, 20, width - 21)
            if blob.y < 20 or blob.y >= height - 20:
                blob.vy *= -1
                blob.y = np.clip(blob.y, 20, height - 21)

        ground_truth["frames"].append(frame_gt)
        out.write(frame)

        if (f + 1) % 50 == 0:
            print(f"  Generated frame {f + 1}/{n_frames}")

    out.release()
    print(f"Saved video: {output_path}")

    # Save ground truth JSON
    with open(ground_truth_path, 'w') as f:
        json.dump(ground_truth, f, indent=2)
    print(f"Saved ground truth: {ground_truth_path}")


def main():
    print("Generating radar scene video...")
    print("=" * 40)

    base_dir = os.path.dirname(__file__)
    video_path = os.path.join(base_dir, "radar_scene.mp4")
    gt_path = os.path.join(base_dir, "ground_truth.json")

    generate_video(
        output_path=video_path,
        ground_truth_path=gt_path,
        width=400,
        height=400,
        n_frames=300,
        fps=15,
        n_blobs=10,
        speckle_density=0.003,
        blob_pd=0.85,
        seed=123
    )

    print()
    print(f"Video: {video_path}")
    print(f"Ground truth: {gt_path}")
    print()
    print("Run 'python tracker_demo.py' to track the blobs")


if __name__ == "__main__":
    main()
