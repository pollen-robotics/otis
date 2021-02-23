import numpy as np

from collections import OrderedDict

from reachy.parts.hand import Hand

from .finger_motor import FingerMotor
from .kinematics import FiveBarsMechanism


class RightOtis(Hand):
    """RightOtis part.

    Args:
        side (str): which side the hand is attached to ('left' or 'right')
        io (str): port name where the modules can be found
    """

    dxl_motors = OrderedDict([
        ('forearm_yaw', {
            'id': 14, 'offset': 0.0, 'orientation': 'indirect',
            'angle-limits': [-100, 100],
            'link-translation': [0, 0, 0], 'link-rotation': [0, 0, 1],
        }),
        ('wrist_pitch', {
            'id': 15, 'offset': 0.0, 'orientation': 'indirect',
            'angle-limits': [-45, 45],
            'link-translation': [0, 0, -0.25], 'link-rotation': [0, 1, 0],
        }),
        ('wrist_roll', {
            'id': 16, 'offset': -15.0, 'orientation': 'indirect',
            'angle-limits': [-45, 45],
            'link-translation': [0, 0, 0], 'link-rotation': [1, 0, 0],
        }),
        ('_motor_a', {
            'id': 3, 'offset': 226.0, 'orientation': 'direct',
            'angle-limits': [-123, 140],
            'link-translation': [0, 0, 0], 'link-rotation': [0, 0, 0],
        }),
        ('_motor_b', {
            'id': 5, 'offset': 57.0, 'orientation': 'direct',
            'angle-limits': [-150, 117],
            'link-translation': [0, 0, 0], 'link-rotation': [0, 0, 0],
        }),
        ('motor_lift', {
            'id': 7, 'offset': 0, 'orientation': 'direct',
            'angle-limits': [-150, 150],
            'link-translation': [0, 0, 0], 'link-rotation': [0, 0, 0],
        }),
    ])

    five_bars_mechanism_params = {
        'Ax': 40,
        'Ay': 45,
        'Bx': 90,
        'By': 35,
        'R_A': 30,
        'R_B': 30,
        'L_A': 60,
        'L_B': 50,
        'd': 15,
        'theta_G': 80,
    }
    reduction = 0.5

    def __init__(self, root, io):
        super().__init__(root, io)

        dxl_motors = OrderedDict({
            name: dict(conf)
            for name, conf in self.dxl_motors.items()
        })

        self.attach_dxl_motors(dxl_motors)

        self.motor_a = FingerMotor(self._motor_a, self.reduction)
        self.motor_b = FingerMotor(self._motor_b, self.reduction)
        self.mechanism = FiveBarsMechanism(self.five_bars_mechanism_params)

        self.otis_motors = [self.motor_a, self.motor_b, self.motor_lift]

    def forward(self, motor_a_pos=None, motor_b_pos=None):
        """Compute the forward kinematics of the handwriting fingers.

        Args:
            motor_a_pos (float): motor a position in degrees
            motor_b_pos (float): motor a position in degrees
        Returns:
            (x, y): float the cartesian coordinates (in mm)

        If you do not provide the motor a and b position, their current position is used.
        You can also provide array of theta_a, theta_b positions.
        """
        if motor_a_pos is None:
            motor_a_pos = self.motor_a.present_position
        if motor_b_pos is None:
            motor_b_pos = self.motor_b.present_position

        if hasattr(motor_a_pos, '__iter__'):
            if len(motor_a_pos) != len(motor_b_pos):
                raise ValueError('Positions for motor a and b should be the same length!')

            return np.array([
                self.mechanism.forward(pos_a, pos_b)
                for pos_a, pos_b in zip(motor_a_pos, motor_b_pos)
            ]).T

        return self.mechanism.forward(
                theta_A=motor_a_pos,
                theta_B=motor_b_pos,
            )

    def inverse(self, x, y):
        """Compute the inverse kinematics of the handwriting fingers.

        Args:
            x (float): the x cartesian coordinates in mm
            y (float): the x cartesian coordinates in mm
        Returns:
            (theta_a, theta_b): the motor a and b corresponding angles.

        You can also provide array of x, y positions.
        """
        if hasattr(x, '__iter__'):
            if len(x) != len(y):
                raise ValueError('x and y should be the same length!')

            return np.array([
                self.mechanism.inverse(xx, yy)
                for xx, yy in zip(x, y)
            ]).T

        return self.mechanism.inverse(x, y)

    @property
    def compliant(self):
        return all([m.compliant for m in self.otis_motors])

    @compliant.setter
    def compliant(self, value):
        for m in self.otis_motors:
            m.compliant = value

    def lift(self, duration=0.5, pos=-30):
        """Lift the pencil."""
        self.motor_lift.goto(
            goal_position=pos, duration=duration,
            wait=True, interpolation_mode='minjerk',
        )

    def drop(self, duration=0.5, pos=90):
        """Drop the pencil."""
        self.motor_lift.goto(
            goal_position=pos, duration=duration,
            wait=True, interpolation_mode='minjerk',
        )

    def goto(self,
             goal_positions, duration,
             starting_point='present_position',
             wait=True, interpolation_mode='minjerk'):
        """Set trajectory goal for the specified motors.
        Args:
            goal_positions (dict): desired target position (in the form {'motor_name': target_position})
            duration (float): duration of the movement (in seconds)
            starting_point (str): register used to determine the starting point (eg. 'goal_position' can also be used in some specific case)
            wait (bool): whether or not to wait for the end of the motion
            interpolation_mode (str): interpolation technique used for computing the trajectory ('linear', 'minjerk')
        Returns:
            reachy.trajectory.TrajectoryPlayer: trajectory player that can be used to monitor the trajectory, stop it, etc
        """
        trajs = []

        for i, (motor_name, goal_pos) in enumerate(goal_positions.items()):
            last = wait and (i == len(goal_positions) - 1)

            motor = getattr(self, motor_name)
            trajs.append(motor.goto(goal_pos, duration, starting_point,
                         wait=last, interpolation_mode=interpolation_mode))

        return trajs
