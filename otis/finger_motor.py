
class FingerMotor:
    def __init__(self, dxl_motor, reduction) -> None:
        self.dxl_motor = dxl_motor
        self.reduction = reduction

    # Position
    @property
    def present_position(self):
        return self.dxl_motor.present_position * -self.reduction

    @property
    def goal_position(self):
        return self.dxl_motor.goal_position * -self.reduction

    @goal_position.setter
    def goal_position(self, value):
        self.dxl_motor.goal_position = value / -self.reduction

    @property
    def moving_speed(self):
        return self.dxl_motor.moving_speed * self.reduction

    @moving_speed.setter
    def moving_speed(self, value):
        self.dxl_motor.moving_speed = value / self.reduction

    # Compliancy
    @property
    def compliant(self):
        return self.dxl_motor.compliant

    @compliant.setter
    def compliant(self, value):
        self.dxl_motor.compliant = value

    @property
    def torque_limit(self):
        return self.dxl_motor.torque_linit

    @torque_limit.setter
    def torque_limit(self, value):
        self.dxl_motor.torque_linit = value

    # Temperature
    @property
    def temperature(self):
        """Check the current motor temp. (in °C)."""
        return self.dxl_motor.temperature

    def goto(self,
             goal_position, duration,
             starting_point='present_position',
             wait=False, interpolation_mode='linear'):
        """Set trajectory goal for the motor.
        Args:
            goal_position (float): target position (in degrees)
            duration (float): duration of the movement (in seconds)
            starting_point (str): register used to determine the starting point (eg. 'goal_position' can also be used in some specific case)
            wait (bool): whether or not to wait for the end of the motion
            interpolation_mode (str): interpolation technique used for computing the trajectory ('linear', 'minjerk')
        Returns:
            reachy.trajectory.TrajectoryPlayer: trajectory player that can be used to monitor the trajectory, stop it, etc
        """
        return self.dxl_motor.goto(
            goal_position=goal_position / -self.reduction,
            duration=duration, wait=wait, interpolation_mode=interpolation_mode)

    def use_static_error_fix(self, activate):
        pass
