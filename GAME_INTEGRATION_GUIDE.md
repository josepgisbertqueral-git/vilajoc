# Body Movement Data Export for Game Integration

## Overview

The motion tracker now exports real-time body movement data for each detected person, making it easy to integrate with external game engines (Unity, Unreal, Godot, etc.).

**Available data per person:**
- ✅ Center of mass position (X, Y, Z)
- ✅ Velocity in each direction (X, Y, Z components)
- ✅ Overall velocity magnitude
- ✅ Movement direction angle (0-360°)
- ✅ Normalized direction vector

---

## Quick Start

### 1. Run the Export Demo

```bash
python demos/export_movement_data.py --output movement_data.json
```

**Output:** JSON file with real-time movement data for all detected people

### 2. Use in Your Python Code

```python
from src.core.body_movement_tracker import BodyMovementTracker

# Initialize tracker
tracker = BodyMovementTracker(buffer_size=30, fps=30.0, use_3d=True)

# Process frame
pose_result = estimator.process_frame(frame)
body_movements = tracker.update(pose_result)

# Access movement data for each person
for person_id, movement in body_movements.items():
    print(f"Person {person_id}:")
    print(f"  Position: ({movement.center_x:.2f}, {movement.center_y:.2f})")
    print(f"  Velocity: {movement.velocity_magnitude:.2f} px/s")
    print(f"  Direction: {movement.direction_angle:.0f}°")
    
    # Export to external game
    game_data = movement.to_dict()
```

---

## Data Structure

### BodyMovement Class

```python
@dataclass
class BodyMovement:
    person_id: int
    
    # Position (normalized 0-1 in frame, or meters in 3D)
    center_x: float
    center_y: float
    center_z: Optional[float]
    
    # Velocity (pixels/second or meters/second)
    velocity_x: float
    velocity_y: float
    velocity_z: Optional[float]
    velocity_magnitude: float
    
    # Direction
    direction_angle: float      # 0-360°
    direction_x: float          # Normalized
    direction_y: float          # Normalized
    direction_z: Optional[float]
    
    # Metadata
    num_visible_keypoints: int
    timestamp_ms: float
```

### JSON Export Format

```json
{
  "metadata": {
    "total_frames": 1500,
    "total_data_points": 1500,
    "duration_seconds": 50.0,
    "fps": 30,
    "resolution": {"width": 1280, "height": 720}
  },
  "data": [
    {
      "frame": 0,
      "timestamp_ms": 0,
      "people": {
        "0": {
          "center": {"x": 0.5123, "y": 0.6234, "z": 0.1234},
          "velocity": {
            "x": 12.34,
            "y": -5.67,
            "z": 0.12,
            "magnitude": 13.45
          },
          "direction": {
            "angle_deg": 45.2,
            "x": 0.7071,
            "y": -0.7071,
            "z": 0.0
          }
        },
        "1": {
          "center": {"x": 0.3456, "y": 0.4567, "z": 0.0987},
          "velocity": {...}
        }
      }
    }
  ]
}
```

---

## Usage Examples

### Example 1: Real-time Movement Display

```python
from src.core.body_movement_tracker import BodyMovementTracker

tracker = BodyMovementTracker(use_3d=True)

while video_playing:
    pose = estimator.process_frame(frame)
    movements = tracker.update(pose)
    
    for person_id, mvt in movements.items():
        print(f"Person {person_id}:")
        print(f"  Speed: {mvt.velocity_magnitude:.2f} px/s")
        print(f"  Direction: {mvt.direction_angle:.0f}°")
        print(f"  Position: ({mvt.center_x:.3f}, {mvt.center_y:.3f})")
```

### Example 2: Game Event Trigger

```python
# Trigger game action based on movement
if movement.velocity_magnitude > 100:  # Fast movement
    emit_game_event('player_running', {
        'person_id': movement.person_id,
        'speed': movement.velocity_magnitude,
        'direction': movement.direction_angle,
    })
```

### Example 3: Export to External Game (UDP Socket)

```python
import socket
import json

def send_to_game(movement, game_host='127.0.0.1', game_port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = json.dumps(movement.to_dict()).encode()
    sock.sendto(data, (game_host, game_port))
    sock.close()

# Send each person's movement to game
for person_id, movement in movements.items():
    send_to_game(movement)
```

### Example 4: Game Integration with Buffering

```python
from src.core.body_movement_tracker import BodyMovementTracker

tracker = BodyMovementTracker(buffer_size=30)

# Get all current movements
while True:
    pose = estimator.process_frame(frame)
    movements = tracker.update(pose)
    
    # Get compact JSON for all people
    json_data = tracker.get_movements_json()
    
    # Send to game
    send_to_game_server(json_data)
```

---

## Integration with Game Engines

### Unity Example

```csharp
using UnityEngine;
using System.Collections.Generic;

public class MotionTrackerInput : MonoBehaviour
{
    private Dictionary<int, PlayerController> players = new();
    
    public void UpdateFromMotionData(string jsonData)
    {
        var data = JsonUtility.FromJson<MotionData>(jsonData);
        
        foreach (var person in data.people.Values)
        {
            if (!players.ContainsKey(person.person_id))
            {
                players[person.person_id] = SpawnPlayer(person.person_id);
            }
            
            var player = players[person.person_id];
            
            // Update position (map normalized to world space)
            player.position = new Vector3(
                (person.center.x - 0.5f) * 10,  // Scale to world
                person.center.y * 5,
                person.center.z ?? 0
            );
            
            // Update velocity
            player.velocity = new Vector3(
                person.velocity.x / 100f,
                person.velocity.y / 100f,
                person.velocity.z ?? 0 / 100f
            );
            
            // Update animation based on movement
            float speed = person.velocity.magnitude;
            if (speed > 50)
                player.animator.SetTrigger("Run");
            else if (speed > 10)
                player.animator.SetTrigger("Walk");
            else
                player.animator.SetTrigger("Idle");
        }
    }
}
```

### Unreal Engine Example (Blueprint Friendly)

```cpp
void AMotionTrackerPlayer::UpdateMovement(const FVector Center, 
                                         const FVector Velocity, 
                                         float DirectionAngle)
{
    // Update character position
    SetActorLocation(FVector(
        (Center.X - 0.5f) * 1000,  // Scale to Unreal units
        (Center.Y - 0.5f) * 1000,
        0
    ));
    
    // Update velocity
    GetCharacterMovement()->Velocity = FVector(
        Velocity.X * 100,
        Velocity.Y * 100,
        0
    );
    
    // Rotate based on direction
    FRotator NewRotation = FRotator::ZeroRotator;
    NewRotation.Yaw = DirectionAngle;
    SetActorRotation(NewRotation);
}
```

---

## Direction Angles Reference

Direction is calculated as angle from positive X-axis (standard math convention):

```
        270°
         ↑
    180° ← → 0°
         ↓
        90°

Examples:
- Moving right: 0°
- Moving down-right: 45°
- Moving down: 90°
- Moving down-left: 135°
- Moving left: 180°
- Moving up-left: 225°
- Moving up: 270°
- Moving up-right: 315°
```

---

## Coordinate Systems

### 2D Coordinates (Image Space)
- **X range:** 0.0 - 1.0 (left to right)
- **Y range:** 0.0 - 1.0 (top to bottom)
- **Velocity:** pixels per second

### 3D Coordinates (World Space)
- **X range:** -∞ to +∞ (meters, relative to camera)
- **Y range:** -∞ to +∞ (meters)
- **Z range:** -∞ to +∞ (meters, depth)
- **Velocity:** meters per second

---

## Performance Tips

1. **Use compact format for network:**
   ```python
   compact_data = movement.to_compact_dict()  # Removes None values
   ```

2. **Reduce tracking buffer for lower latency:**
   ```python
   tracker = BodyMovementTracker(buffer_size=10)  # Smaller = faster but jitterier
   ```

3. **Adjust FPS to match your game:**
   ```python
   tracker = BodyMovementTracker(fps=60)  # Match your target FPS
   ```

4. **Export only key frames:**
   ```python
   if frame_count % 3 == 0:  # Every 3rd frame
       send_to_game(movements)
   ```

---

## Testing Your Integration

### 1. Save movement data
```bash
python demos/export_movement_data.py --output test_data.json
```

### 2. Check the JSON format
```bash
head -100 test_data.json
```

### 3. Verify all people are captured
```python
import json
with open('test_data.json') as f:
    data = json.load(f)
    print(f"Total frames: {len(data['data'])}")
    print(f"People detected: {set(p for frame in data['data'] for p in frame['people'].keys())}")
```

---

## Troubleshooting

### Movement seems jittery
- **Solution:** Increase buffer_size (more smoothing but higher latency)
  ```python
  tracker = BodyMovementTracker(buffer_size=60)
  ```

### Velocity values too large/small
- **Check FPS setting:** Must match your actual frame rate
  ```python
  tracker.set_fps(30)  # Or whatever your actual FPS is
  ```

### Missing person's data
- **Check visibility:** Person may be partially off-screen
- **Check confidence:** Lower min_detection_confidence in backend

### Coordinates not matching game world
- **Scale appropriately:** Map normalized (0-1) to your world units
  ```python
  world_x = (movement.center_x - 0.5) * world_width
  world_y = (movement.center_y - 0.5) * world_height
  ```

---

## Files

- **Tracker:** `src/core/body_movement_tracker.py`
- **Demo:** `demos/export_movement_data.py`
- **Integration:** See examples above for game engines

---

## Next Steps

1. Run `export_movement_data.py` to collect sample data
2. Review the JSON format in output file
3. Integrate with your game engine using provided examples
4. Adjust buffer_size and fps for your needs
5. Test with multiple people

---

**Ready to export movement data to your game!** 🎮
