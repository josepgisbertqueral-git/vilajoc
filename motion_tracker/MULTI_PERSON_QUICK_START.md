# Quick Start: Multi-Person Detection

## TL;DR - What Changed?

✅ **Your motion tracker now detects up to 2 people at the same time (configurable to 4)**

## Quick Examples

### 1. Run the demo (detects 2 people by default)
```bash
python demos/webcam_demo.py
```

### 2. Detect more people
```python
from src.backends.mediapipe_backend import MediaPipeBackend

# Detect up to 3 people
estimator = MediaPipeBackend(num_poses=3)
estimator.initialize()

pose_result = estimator.process_frame(frame)
print(f"Found {pose_result.num_people} people")
```

### 3. Access each person's data
```python
# Get primary person (backward compatible)
main_person = pose_result.keypoints

# Get specific person
person_2_keypoints = pose_result.get_person_pose(1)  # person_id=1 is 2nd person

# Get keypoint for specific person
left_elbow_person1 = pose_result.get_keypoint('left_elbow', person_id=1)
```

### 4. Skeleton colors
- **Green** = Person 1
- **Blue** = Person 2
- **Orange** = Person 3
- **Cyan** = Person 4

## Key Changes

| File | Change |
|------|--------|
| `pose_estimator.py` | Added `keypoints_list` and `num_people` to `PoseResult` |
| `mediapipe_backend.py` | Changed `num_poses=1` → configurable parameter (default 2) |
| `skeleton_renderer.py` | Added multi-color skeleton rendering + `_draw_*_multi()` methods |
| `webcam_demo.py` | Updated to `num_poses=2` and show people count |

## Backward Compatible ✓

All existing code works unchanged - `pose_result.keypoints` still works for single person.

## Performance

- MediaPipe supports 1-4 people
- Adding more people = more latency (~5-10ms per person)
- Model complexity, resolution, and confidence affect FPS

---

**Full guide:** See `MULTI_PERSON_DETECTION.md`
