# Multi-Person Detection Guide

## Overview
Your motion tracker has been updated to detect **up to 2 (or more) people simultaneously** instead of just one. This guide explains the changes and how to use the new multi-person detection feature.

## Changes Made

### 1. **Core Data Structure** (`src/core/pose_estimator.py`)
- Modified `PoseResult` class to store multiple people's keypoints:
  - `keypoints_list`: List of keypoint lists for multiple people
  - `num_people`: Number of people detected
  - Updated `get_keypoint()` and `get_keypoints_by_names()` to accept `person_id` parameter
  - Added `get_person_pose()` method to retrieve a specific person's keypoints

**Backward Compatible:** Single-person code still works - `pose_result.keypoints` returns the primary person's keypoints.

### 2. **MediaPipe Backend** (`src/backends/mediapipe_backend.py`)
- Added `num_poses` parameter to `__init__()` (default: 2)
- Changed hardcoded `num_poses=1` to use configurable value
- Updated `process_frame()` to:
  - Process all detected poses, not just the first one
  - Return all poses in `keypoints_list`
  - Maintain backward compatibility by storing first person in `keypoints`

**Usage Example:**
```python
estimator = MediaPipeBackend(num_poses=2)  # Detect up to 2 people
estimator.initialize()
pose_result = estimator.process_frame(frame)

print(f"Detected {pose_result.num_people} people")
if pose_result.num_people > 1:
    for person_id, keypoints in enumerate(pose_result.keypoints_list):
        print(f"Person {person_id}: {len(keypoints)} keypoints")
```

### 3. **Skeleton Renderer** (`src/visualization/skeleton_renderer.py`)
- Added multi-person color scheme:
  - Person 1: Green (0, 255, 0)
  - Person 2: Blue (255, 0, 0)
  - Person 3: Orange (0, 165, 255)
  - Person 4: Cyan (255, 255, 0)
- Updated `render()` to handle multiple people:
  - Automatically detects multiple people and draws them with different colors
  - Added `_draw_keypoints_multi()` and `_draw_connections_multi()` methods
- Single-person rendering still works as before

### 4. **Webcam Demo** (`demos/webcam_demo.py`)
- Updated `MediaPipeBackend` initialization to use `num_poses=2`
- Added "People Detected" display in the statistics panel

## How to Use

### Basic Usage (Automatically Detects 2 People)
```bash
python demos/webcam_demo.py
```

The demo will now:
- ✅ Display skeletons for up to 2 people
- ✅ Use different colors for each person
- ✅ Show "People Detected: X" in the statistics panel
- ✅ Work exactly like before if only 1 person is in frame

### Advanced Usage (Custom Number of People)

Change the number of detected people in any of your scripts:

```python
from src.backends.mediapipe_backend import MediaPipeBackend

# Detect up to 3 people
estimator = MediaPipeBackend(num_poses=3)
estimator.initialize()

pose_result = estimator.process_frame(frame)

# Process all detected people
if pose_result and pose_result.num_people > 0:
    print(f"Detected {pose_result.num_people} people")
    
    # Access individual people
    for person_id in range(pose_result.num_people):
        person_keypoints = pose_result.get_person_pose(person_id)
        print(f"Person {person_id} has {len(person_keypoints)} keypoints")
        
        # Get specific keypoint for this person
        left_elbow = pose_result.get_keypoint('left_elbow', person_id=person_id)
        if left_elbow:
            print(f"Person {person_id} left elbow: ({left_elbow.x}, {left_elbow.y})")
```

### Working with Multiple People in Analysis

The `AngleCalculator` and `MotionAnalyzer` work with the first person by default:

```python
from src.core.angle_calculator import AngleCalculator
from src.core.motion_analyzer import MotionAnalyzer

angle_calc = AngleCalculator()
motion_analyzer = MotionAnalyzer()

pose_result = estimator.process_frame(frame)

if pose_result.num_people >= 2:
    # Analyze first person
    angles_person1 = angle_calc.calculate_all_angles(pose_result)
    motion_analyzer.update(pose_result)
    
    # Analyze second person separately
    person2_pose = PoseResult(
        keypoints=pose_result.get_person_pose(1),
        confidence=pose_result.confidence,
        image_width=pose_result.image_width,
        image_height=pose_result.image_height,
    )
    angles_person2 = angle_calc.calculate_all_angles(person2_pose)
```

## MediaPipe Limits

- MediaPipe can detect **up to 4 people** (`num_poses` parameter supports 1-4)
- Performance scales with number of people (detecting 4 people is slower than 1)
- Each additional person adds ~5-10ms latency depending on complexity

## Performance Tips

1. **Adjust confidence thresholds** for stricter/looser detection:
   ```python
   estimator = MediaPipeBackend(
       num_poses=2,
       min_detection_confidence=0.6,  # Higher = stricter
       min_tracking_confidence=0.5
   )
   ```

2. **Reduce model complexity** if FPS is too low:
   ```python
   estimator = MediaPipeBackend(
       model_complexity=0,  # 0=lite, 1=full (default), 2=heavy
       num_poses=2
   )
   ```

3. **Lower camera resolution** to increase FPS:
   ```bash
   python demos/webcam_demo.py --width 640 --height 480
   ```

## Backward Compatibility

✅ All existing code continues to work without changes:
- Single-person analysis code works as-is
- `pose_result.keypoints` still contains primary person's keypoints
- Rendering automatically handles both single and multi-person cases

## Testing

Run the webcam demo with 2+ people in frame:
```bash
python demos/webcam_demo.py
```

You should see:
- Green skeleton for person 1
- Blue skeleton for person 2
- "People Detected: 2" in the stats panel
- Different colored connections for each person

## Files Modified

1. `src/core/pose_estimator.py` - Added multi-person support to PoseResult
2. `src/backends/mediapipe_backend.py` - Changed num_poses to configurable parameter
3. `src/visualization/skeleton_renderer.py` - Added multi-color skeleton rendering
4. `demos/webcam_demo.py` - Updated to use num_poses=2 and display people count

## Next Steps

To customize for your use case:

1. **Increase people limit:** Change `num_poses=2` to `num_poses=3` or `num_poses=4`
2. **Adjust colors:** Edit `COLORS` dict in `skeleton_renderer.py`
3. **Analyze individual people:** Use `pose_result.get_person_pose(person_id)`
4. **Add per-person metrics:** Create separate MotionAnalyzer instances per person

---

**Questions?** Check the demo files or explore the updated class definitions!
