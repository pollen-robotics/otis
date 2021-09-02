from reachy_sdk.trajectory import goto
from reachy_sdk.trajectory.interpolation import minimum_jerk


def lift(reachy, duration=0.5, pos=-30):
    """Lift the pencil."""
    goto(
        goal_positions={reachy.r_arm.r_otis_motor_lift: pos},
        duration=duration,
        interpolation_mode=minimum_jerk,
    )

def drop(reachy, duration=0.5, pos=90):
    """Drop the pencil."""
    goto(
        goal_positions={reachy.r_arm.r_otis_motor_lift: pos},
        duration=duration,
        interpolation_mode=minimum_jerk,
    )
