from .otis import RightOtis


def register():
    from reachy.parts.arm import hands
    hands['otis'] = {'right': RightOtis}
