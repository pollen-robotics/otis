import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches


def estimate_reachable_area(mechanism, angle_A_limits=[-180, 180], angle_B_limits=[-180, 180], init_sampling=10, area_sampling=100):
    f = []

    for m1 in np.linspace(*angle_A_limits, init_sampling):
        for m2 in np.linspace(*angle_B_limits, init_sampling):
            pos = mechanism.forward(m1, m2)
            if pos:
                f.append(pos)
    
    f = np.array(f)
    
    # Sample a whole rectangular surface including the reacheable space

    x_sampling = np.linspace(min(f[:,0]), max(f[:,0]), area_sampling)
    y_sampling = np.linspace(min(f[:,1]), max(f[:,1]), area_sampling)
    
    x_lenght = max(f[:,0]) - min(f[:,0])
    y_lenght = max(f[:,1]) - min(f[:,1])
    
    surface = x_lenght * y_lenght

    binary_space = np.zeros([area_sampling, area_sampling])
    reachable_space = []
    for i in range(area_sampling):
        for j in range(area_sampling):

            sol = mechanism.inverse(x_sampling[i], y_sampling[j], angle_A_limits, angle_B_limits)

            if sol:
                binary_space[i,j] = 0
                reachable_space.append([x_sampling[i], y_sampling[j]])
            else:
                binary_space[i,j] = 1
    
    rectangle = find_biggest_rectangle(binary_space)
    x_rect = [x_sampling[rectangle[0]], x_sampling[rectangle[2]]]
    y_rect = [y_sampling[rectangle[1]], y_sampling[rectangle[3]]]


    results = {
        'reachable_space': np.array(reachable_space),
        'binary_space': binary_space,
        'x': x_sampling,
        'y': y_sampling, 
        'biggest_rectangle': {'x_min':x_rect[0] , 'y_min': y_rect[0], 
                              'x_max':x_rect[1], 'y_max': y_rect[1], 
                              'x_length':x_rect[1]-x_rect[0], 'y_length':y_rect[1]-y_rect[0],
                              'surface': (x_rect[1]-x_rect[0])*(y_rect[1]-y_rect[0]), },
        'reachable_surface': binary_space.sum() / (area_sampling**2) * surface,
    }
    
    return results


def find_biggest_rectangle(binary_reachable_space):
    nrows = binary_reachable_space.shape[0]
    ncols = binary_reachable_space.shape[1]
    skip = 1
    area_max = (0, [])

    w = np.zeros(dtype=int, shape=binary_reachable_space.shape)
    h = np.zeros(dtype=int, shape=binary_reachable_space.shape)

    for r in range(nrows):
        for c in range(ncols):
            if binary_reachable_space[r][c] == skip:
                continue
            if r == 0:
                h[r][c] = 1
            else:
                h[r][c] = h[r-1][c]+1
            if c == 0:
                w[r][c] = 1
            else:
                w[r][c] = w[r][c-1]+1
            minw = w[r][c]
            for dh in range(h[r][c]):
                minw = min(minw, w[r-dh][c])
                area = (dh+1)*minw
                if area > area_max[0]:
                    area_max = (area, [r-dh, c-minw+1, r, c])
    
    biggest_rectangle = area_max[1]
    
    return biggest_rectangle


def plot_reachable_area(results):
    fig, ax = plt.subplots()

    reachable_space = results['reachable_space']

    ax.plot(reachable_space[:,0], reachable_space[:,1], '*')

    ax.add_patch(
        patches.Rectangle(
            (results['biggest_rectangle']['x_min'], results['biggest_rectangle']['y_min']),
            results['biggest_rectangle']['x_length'],
            results['biggest_rectangle']['y_length'],
            linewidth=3,
            edgecolor = 'red',
            fill=False, zorder=10
        ) )
    
    axes = plt.gca()
    axes.set_xlim([0,120])
    axes.set_ylim([35,150])
    
    plt.show()
    
    return fig, ax

def estimate_precision(mechanism, x_sampling, y_sampling, delta, angle_A_limits, angle_B_limits):
    pos_error = np.zeros([x_sampling.size, y_sampling.size])

    for i, x in enumerate(x_sampling):
        for j, y in enumerate(y_sampling):
            sol = mechanism.inverse(x,y,angle_A_limits, angle_B_limits )
            if sol:
                m1, m2 = sol
                error = []

                for m1e in [m1-delta, m1, m1+delta]:
                    for m2e in [m2-delta, m2, m2+delta]:
                        err_target = mechanism.forward(m1e, m2e)
                        if err_target:
                            error.append(np.abs(np.array([x, y]) - np.array(err_target)))

                error = np.array(error)
                error = np.sqrt(error[:,0]**2+error[:,1]**2)
                pos_error[i,j] = max(error)
            else:
                pos_error[i,j] = np.nan
    
    return pos_error