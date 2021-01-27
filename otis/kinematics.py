import numpy as np
from operator import itemgetter


class NoFKSolutionError(Exception):
    def __init__(self, theta_a, theta_b) -> None:
        super().__init__(f'theta=({theta_a}, {theta_b})')


class NoIKSolutionError(Exception):
    def __init__(self, x, y) -> None:
        super().__init__(f'taregt pos=({x}, {y})')


class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class Circle(object):
    def __init__(self, x=0, y=0, r=1):
        self.x = x
        self.y = y
        self.r = r


class FiveBarsMechanism(object):
    def __init__(self, params, angle_unit='deg'):
        self.angle_unit = angle_unit
        # params = [Ax, Ay, Bx, By, R_A, R_B, L_A, L_B, d, theta_G]

        if isinstance(params, dict):
            self.A = Point(params['Ax'], params['Ay'])
            self.B = Point(params['Bx'], params['By'])
            self.R_A = params['R_A']
            self.R_B = params['R_B']
            self.L_A = params['L_A']
            self.L_B = params['L_B']
            self.delta = params['d']
            self.theta_G = params['theta_G']

        elif isinstance(params, list):
            self.A = Point()
            self.B = Point()
            self.A.x, self.A.y, self.B.x, self.B.y, self.R_A, self.R_B, self.L_A, self.L_B, self.delta, self.theta_G = params

    def forward(self, theta_A, theta_B):
        if self.angle_unit == 'deg':
            theta_A = np.deg2rad(theta_A)
            theta_B = np.deg2rad(theta_B)
            theta_G = np.deg2rad(self.theta_G)

        C = [self.R_A * np.cos(theta_A) + self.A.x,
             self.R_A * np.sin(theta_A) + self.A.y]

        D = [self.R_B * np.cos(theta_B) + self.B.x,
             self.R_B * np.sin(theta_B) + self.B.y]

        C_A = Circle(C[0], C[1], self.L_A)
        C_B = Circle(D[0], D[1], self.L_B)

        sols = get_two_circles_intersections(C_A, C_B)

        if sols is None:
            raise NoFKSolutionError(theta_A, theta_B)

        dist = np.sqrt((sols[0][0]-sols[1][0])**2 + (sols[0][1]-sols[1][1])**2)

        if np.rad2deg(np.arccos(max(min(dist / 2 / max(self.L_B, self.L_A), -1), 1))) > 80:
            raise NoFKSolutionError(theta_A, theta_B)

        E = max(sols, key=itemgetter(1))  # does not work well for some extrem positions

        # Test flipped leg
        V_BD = [D[0]-self.B.x, D[1]-self.B.y]
        Eb = np.array([self.B.x, self.B.y]) + np.array(V_BD) * (self.L_B + self.R_B) / self.R_B
        if np.arctan2(E[1], E[0]) - np.arctan2(Eb[1], Eb[0]) < 0:
            # B leg has flipped
            raise NoFKSolutionError(theta_A, theta_B)

        V_AC = [C[0]-self.A.x, C[1]-self.A.y]
        Ea = np.array([self.A.x, self.A.y]) + np.array(V_AC) * (self.L_A + self.R_A) / self.R_A
        if np.arctan2(E[1], E[0]) - np.arctan2(Ea[1], Ea[0]) > 0:
            # A leg has flipped
            raise NoFKSolutionError(theta_A, theta_B)

        CE_angle = np.arctan2(E[1]-C[1], E[0]-C[0])

        # If G is a rigid body with CE
        G = [E[0] + self.delta * np.cos(CE_angle + theta_G),
             E[1] + self.delta * np.sin(CE_angle + theta_G)]

        # If G is a rigid body with DE
        # V_DE = [E[0]-D[0], E[1]-D[1]]
        # G = np.array(D) + np.array(V_DE) * (self.delta + self.L_B) / self.L_B

        return G[0], G[1]

    def inverse(self, x, y, solA_range=[-180, 180], solB_range=[-180, 180]):
        # If G is a rigid body with CE

        theta_G = self.theta_G
        if self.angle_unit == 'deg':
            theta_G = np.deg2rad(self.theta_G)

        r = np.sqrt(self.delta**2 + self.L_A**2 - 2*self.delta*self.L_A*np.cos(np.pi-theta_G))
        C_G = Circle(x, y, r)
        C_A = Circle(self.A.x, self.A.y, self.R_A)

        C = get_two_circles_intersections(C_G, C_A)
        if C is None:
            raise NoIKSolutionError(x, y)

        C = min(C, key=itemgetter(0))

        C = Point(C[0], C[1])

        C_delta = Circle(x, y, self.delta)
        C_C = Circle(C.x, C.y, self.L_A)

        E = get_two_circles_intersections(C_delta, C_C)

        # sould not work everywher on the space :(
        E = min(E, key=itemgetter(1))
        E = Point(E[0], E[1])

        C_E = Circle(E.x, E.y, self.L_B)
        C_B = Circle(self.B.x, self.B.y, self.R_B)
        D = get_two_circles_intersections(C_E, C_B)

        if D is None:
            raise NoIKSolutionError(x, y)

        D = max(D, key=itemgetter(0))

        D = Point(D[0], D[1])

        # If G is a rigid body with DE
        # C_G = Circle(x, y, self.L_B + self.delta)
        # C_B = Circle( self.B.x, self.B.y, self.R_B)

        # D = get_two_circles_intersections(C_G, C_B)
        # if not D:
        #     return None

        # D = max(D, key=itemgetter(0))

        # D = Point(D[0], D[1])

        # C_E = Circle(x + self.delta /(self.L_B+self.delta ) * (D.x - x),
        #              y + self.delta /(self.L_B+self.delta ) * (D.y - y),
        #              self.L_A)

        # C_A = Circle(self.A.x, self.A.y, self.R_A)

        # C = get_two_circles_intersections(C_E, C_A)
        # if not C:
        #     return None

        # C = min(C, key=itemgetter(0))
        # C = Point(C[0], C[1])

        theta_A = np.arccos(min(max((C.x - self.A.x) / self.R_A, -1), 1))
        theta_B = np.arccos(min(max((D.x - self.B.x) / self.R_B, -1), 1))

        theta_A = 2 * np.pi - theta_A if C.y - self.A.y < 0 else theta_A
        theta_B = -theta_B if (D.y - self.B.y) < 0 else theta_B

        if not(solA_range[0] <= np.rad2deg(theta_A) <= solA_range[1]):
            raise NoIKSolutionError(x, y)

        if not(solB_range[0] <= np.rad2deg(theta_B) <= solB_range[1]):
            raise NoIKSolutionError(x, y)

        if self.angle_unit == 'deg':
            return (np.rad2deg(theta_A), np.rad2deg(theta_B))
        else:
            return (theta_A, theta_B)


def get_two_circles_intersections(C0, C1):
    # C0 and C1 are Circle objects
    d = np.sqrt((C1.x - C0.x)**2 + (C1.y - C0.y)**2)

    # non intersecting
    if d > C0.r + C1.r:
        return None
    # One circle within other
    if d < abs(C0.r-C1.r):
        return None
    # coincident circles
    if d == 0 and C0.r == C1.r:
        return None

    a = (C0.r**2 - C1.r**2 + d**2) / (2 * d)
    h = np.sqrt(C0.r**2 - a**2)

    x2 = C0.x + a * (C1.x - C0.x) / d
    y2 = C0.y + a * (C1.y - C0.y) / d

    x_sol_1 = x2 + h * (C1.y - C0.y) / d
    y_sol_1 = y2 - h * (C1.x - C0.x) / d

    x_sol_2 = x2 - h * (C1.y - C0.y) / d
    y_sol_2 = y2 + h * (C1.x - C0.x) / d

    return (x_sol_1, y_sol_1), (x_sol_2, y_sol_2)
