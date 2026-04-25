"""Multi-person body movement tracking for direction and velocity analysis.

This module tracks center of mass, movement velocity, and direction for each person
to enable real-time motion data export for external applications (games, AR, VR).
"""

from typing import Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, asdict
import numpy as np

from .pose_estimator import PoseResult, Keypoint


@dataclass
class BodyMovement:
    """Movement data for a single person."""
    person_id: int
    
    # Position (normalized 0-1 in frame)
    center_x: float
    center_y: float
    center_z: Optional[float] = None  # 3D depth if available
    
    # Velocity in pixels/second (2D) or meters/second (3D)
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    velocity_z: Optional[float] = None  # 3D velocity
    
    # Overall velocity magnitude
    velocity_magnitude: float = 0.0
    
    # Direction in degrees (0-360, where 0=right, 90=down, 180=left, 270=up)
    direction_angle: float = 0.0
    
    # Direction vector (normalized)
    direction_x: float = 0.0
    direction_y: float = 0.0
    direction_z: Optional[float] = None  # 3D direction
    
    # Keypoints used for center calculation
    num_visible_keypoints: int = 0
    
    # Timestamp
    timestamp_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for easy export to JSON/external apps."""
        return asdict(self)
    
    def to_compact_dict(self) -> Dict:
        """Compact format without None values."""
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


class BodyMovementTracker:
    """Track movement direction and velocity for each detected person."""

    # Core keypoints for center of mass calculation (excluding hands/feet for stability)
    CENTER_KEYPOINTS = [
        'nose',
        'left_shoulder', 'right_shoulder',
        'left_hip', 'right_hip',
        'left_elbow', 'right_elbow',
        'left_knee', 'right_knee',
    ]

    def __init__(
        self,
        buffer_size: int = 30,
        fps: float = 30.0,
        use_3d: bool = True,
    ):
        """Initialize body movement tracker.
        
        Args:
            buffer_size: Number of frames to keep in history
            fps: Frames per second for velocity calculation
            use_3d: Use 3D world coordinates if available
        """
        self.buffer_size = buffer_size
        self.fps = fps
        self.use_3d = use_3d
        
        # History buffers per person: person_id -> deque of positions
        self._position_history: Dict[int, deque] = {}
        self._timestamp_history: Dict[int, deque] = {}
        
        self._frame_count = 0

    def update(
        self,
        pose_result: PoseResult,
        timestamp_ms: Optional[float] = None,
    ) -> Dict[int, BodyMovement]:
        """Process frame and calculate movement for all detected people.
        
        Args:
            pose_result: Detection result with one or more people
            timestamp_ms: Frame timestamp in milliseconds
            
        Returns:
            Dictionary mapping person_id -> BodyMovement
        """
        if timestamp_ms is None:
            timestamp_ms = self._frame_count * (1000.0 / self.fps)
        
        self._frame_count += 1
        movements = {}
        
        # Process all detected people
        num_people = pose_result.num_people if hasattr(pose_result, 'num_people') else 1
        
        for person_id in range(num_people):
            # Get keypoints for this person
            if person_id == 0:
                keypoints = pose_result.keypoints
            else:
                keypoints = pose_result.get_person_pose(person_id)
            
            if keypoints is None or len(keypoints) == 0:
                continue
            
            # Calculate center of mass
            center = self._calculate_center_of_mass(keypoints)
            if center is None:
                continue
            
            # Initialize history for new person
            if person_id not in self._position_history:
                self._position_history[person_id] = deque(maxlen=self.buffer_size)
                self._timestamp_history[person_id] = deque(maxlen=self.buffer_size)
            
            # Store current position
            self._position_history[person_id].append(center)
            self._timestamp_history[person_id].append(timestamp_ms)
            
            # Calculate movement
            movement = self._calculate_movement(
                person_id=person_id,
                current_center=center,
                timestamp_ms=timestamp_ms,
            )
            movements[person_id] = movement
        
        return movements

    def _calculate_center_of_mass(
        self,
        keypoints: List[Keypoint],
    ) -> Optional[Tuple[float, float, Optional[float]]]:
        """Calculate center of mass from keypoints.
        
        Returns:
            (center_x, center_y, center_z) or None
        """
        # Get center keypoints
        center_kpts = []
        for kp in keypoints:
            if kp.name in self.CENTER_KEYPOINTS and kp.visibility > 0.3:
                center_kpts.append(kp)
        
        if not center_kpts:
            return None
        
        # Calculate average position
        x_coords = np.array([kp.x for kp in center_kpts])
        y_coords = np.array([kp.y for kp in center_kpts])
        
        center_x = float(np.mean(x_coords))
        center_y = float(np.mean(y_coords))
        
        # 3D position if available
        center_z = None
        if self.use_3d:
            z_coords = [kp.z for kp in center_kpts]
            if all(z is not None for z in z_coords):
                center_z = float(np.mean(z_coords))
        
        return center_x, center_y, center_z

    def _calculate_movement(
        self,
        person_id: int,
        current_center: Tuple[float, float, Optional[float]],
        timestamp_ms: float,
    ) -> BodyMovement:
        """Calculate velocity and direction for a person.
        
        Args:
            person_id: Person identifier
            current_center: (x, y, z) current center position
            timestamp_ms: Current timestamp
            
        Returns:
            BodyMovement with calculated metrics
        """
        current_x, current_y, current_z = current_center
        
        # Initialize movement
        velocity_x = 0.0
        velocity_y = 0.0
        velocity_z = None
        direction_angle = 0.0
        direction_x = 0.0
        direction_y = 0.0
        direction_z = None
        
        # Calculate velocity if history exists
        pos_history = self._position_history[person_id]
        time_history = self._timestamp_history[person_id]
        
        if len(pos_history) >= 2:
            prev_x, prev_y, prev_z = pos_history[-2]
            prev_time = time_history[-2]
            
            # Time delta in seconds
            dt = (timestamp_ms - prev_time) / 1000.0
            if dt > 0:
                # Velocity in normalized units per second
                # (normalized by assuming 30fps ~= motion in 1/30th of frame)
                velocity_x = (current_x - prev_x) / dt
                velocity_y = (current_y - prev_y) / dt
                
                if self.use_3d and current_z is not None and prev_z is not None:
                    velocity_z = (current_z - prev_z) / dt
                
                # Direction angle (in degrees, 0=right, 90=down, 180=left, 270=up)
                direction_angle = self._calculate_direction_angle(velocity_x, velocity_y)
                
                # Direction vector (normalized)
                vel_mag = np.sqrt(velocity_x**2 + velocity_y**2)
                if vel_mag > 1e-6:
                    direction_x = velocity_x / vel_mag
                    direction_y = velocity_y / vel_mag
                    
                    if velocity_z is not None and self.use_3d:
                        vel_mag_3d = np.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
                        if vel_mag_3d > 1e-6:
                            direction_z = velocity_z / vel_mag_3d
        
        # Calculate velocity magnitude
        velocity_magnitude = np.sqrt(velocity_x**2 + velocity_y**2)
        if velocity_z is not None and self.use_3d:
            velocity_magnitude = np.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)
        
        # Count visible keypoints
        num_visible = sum(
            1 for kp in pos_history
            if kp is not None
        )
        
        return BodyMovement(
            person_id=person_id,
            center_x=current_x,
            center_y=current_y,
            center_z=current_z,
            velocity_x=float(velocity_x),
            velocity_y=float(velocity_y),
            velocity_z=velocity_z,
            velocity_magnitude=float(velocity_magnitude),
            direction_angle=float(direction_angle),
            direction_x=float(direction_x),
            direction_y=float(direction_y),
            direction_z=direction_z,
            num_visible_keypoints=len(pos_history),
            timestamp_ms=timestamp_ms,
        )

    @staticmethod
    def _calculate_direction_angle(vx: float, vy: float) -> float:
        """Calculate direction angle in degrees.
        
        Returns angle 0-360 where:
        - 0° = moving right
        - 90° = moving down
        - 180° = moving left
        - 270° = moving up
        """
        angle_rad = np.arctan2(vy, vx)
        angle_deg = np.degrees(angle_rad)
        # Normalize to 0-360
        if angle_deg < 0:
            angle_deg += 360
        return float(angle_deg)

    def get_latest_movement(
        self,
        person_id: int,
    ) -> Optional[BodyMovement]:
        """Get the most recent movement data for a person.
        
        Args:
            person_id: Person identifier
            
        Returns:
            BodyMovement or None if person not tracked
        """
        if person_id not in self._position_history:
            return None
        
        pos_history = self._position_history[person_id]
        time_history = self._timestamp_history[person_id]
        
        if not pos_history:
            return None
        
        current_center = pos_history[-1]
        current_time = time_history[-1]
        
        return self._calculate_movement(person_id, current_center, current_time)

    def get_all_movements(self) -> Dict[int, BodyMovement]:
        """Get current movement data for all tracked people.
        
        Returns:
            Dictionary mapping person_id -> BodyMovement
        """
        movements = {}
        for person_id in self._position_history:
            movement = self.get_latest_movement(person_id)
            if movement is not None:
                movements[person_id] = movement
        return movements

    def get_movements_json(self) -> Dict:
        """Get all movements as JSON-serializable dictionary.
        
        Useful for exporting to external applications (games, etc).
        """
        movements = self.get_all_movements()
        return {
            'timestamp_ms': int(self._frame_count * 1000.0 / self.fps),
            'frame_number': self._frame_count,
            'num_people': len(movements),
            'people': {
                str(pid): movement.to_dict()
                for pid, movement in movements.items()
            }
        }

    def clear(self):
        """Clear all tracking history."""
        self._position_history.clear()
        self._timestamp_history.clear()
        self._frame_count = 0

    def set_fps(self, fps: float):
        """Update FPS for velocity calculations."""
        self.fps = fps
