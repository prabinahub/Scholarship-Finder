import numpy as np


def topsis(matrix, weights, benefit):
    """Score every row from 0 to 1 (higher is better).

    matrix  - one row per option, one column per criterion
    weights - how important each criterion is
    benefit - True if bigger is better for that criterion, False if smaller is better
    """
    if len(matrix) == 0:
        return []
    x = np.array(matrix, dtype=float)

    # 1. Put every column on the same scale
    norms = np.sqrt((x ** 2).sum(axis=0))
    norms[norms == 0] = 1
    v = x / norms * np.array(weights, dtype=float)

    # 2. The best and worst value in each column
    is_benefit = np.array(benefit, dtype=bool)
    best = np.where(is_benefit, v.max(axis=0), v.min(axis=0))
    worst = np.where(is_benefit, v.min(axis=0), v.max(axis=0))

    # 3. How far each option is from the best and from the worst
    d_best = np.sqrt(((v - best) ** 2).sum(axis=1))
    d_worst = np.sqrt(((v - worst) ** 2).sum(axis=1))

    # 4. Closeness to the best: 1 = the best, 0 = the worst
    total = d_best + d_worst
    safe_total = np.where(total == 0, 1, total)
    closeness = np.where(total == 0, 0.5, d_worst / safe_total)
    return [float(c) for c in closeness]
