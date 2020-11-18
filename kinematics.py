import numpy as np
from operator import itemgetter


class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

class Circle(object):
    def __init__(self, x=0, y=0, r=1):
        self.x = x
        self.y = y
        self.r = r

class five_bars_writting_mechanism(object):
    def __init__(self, params, angle_unit='deg'):
        self.angle_unit = angle_unit
        
        self.A = Point(params['A'][0], params['A'][1])
        self.B = Point(params['B'][0], params['B'][1])
        self.R_A = params['R_A']
        self.R_B = params['R_B']
        self.L_A = params['L_A']
        self.L_B = params['L_B']
        self.delta = params['d']
    
    def forward(self, theta_A, theta_B):
        if self.angle_unit == 'deg':
            theta_A = np.deg2rad(theta_A)
            theta_B = np.deg2rad(theta_B)

        C = [self.R_A * np.cos(theta_A) + self.A.x, 
            self.R_A * np.sin(theta_A) + self.A.y]

        D = [self.R_B * np.cos(theta_B) + self.B.x,
            self.R_B * np.sin(theta_B) + self.B.y]
        
        C_A = Circle(C[0], C[1], self.L_A)
        C_B = Circle(D[0], D[1], self.L_B)

        sols = get_two_circles_intersections(C_A, C_B)

        if not(sols):
            return None

        E = max(sols, key=itemgetter(1))
        phi = np.arcsin( (E[1]-D[1])/self.L_B)

        #G point
        x = E[0] + self.delta * np.cos(np.pi - phi)
        y = E[1] + self.delta * np.sin(np.pi - phi)

        return x, y 

    
    def inverse(self, x, y):
        
        C_G = Circle(x, y, self.L_B + self.delta)
        C_B = Circle( self.B.x, self.B.y, self.R_B)

        D = max(get_two_circles_intersections(C_G, C_B), key=itemgetter(0))
        D = Point(D[0], D[1])

        C_E = Circle(x + self.delta /(self.L_B+self.delta ) * (D.x - x), 
                     y + self.delta /(self.L_B+self.delta ) * (D.y - y), 
                     self.L_A)
        
        C_A = Circle(self.A.x, self.A.y, self.R_A)

        C = min(get_two_circles_intersections(C_E, C_A), key=itemgetter(0))
        C = Point(C[0], C[1])

        theta_A = np.arccos((C.x - self.A.x) / self.R_A)
        theta_B = np.arccos((D.x - self.B.x) / self.R_B) 

        theta_A = 2*np.pi - theta_A if C.y - self.A.y < 0 else theta_A
        theta_B = -1 * theta_B if D.y - self.B.y < 0 else theta_B

        if self.angle_unit == 'deg':
            return (np.rad2deg(theta_A), np.rad2deg(theta_B))
        else :
            return (theta_A, theta_B)


def get_two_circles_intersections(C0, C1): 
    #C0 and C1 are Circle objects

    d = np.sqrt((C1.x - C0.x)**2 + (C1.y - C0.y)**2)
    
    # non intersecting
    if d > C0.r + C1.r :
        return None
    # One circle within other
    if d < abs(C0.r-C1.r):
        return None
    # coincident circles
    if d == 0 and C0.r == C1.r:
        return None
    else:
        a = (C0.r**2 - C1.r**2 + d**2) / (2 * d)
        h = np.sqrt(C0.r**2 - a**2)
        
        x2 = C0.x + a * (C1.x - C0.x) / d   
        y2 = C0.y + a * (C1.y - C0.y) / d 
        
        x_sol_1 = x2 + h * (C1.y - C0.y) / d     
        y_sol_1 = y2 - h * (C1.x - C0.x) / d 

        x_sol_2 = x2 - h * (C1.y - C0.y) / d
        y_sol_2 = y2 + h * (C1.x - C0.x) / d
        
        return (x_sol_1, y_sol_1), (x_sol_2, y_sol_2)
