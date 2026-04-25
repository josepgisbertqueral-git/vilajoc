#!/usr/bin/env python3
"""Export body movement data to JSON for external game integration.

This demo shows how to continuously export real-time movement data
(position, velocity, direction) for each detected person.

Output format is JSON that can be consumed by game engines (Unity, Unreal, etc).

Usage:
    python demos/export_movement_data.py [--output FILE] [--camera CAMERA_ID]
    
Controls:
    - Press 'q' to quit
    - Press 's' to save screenshot
"""

import sys
import argparse
from pathlib import Path
import time
import json
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backends.mediapipe_backend import MediaPipeBackend
from src.core.body_movement_tracker import BodyMovementTracker
from src.visualization.skeleton_renderer import SkeletonRenderer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Export body movement data for game integration')
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device ID (default: 0)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='movement_data.json',
        help='Output JSON file (default: movement_data.json)'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=1280,
        help='Camera frame width (default: 1280)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=720,
        help='Camera frame height (default: 720)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Target FPS (default: 30)'
    )
    return parser.parse_args()


def main():
    """Main export function."""
    args = parse_args()

    print("=" * 70)
    print("Body Movement Data Export - Game Integration")
    print("=" * 70)
    print(f"Camera ID: {args.camera}")
    print(f"Resolution: {args.width}x{args.height}")
    print(f"Output file: {args.output}")
    print("\nControls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save screenshot")
    print("=" * 70)

    # Initialize camera
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not cap.isOpened():
        print(f"Error: Could not open camera {args.camera}")
        return 1

    # Initialize pose estimator (detect 2 people)
    print("\nInitializing pose estimator...")
    estimator = MediaPipeBackend(
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        num_poses=2,
    )

    if not estimator.initialize():
        print("Error: Failed to initialize pose estimator")
        return 1

    print(f"[OK] Initialized {estimator.backend_name} backend")

    # Initialize body movement tracker
    body_movement_tracker = BodyMovementTracker(
        buffer_size=30,
        fps=args.fps,
        use_3d=True,
    )

    # Initialize renderer
    renderer = SkeletonRenderer(
        show_keypoints=True,
        show_connections=True,
        show_labels=False,
    )

    # Data collection
    frame_count = 0
    start_time = time.time()
    screenshot_count = 0
    movement_data_history = []
    fps_history = []

    print("\nStarting data export (press 'q' to quit)...\n")

    try:
        while True:
            loop_start = time.time()

            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            # Process pose
            pose_result = estimator.process_frame(frame)

            if pose_result and pose_result.is_valid():
                # Get body movement data
                body_movements = body_movement_tracker.update(pose_result)

                # Render skeleton
                frame = renderer.render(frame, pose_result)

                # Collect movement data for all people
                frame_data = {
                    'frame': frame_count,
                    'timestamp_ms': body_movement_tracker._frame_count * (1000.0 / args.fps),
                    'people': {}
                }

                for person_id, movement in body_movements.items():
                    frame_data['people'][int(person_id)] = {
                        'center': {
                            'x': round(movement.center_x, 4),
                            'y': round(movement.center_y, 4),
                            'z': round(movement.center_z, 4) if movement.center_z else None,
                        },
                        'velocity': {
                            'x': round(movement.velocity_x, 4),
                            'y': round(movement.velocity_y, 4),
                            'z': round(movement.velocity_z, 4) if movement.velocity_z else None,
                            'magnitude': round(movement.velocity_magnitude, 4),
                        },
                        'direction': {
                            'angle_deg': round(movement.direction_angle, 2),
                            'x': round(movement.direction_x, 4),
                            'y': round(movement.direction_y, 4),
                            'z': round(movement.direction_z, 4) if movement.direction_z else None,
                        },
                    }

                movement_data_history.append(frame_data)

                # Display current data on frame
                stats = {
                    'Frame': str(frame_count),
                    'People': str(pose_result.num_people),
                }

                # Add person 0 movement data
                if 0 in body_movements:
                    mvt = body_movements[0]
                    stats['P0 Speed'] = f"{mvt.velocity_magnitude:.2f}px/s"
                    stats['P0 Direction'] = f"{mvt.direction_angle:.0f}°"
                    stats['P0 Pos'] = f"({mvt.center_x:.2f}, {mvt.center_y:.2f})"

                # Add person 1 movement data if available
                if 1 in body_movements:
                    mvt = body_movements[1]
                    stats['P1 Speed'] = f"{mvt.velocity_magnitude:.2f}px/s"
                    stats['P1 Direction'] = f"{mvt.direction_angle:.0f}°"

                # Calculate and display FPS
                current_fps = 1.0 / (time.time() - loop_start + 1e-6)
                fps_history.append(current_fps)
                if len(fps_history) > 30:
                    fps_history.pop(0)
                avg_fps = np.mean(fps_history)
                stats['FPS'] = f"{avg_fps:.1f}"

                frame = renderer.draw_stats_panel(frame, stats, position='top_left')

            else:
                cv2.putText(
                    frame,
                    "No pose detected",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2,
                )

            # Display frame
            cv2.imshow('Movement Data Export', frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\nQuitting and saving data...")
                break
            elif key == ord('s'):
                screenshot_count += 1
                filename = f"export_screenshot_{screenshot_count:03d}.png"
                cv2.imwrite(filename, frame)
                print(f"Screenshot saved: {filename}")

            frame_count += 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        # Save collected data to JSON file
        print(f"\nSaving movement data to {args.output}...")

        output_data = {
            'metadata': {
                'total_frames': frame_count,
                'total_data_points': len(movement_data_history),
                'start_time': start_time,
                'duration_seconds': time.time() - start_time,
                'fps': args.fps,
                'resolution': {
                    'width': args.width,
                    'height': args.height,
                }
            },
            'data': movement_data_history
        }

        try:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"[OK] Data saved to {args.output}")
            print(f"[OK] Total frames: {frame_count}")
            print(f"[OK] Total duration: {time.time() - start_time:.1f}s")
        except Exception as e:
            print(f"Error saving file: {e}")
            return 1

        # Print sample of the data format
        if movement_data_history:
            print("\nSample data format (first frame):")
            print(json.dumps(movement_data_history[0], indent=2))

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        estimator.release()

    return 0


if __name__ == '__main__':
    sys.exit(main())
