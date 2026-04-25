"""Pickleball standard action templates and detection logic."""

from typing import Dict, List, Optional, Tuple
from ...core.sport_analyzer import ActionTemplate


class PickleballActions:
    """Library of standard pickleball action templates.

    Each template defines key joints and ideal angle ranges for a specific
    stroke or movement.
    """

    # Key joints for pickleball analysis
    RACKET_ARM_JOINTS = [
        'right_shoulder', 'right_elbow', 'right_wrist',
    ]
    NON_RACKET_ARM_JOINTS = [
        'left_shoulder', 'left_elbow', 'left_wrist',
    ]
    LOWER_BODY_JOINTS = [
        'left_hip', 'right_hip', 'left_knee', 'right_knee',
        'left_ankle', 'right_ankle',
    ]
    ALL_KEY_JOINTS = RACKET_ARM_JOINTS + NON_RACKET_ARM_JOINTS + LOWER_BODY_JOINTS

    @classmethod
    def ready_stance(cls) -> ActionTemplate:
        """Basic ready position, leaning forward slightly, paddle up."""
        return ActionTemplate(
            name='ready_stance',
            description='准备姿势 - 双脚分开，屈膝，球拍置于胸前',
            key_joints=cls.ALL_KEY_JOINTS,
            ideal_angles={
                'right_knee': (110.0, 150.0),     # bent knees
                'left_knee': (110.0, 150.0),      # bent knees
                'right_hip': (120.0, 160.0),      # forward lean
                'left_hip': (120.0, 160.0),
                'right_shoulder': (20.0, 70.0),   # arms forward/up
                'left_shoulder': (20.0, 70.0),
                'right_elbow': (80.0, 130.0),     # arms ready, not fully straight
                'left_elbow': (80.0, 130.0),
            },
        )

    @classmethod
    def dink_forehand(cls) -> ActionTemplate:
        """Forehand dink, typically at the kitchen line."""
        return ActionTemplate(
            name='dink_forehand',
            description='正手推挡(Dink) - 靠近网前的柔和击球',
            key_joints=cls.RACKET_ARM_JOINTS + ['right_hip', 'right_knee'],
            ideal_angles={
                'right_shoulder': (20.0, 60.0),   # arm low
                'right_elbow': (130.0, 170.0),    # mostly extended, but soft
                'right_knee': (110.0, 150.0),     # staying low
                'right_hip': (120.0, 160.0),      # staying low
            },
        )

    @classmethod
    def dink_backhand(cls) -> ActionTemplate:
        """Backhand dink."""
        return ActionTemplate(
            name='dink_backhand',
            description='反手推挡(Dink) - 靠近网前的柔和反手击球',
            key_joints=cls.RACKET_ARM_JOINTS + ['left_hip', 'left_knee'],
            ideal_angles={
                'right_shoulder': (20.0, 60.0),   # arm low, reaching across
                'right_elbow': (130.0, 170.0),    # mostly extended
                'left_knee': (110.0, 150.0),      # staying low
            },
        )

    @classmethod
    def drive_forehand(cls) -> ActionTemplate:
        """Forehand drive/groundstroke."""
        return ActionTemplate(
            name='drive_forehand',
            description='正手抽球(Drive) - 有力量的底线正手击球',
            key_joints=cls.RACKET_ARM_JOINTS + ['right_hip'],
            ideal_angles={
                'right_shoulder': (50.0, 110.0),   # arm swinging through
                'right_elbow': (130.0, 180.0),     # extended through contact
                'right_hip': (140.0, 180.0),       # body rotating/extending up
            },
        )

    @classmethod
    def drive_backhand(cls) -> ActionTemplate:
        """Backhand drive/groundstroke."""
        return ActionTemplate(
            name='drive_backhand',
            description='反手抽球(Drive) - 有力量的底线反手击球',
            key_joints=cls.RACKET_ARM_JOINTS + ['left_hip'],
            ideal_angles={
                'right_shoulder': (40.0, 100.0),   # arm sweeping across
                'right_elbow': (130.0, 180.0),     # extended
                'left_hip': (140.0, 180.0),        # body rotating
            },
        )

    @classmethod
    def volley_forehand(cls) -> ActionTemplate:
        """Forehand punch volley."""
        return ActionTemplate(
            name='volley_forehand',
            description='正手截击(Volley) - 不落地直接击球',
            key_joints=cls.RACKET_ARM_JOINTS,
            ideal_angles={
                'right_shoulder': (70.0, 120.0),   # paddle higher than dink
                'right_elbow': (110.0, 160.0),     # punch motion
            },
        )

    @classmethod
    def volley_backhand(cls) -> ActionTemplate:
        """Backhand punch volley."""
        return ActionTemplate(
            name='volley_backhand',
            description='反手截击(Volley) - 不落地直接反手击球',
            key_joints=cls.RACKET_ARM_JOINTS,
            ideal_angles={
                'right_shoulder': (70.0, 120.0),
                'right_elbow': (100.0, 150.0),
            },
        )

    @classmethod
    def overhead_smash(cls) -> ActionTemplate:
        """Overhead smash."""
        return ActionTemplate(
            name='overhead_smash',
            description='高压杀球(Smash) - 过顶用力击打高球',
            key_joints=cls.RACKET_ARM_JOINTS + ['right_hip', 'left_knee'],
            ideal_angles={
                'right_shoulder': (130.0, 180.0),  # arm high
                'right_elbow': (120.0, 170.0),     # high contact point
                'right_hip': (140.0, 180.0),       # body extended
            },
        )

    @classmethod
    def serve(cls) -> ActionTemplate:
        """Underhand serve."""
        return ActionTemplate(
            name='serve',
            description='发球(Serve) - 下手击球的发球动作',
            key_joints=cls.RACKET_ARM_JOINTS + ['right_hip', 'right_knee'],
            ideal_angles={
                'right_shoulder': (20.0, 80.0),   # pendulan swing low to high
                'right_elbow': (140.0, 180.0),    # relatively straight
                'right_hip': (150.0, 180.0),      # upright
                'right_knee': (130.0, 170.0),     # slight bend to stand step
            },
        )

    @classmethod
    def all_templates(cls) -> Dict[str, ActionTemplate]:
        """Get all built-in templates."""
        return {
            'ready_stance': cls.ready_stance(),
            'dink_forehand': cls.dink_forehand(),
            'dink_backhand': cls.dink_backhand(),
            'drive_forehand': cls.drive_forehand(),
            'drive_backhand': cls.drive_backhand(),
            'volley_forehand': cls.volley_forehand(),
            'volley_backhand': cls.volley_backhand(),
            'overhead_smash': cls.overhead_smash(),
            'serve': cls.serve(),
        }

    @classmethod
    def detect_action_type(
        cls,
        angles: Dict[str, Optional[float]],
        arm_velocity: float,
        templates: Optional[Dict[str, ActionTemplate]] = None,
    ) -> Optional[Tuple[str, float]]:
        """Detect which action best matches current angles.

        Args:
            angles: Current joint angles
            arm_velocity: Current peak arm angular velocity
            templates: Templates to match against (defaults to all built-in)

        Returns:
            (action_name, confidence) or None
        """
        if templates is None:
            templates = cls.all_templates()

        best_match = None
        best_score = 0.0

        for name, template in templates.items():
            if not template.ideal_angles:
                continue

            match_count = 0
            total = 0
            for joint, (min_a, max_a) in template.ideal_angles.items():
                angle = angles.get(joint)
                if angle is None:
                    continue
                total += 1
                if min_a <= angle <= max_a:
                    match_count += 1
                else:
                    # Partial credit for being close
                    dist = min(abs(angle - min_a), abs(angle - max_a))
                    if dist < 15:
                        match_count += 0.5

            if total == 0:
                continue

            score = match_count / total

            # Provide some minor contextual boost
            if name == 'overhead_smash' and arm_velocity > 200:
                score *= 1.2
            elif 'drive' in name and arm_velocity > 150:
                score *= 1.1
            elif 'dink' in name and arm_velocity < 150:
                score *= 1.1
            elif name == 'ready_stance' and arm_velocity < 50:
                score *= 1.2

            score = min(1.0, score)

            if score > best_score:
                best_score = score
                best_match = name

        if best_match and best_score >= 0.5:
            return best_match, best_score

        return None
