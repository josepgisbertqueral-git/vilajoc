#!/usr/bin/env python3
"""Real-time webcam pose estimation demo.

Tracks 2 people with key joint angles, movement direction and velocity.

Usage:
    python demos/webcam_demo.py [--camera CAMERA_ID]

Controls:
    - Press 'q' to quit
    - Press 's' to save screenshot
"""

import sys
import argparse
from pathlib import Path
import time
import cv2
import socket
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.backends.mediapipe_backend import MediaPipeBackend
from src.core.angle_calculator import AngleCalculator
from src.core.body_movement_tracker import BodyMovementTracker
from src.visualization.skeleton_renderer import SkeletonRenderer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Real-time pose estimation webcam demo')
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID (default: 0)')
    parser.add_argument('--width', type=int, default=1280, help='Frame width (default: 1280)')
    parser.add_argument('--height', type=int, default=720, help='Frame height (default: 720)')
    return parser.parse_args()


def get_direction(velocity_x):
    """Convert X-axis velocity to direction text."""
    if velocity_x > 0.1:
        return "RIGHT"
    elif velocity_x < -0.1:
        return "LEFT"
    return "—"

def detect_squat(pose_result, person_id):
    """Simple squat detection using hip vs knee height."""
    hip = pose_result.get_keypoint("left_hip", person_id)
    knee = pose_result.get_keypoint("left_knee", person_id)

    if hip and knee:
        return hip.y > knee.y  # lower in image = larger y
    return False


def main():
    """Main demo function."""
    args = parse_args()

    print("=" * 60)
    print("Motion Tracker - 2 Person Pose Demo")
    print("=" * 60)
    print(f"Camera: {args.camera} | Resolution: {args.width}x{args.height}")
    print("Controls: 'q' to quit, 's' to save screenshot")
    print("=" * 60 + "\n")

    # Initialize camera
    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not cap.isOpened():
        print(f"Error: Could not open camera {args.camera}")
        return 1

    # Initialize components
    print("Initializing pose estimator...")
    estimator = MediaPipeBackend(
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        num_poses=2,  # Track up to 2 people
    )

    if not estimator.initialize():
        print("Error: Failed to initialize pose estimator")
        return 1

    print(f"[OK] {estimator.backend_name} initialized")
    print("[OK] Tracking up to 2 people\n")

    angle_calculator = AngleCalculator(use_3d=True)
    body_movement_tracker = BodyMovementTracker(buffer_size=30, fps=30.0, use_3d=True)
    renderer = SkeletonRenderer(show_keypoints=True, show_connections=True, show_labels=False)

    # Initialize UDP socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_address = ("127.0.0.1", 4242)
    last_send_time = 0.0

    # Key joints to display
    key_joints = [
        'left_shoulder', 'right_shoulder',
        'left_elbow', 'right_elbow',
        'left_hip', 'right_hip',
        'left_knee', 'right_knee',
    ]

    frame_count = 0
    start_time = time.time()
    screenshot_count = 0

    print("Starting detection... (Press 'q' to quit)\n")
    log_file = open("udp_log.jsonl", "a", buffering=1)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            pose_result = estimator.process_frame(frame)
            
            if pose_result and pose_result.is_valid():
                # Calculate angles and movement
                angles = angle_calculator.calculate_all_angles(pose_result)
                body_movements = body_movement_tracker.update(pose_result)

                # Render skeleton
                frame = renderer.render(frame, pose_result, angles)

                # Display stats for each detected person
                for person_id in range(pose_result.num_people):
                    stats = {'Person': f"#{person_id + 1}"}
                    
                    # Add joint angles
                    if angles:
                        for joint in key_joints:
                            if joint in angles and angles[joint] is not None:
                                angle_val = angles[joint]
                                joint_name = joint.replace('_', ' ').title()
                                joint_name = joint_name.replace('Left', 'L').replace('Right', 'R')
                                stats[joint_name] = f"{angle_val:.0f}°"
                    
                    # Add movement data
                    if person_id in body_movements:
                        movement = body_movements[person_id]
                        stats['Velocity'] = f"{movement.velocity_magnitude:.1f}px/s"
                        stats['Direction'] = get_direction(movement.velocity_x)
                    
                    # Draw stats panel for this person
                    position = 'top_left' if person_id == 0 else 'top_right'
                    frame = renderer.draw_stats_panel(frame, stats, position=position)
            
            else:
                cv2.putText(frame, "No pose detected", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            cv2.imshow('Motion Tracker - 2 Person Demo', frame)

            # Keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                screenshot_count += 1
                filename = f"screenshot_{screenshot_count:03d}.png"
                cv2.imwrite(filename, frame)
                print(f"Saved: {filename}")

            frame_count += 1

            current_time = time.time()

            # Comprovació de seguretat: Només intentar enviar si hi ha resultats vàlids
            if pose_result and pose_result.is_valid() and current_time - last_send_time >= 0.5:
                payload = []

                for person_id in range(pose_result.num_people):
                    # Comprovar que el tracker realment té dades d'aquest ID
                    if 'body_movements' in locals() and person_id in body_movements:
                        movement = body_movements[person_id]

                        velocity = float(movement.velocity_magnitude)
                        direction = get_direction(movement.velocity_x)
                        squat = detect_squat(pose_result, person_id)

                        payload.append({
                            "id": person_id,
                            "velocity": velocity,
                            "direction": direction,
                            "squat": squat
                        })

                if payload:
                    try:
                        udp_sock.sendto(json.dumps(payload).encode(), udp_address)
                        log_file.write(json.dumps({"data": payload}) + "\n")
                    except Exception as e:
                        print(f"Error enviant UDP: {e}")

                last_send_time = current_time

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        elapsed_time = time.time() - start_time
        avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        print("\n" + "=" * 60)
        print(f"Frames: {frame_count} | Duration: {elapsed_time:.1f}s | FPS: {avg_fps:.1f}")
        print("=" * 60)

        cap.release()
        cv2.destroyAllWindows()
        return 0


if __name__ == '__main__':
    sys.exit(main())
