"""
Ball Collection Path Planner — pure algorithm functions.

All functions operate on numpy arrays. Imports field constants but no matplotlib
or UI dependencies.
"""

from collections import deque

import numpy as np

from field import INTAKE_WIDTH

INTAKE_HALF_WIDTH = INTAKE_WIDTH / 2


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def path_distance(points: np.ndarray) -> float:
    """Sum of euclidean distances between consecutive points.

    Parameters
    ----------
    points : ndarray, shape (N, 2)

    Returns
    -------
    float  Total path length.
    """
    if len(points) < 2:
        return 0.0
    diffs = np.diff(points, axis=0)
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


# ---------------------------------------------------------------------------
# Clustering (Phase 1)
# ---------------------------------------------------------------------------

def find_nearest_cluster(
    balls: np.ndarray,
    robot_pos: np.ndarray,
    radius: float = 1.5,
) -> np.ndarray:
    """Flood-fill cluster seeded from the ball nearest to the robot.

    Parameters
    ----------
    balls : ndarray, shape (N, 2)
    robot_pos : ndarray, shape (2,)
    radius : float  Max distance to consider a ball part of the cluster.

    Returns
    -------
    ndarray, shape (M, 2)  Balls belonging to the nearest cluster.
    """
    if len(balls) == 0:
        return np.empty((0, 2))

    # Seed: ball closest to robot
    dists = np.linalg.norm(balls - robot_pos, axis=1)
    seed_idx = int(np.argmin(dists))

    in_cluster = np.zeros(len(balls), dtype=bool)
    in_cluster[seed_idx] = True

    # BFS expansion
    queue = deque([seed_idx])
    while queue:
        curr = queue.popleft()
        d = np.linalg.norm(balls - balls[curr], axis=1)
        for i in range(len(balls)):
            if not in_cluster[i] and d[i] <= radius:
                in_cluster[i] = True
                queue.append(i)

    return balls[in_cluster]


def find_all_clusters(balls: np.ndarray, radius: float = 1.5) -> list[np.ndarray]:
    """Partition all balls into clusters using BFS flood-fill.

    Parameters
    ----------
    balls  : ndarray, shape (N, 2)
    radius : float  Max distance between balls in the same cluster.

    Returns
    -------
    list[ndarray]  Each element is an (M, 2) array of balls in one cluster.
    """
    if len(balls) == 0:
        return []

    visited = np.zeros(len(balls), dtype=bool)
    clusters: list[np.ndarray] = []

    for seed in range(len(balls)):
        if visited[seed]:
            continue
        # BFS from this seed
        in_cluster = np.zeros(len(balls), dtype=bool)
        in_cluster[seed] = True
        visited[seed] = True
        queue = deque([seed])
        while queue:
            curr = queue.popleft()
            d = np.linalg.norm(balls - balls[curr], axis=1)
            for i in range(len(balls)):
                if not visited[i] and d[i] <= radius:
                    visited[i] = True
                    in_cluster[i] = True
                    queue.append(i)
        clusters.append(balls[in_cluster])

    return clusters


def score_cluster(
    cluster: np.ndarray,
    robot_pos: np.ndarray,
    distance_bias: float = 0.5,
) -> tuple[float, float]:
    """Score a cluster by size / (min_distance_to_robot + bias).

    Parameters
    ----------
    cluster       : ndarray, shape (M, 2)
    robot_pos     : ndarray, shape (2,)
    distance_bias : float  Prevents division-by-zero; ~robot radius.

    Returns
    -------
    (score, min_distance)
    """
    dists = np.linalg.norm(cluster - robot_pos, axis=1)
    min_dist = float(np.min(dists))
    score = len(cluster) / (min_dist + distance_bias)
    return score, min_dist


def select_best_cluster(
    balls: np.ndarray,
    robot_pos: np.ndarray,
    radius: float = 1.5,
    distance_bias: float = 0.5,
) -> dict | None:
    """Find all clusters and return the highest-scoring one.

    Returns
    -------
    dict with keys: cluster, score, min_distance, size, num_clusters.
    None if no balls.
    """
    clusters = find_all_clusters(balls, radius=radius)
    if not clusters:
        return None

    best_cluster = None
    best_score = -1.0
    best_min_dist = 0.0

    for c in clusters:
        s, md = score_cluster(c, robot_pos, distance_bias=distance_bias)
        if s > best_score:
            best_score = s
            best_min_dist = md
            best_cluster = c

    return {
        "cluster": best_cluster,
        "score": best_score,
        "min_distance": best_min_dist,
        "size": len(best_cluster),
        "num_clusters": len(clusters),
    }


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------

def nearest_neighbor_order(
    points: np.ndarray,
    start: np.ndarray,
) -> np.ndarray:
    """Greedy nearest-neighbor ordering starting from *start*.

    Parameters
    ----------
    points : ndarray, shape (N, 2)  Points to visit.
    start  : ndarray, shape (2,)    Starting position (not included in output).

    Returns
    -------
    ndarray, shape (N, 2)  *points* reordered by nearest-neighbor.
    """
    if len(points) == 0:
        return np.empty((0, 2))

    remaining = list(range(len(points)))
    ordered: list[int] = []
    current = start.copy()

    while remaining:
        dists = np.linalg.norm(points[remaining] - current, axis=1)
        nearest_idx = int(np.argmin(dists))
        chosen = remaining.pop(nearest_idx)
        ordered.append(chosen)
        current = points[chosen]

    return points[ordered]


# ---------------------------------------------------------------------------
# 2-opt improvement
# ---------------------------------------------------------------------------

def two_opt_improve(tour: np.ndarray) -> np.ndarray:
    """Open-path 2-opt refinement. First point is fixed (robot position).

    Parameters
    ----------
    tour : ndarray, shape (N, 2)  Ordered waypoints (first = robot pos).

    Returns
    -------
    ndarray, shape (N, 2)  Improved tour.
    """
    if len(tour) < 4:
        return tour.copy()

    tour = tour.copy()
    n = len(tour)
    improved = True

    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                # Current edges: (i, i+1) and (j, j+1 if exists)
                d_old = np.linalg.norm(tour[i] - tour[i + 1])
                if j + 1 < n:
                    d_old += np.linalg.norm(tour[j] - tour[j + 1])
                    d_new = (np.linalg.norm(tour[i] - tour[j])
                             + np.linalg.norm(tour[i + 1] - tour[j + 1]))
                else:
                    # j is the last point — only one edge to compare
                    d_new = np.linalg.norm(tour[i] - tour[j])

                if d_new < d_old - 1e-10:
                    tour[i + 1:j + 1] = tour[i + 1:j + 1][::-1]
                    improved = True

    return tour


# ---------------------------------------------------------------------------
# Intake-aware waypoint pruning
# ---------------------------------------------------------------------------

def _point_to_segment_dist(point: np.ndarray, seg_start: np.ndarray, seg_end: np.ndarray) -> float:
    """Minimum distance from a point to a line segment."""
    v = seg_end - seg_start
    u = point - seg_start
    len_sq = np.dot(v, v)
    if len_sq < 1e-12:
        return float(np.linalg.norm(u))
    t = np.clip(np.dot(u, v) / len_sq, 0.0, 1.0)
    projection = seg_start + t * v
    return float(np.linalg.norm(point - projection))


def prune_waypoints(waypoints: np.ndarray, intake_half_width: float) -> np.ndarray:
    """Remove waypoints the intake can collect in passing.

    Iteratively removes intermediate waypoints that fall within
    intake_half_width of the straight line between their kept
    neighbours. Re-validates after each pass since removing one
    waypoint changes the segments that remaining waypoints are
    measured against.

    First and last waypoints are always kept.
    """
    if len(waypoints) <= 2:
        return waypoints.copy()

    kept = list(range(len(waypoints)))
    changed = True
    while changed:
        changed = False
        new_kept = [kept[0]]
        for j in range(1, len(kept) - 1):
            seg_start = waypoints[new_kept[-1]]
            seg_end = waypoints[kept[j + 1]]
            dist = _point_to_segment_dist(waypoints[kept[j]], seg_start, seg_end)
            if dist >= intake_half_width:
                new_kept.append(kept[j])
            else:
                changed = True
        new_kept.append(kept[-1])
        kept = new_kept

    return waypoints[kept]


# ---------------------------------------------------------------------------
# Catmull-Rom spline smoothing
# ---------------------------------------------------------------------------

def smooth_path(waypoints: np.ndarray, num_interp: int = 20) -> np.ndarray:
    """Catmull-Rom spline interpolation through waypoints.

    Parameters
    ----------
    waypoints  : ndarray, shape (N, 2)
    num_interp : int  Points to insert between each pair of waypoints.

    Returns
    -------
    ndarray, shape (M, 2)  Smooth path including original waypoints.
    """
    if len(waypoints) < 2:
        return waypoints.copy()

    # Clamp endpoints by repeating first/last
    pts = np.vstack([waypoints[0], waypoints, waypoints[-1]])

    result = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t_idx in range(num_interp):
            t = t_idx / num_interp
            # Catmull-Rom formula
            q = 0.5 * (
                (2 * p1)
                + (-p0 + p2) * t
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3
            )
            result.append(q)

    # Append the final waypoint
    result.append(waypoints[-1])
    return np.array(result)


# ---------------------------------------------------------------------------
# High-level planners
# ---------------------------------------------------------------------------

def plan_nearest_cluster(
    balls: np.ndarray,
    robot_pos: np.ndarray,
    cluster_radius: float = 1.5,
) -> dict:
    """Phase 1: find best cluster, NN order, smooth path.

    Returns
    -------
    dict with keys:
        cluster            — (M, 2) balls in the selected cluster
        waypoints          — ordered waypoints (NN order, pruned)
        path               — smooth Catmull-Rom path through waypoints
        distance           — total path distance (smooth)
        cluster_score      — score of the selected cluster
        cluster_min_distance — distance to nearest ball in cluster
        cluster_size       — number of balls in cluster
        num_clusters       — total clusters found
    Returns None if no balls.
    """
    if len(balls) == 0:
        return None

    selection = select_best_cluster(balls, robot_pos, radius=cluster_radius)
    if selection is None:
        return None

    cluster = selection["cluster"]
    ordered = nearest_neighbor_order(cluster, robot_pos)

    # Prepend robot position for path generation
    waypoints = np.vstack([robot_pos, ordered])
    total_waypoints = len(waypoints)
    waypoints = prune_waypoints(waypoints, INTAKE_HALF_WIDTH)
    path = smooth_path(waypoints)

    return {
        "cluster": cluster,
        "waypoints": waypoints,
        "path": path,
        "distance": path_distance(path),
        "total_waypoints": total_waypoints,
        "pruned_waypoints": total_waypoints - len(waypoints),
        "cluster_score": selection["score"],
        "cluster_min_distance": selection["min_distance"],
        "cluster_size": selection["size"],
        "num_clusters": selection["num_clusters"],
    }


def plan_full_sweep(
    balls: np.ndarray,
    robot_pos: np.ndarray,
) -> dict:
    """Phase 2: NN + 2-opt on all balls.  Returns both paths for comparison.

    Returns
    -------
    dict with keys:
        nn_waypoints    — (N+1, 2) robot_pos + NN ordered balls
        nn_path         — smooth path (NN only)
        nn_distance     — NN path distance
        opt_waypoints   — (N+1, 2) robot_pos + 2-opt improved order
        opt_path        — smooth path (2-opt)
        opt_distance    — 2-opt path distance
        improvement_pct — percentage improvement from 2-opt
    Returns None if no balls.
    """
    if len(balls) == 0:
        return None

    ordered = nearest_neighbor_order(balls, robot_pos)

    # NN-only path
    nn_waypoints = np.vstack([robot_pos, ordered])
    total_waypoints = len(nn_waypoints)

    # 2-opt improved path (before pruning)
    opt_waypoints = two_opt_improve(nn_waypoints)

    # Prune both paths
    nn_waypoints = prune_waypoints(nn_waypoints, INTAKE_HALF_WIDTH)
    opt_waypoints = prune_waypoints(opt_waypoints, INTAKE_HALF_WIDTH)

    nn_path = smooth_path(nn_waypoints)
    nn_dist = path_distance(nn_path)

    opt_path = smooth_path(opt_waypoints)
    opt_dist = path_distance(opt_path)

    improvement = (nn_dist - opt_dist) / nn_dist * 100 if nn_dist > 0 else 0.0

    return {
        "nn_waypoints": nn_waypoints,
        "nn_path": nn_path,
        "nn_distance": nn_dist,
        "opt_waypoints": opt_waypoints,
        "opt_path": opt_path,
        "opt_distance": opt_dist,
        "improvement_pct": improvement,
        "total_waypoints": total_waypoints,
        "pruned_waypoints": total_waypoints - len(opt_waypoints),
    }
