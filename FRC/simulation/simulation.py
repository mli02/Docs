#!/usr/bin/env python3
"""
Ball Collection Path Simulator — interactive matplotlib animation.

Controls
--------
Left click      Place a ball
Right click     Remove nearest ball (within 0.5m)
Space           Plan and start robot execution
1 / 2           Switch to Phase 1 / Phase 2 mode
s               Scatter 8-15 random balls
r               Reset (clear all)
p               Pause / resume
n               Add a random ball mid-execution (test replanning)
d               Toggle NN vs 2-opt path display (Phase 2)
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from field import (
    FIELD_LENGTH, FIELD_WIDTH, INTAKE_WIDTH,
    NN_PATH_COLOR, OPT_PATH_COLOR, CLUSTER_HIGHLIGHT,
    draw_field, draw_robot, draw_ball, draw_path,
)
from planner import (
    plan_nearest_cluster, plan_full_sweep, path_distance,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FPS = 30
ROBOT_SPEED = 3.5           # m/s
COLLECTION_RADIUS = INTAKE_WIDTH / 2 + 0.05  # tolerance for collecting balls
REMOVE_RADIUS = 0.5         # right-click remove tolerance
COMPARISON_PAUSE_SEC = 2.0  # pause to compare NN vs 2-opt before moving


# ---------------------------------------------------------------------------
# Simulation state
# ---------------------------------------------------------------------------
class SimState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.robot_pos = np.array([1.0, FIELD_WIDTH / 2])
        self.robot_heading = 0.0
        self.balls: list[np.ndarray] = []
        self.collected: set[int] = set()

        self.phase = 1                # 1 or 2
        self.status = "idle"          # idle | planning | comparing | executing | done
        self.paused = False
        self.show_nn_path = True      # toggle NN vs 2-opt display

        # Current plan data
        self.plan = None
        self.smooth_path = None       # the path the robot follows
        self.path_idx = 0             # current index along smooth_path
        self.trail: list[np.ndarray] = []

        # Display paths
        self.nn_path = None
        self.opt_path = None

        # Stats
        self.replan_count = 0
        self.comparison_timer = 0.0

        # Artists to clear each frame
        self._artists: list = []


state = SimState()


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def clear_artists():
    for a in state._artists:
        try:
            a.remove()
        except (ValueError, AttributeError):
            pass
    state._artists.clear()


def redraw(ax):
    """Full redraw of all dynamic elements."""
    clear_artists()

    # Balls
    for i, b in enumerate(state.balls):
        artist = draw_ball(ax, b[0], b[1], collected=(i in state.collected))
        state._artists.append(artist)

    # Cluster highlight (Phase 1)
    if state.phase == 1 and state.plan and "cluster" in state.plan:
        cluster = state.plan["cluster"]
        for pt in cluster:
            c = plt.Circle(pt, 0.3, color=CLUSTER_HIGHLIGHT, alpha=0.3, zorder=3)
            ax.add_patch(c)
            state._artists.append(c)

    # Paths
    if state.nn_path is not None and state.show_nn_path:
        arts = draw_path(ax, state.nn_path, color=NN_PATH_COLOR,
                         linestyle="--", label="NN path", linewidth=1.8)
        state._artists.extend(arts)

    if state.opt_path is not None:
        arts = draw_path(ax, state.opt_path, color=OPT_PATH_COLOR,
                         linestyle="-", label="2-opt path", linewidth=2.2)
        state._artists.extend(arts)

    # Phase 1 path (single green line)
    if state.phase == 1 and state.smooth_path is not None and state.opt_path is None:
        arts = draw_path(ax, state.smooth_path, color=OPT_PATH_COLOR,
                         linestyle="-", label="Cluster path", linewidth=2.0)
        state._artists.extend(arts)

    # Trail
    if len(state.trail) > 1:
        trail = np.array(state.trail)
        line, = ax.plot(trail[:, 0], trail[:, 1], color="#3080d0",
                        linewidth=1.2, alpha=0.4, zorder=2)
        state._artists.append(line)

    # Robot
    robot_arts = draw_robot(ax, state.robot_pos[0], state.robot_pos[1],
                            state.robot_heading)
    state._artists.extend(robot_arts)

    # Info overlay
    _draw_info(ax)


def _draw_info(ax):
    """Top-left info text."""
    lines = [
        f"Phase: {state.phase}",
        f"Status: {state.status}",
        f"Balls: {len(state.balls)} remaining",
    ]
    if state.plan:
        total = state.plan.get("total_waypoints", 0)
        pruned = state.plan.get("pruned_waypoints", 0)
        if total > 0:
            lines.append(f"Waypoints: {total - pruned}/{total} ({pruned} pruned)")
        if state.phase == 1:
            lines.append(f"Cluster path: {state.plan.get('distance', 0):.2f} m")
            c_size = state.plan.get("cluster_size", 0)
            c_dist = state.plan.get("cluster_min_distance", 0)
            c_score = state.plan.get("cluster_score", 0)
            num_c = state.plan.get("num_clusters", 0)
            lines.append(f"Cluster: {c_size} balls, {c_dist:.1f}m away (score {c_score:.2f})")
            lines.append(f"Clusters found: {num_c}")
        else:
            nn_d = state.plan.get("nn_distance", 0)
            opt_d = state.plan.get("opt_distance", 0)
            imp = state.plan.get("improvement_pct", 0)
            lines.append(f"NN distance: {nn_d:.2f} m")
            lines.append(f"2-opt distance: {opt_d:.2f} m")
            lines.append(f"Improvement: {imp:.1f}%")
    lines.append(f"Replans: {state.replan_count}")

    text = "\n".join(lines)
    txt = ax.text(
        0.02, 0.98, text, transform=ax.transAxes,
        fontsize=9, verticalalignment="top", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85),
        zorder=20,
    )
    state._artists.append(txt)

    # Controls hint (bottom)
    controls = ("Click: place ball | R-click: remove | Space: go | "
                "1/2: phase | s: scatter | r: reset | p: pause | "
                "n: add ball | d: toggle paths")
    ctrl_txt = ax.text(
        0.5, -0.06, controls, transform=ax.transAxes,
        fontsize=7.5, ha="center", color="#666666", zorder=20,
    )
    state._artists.append(ctrl_txt)


# ---------------------------------------------------------------------------
# Ball array helper
# ---------------------------------------------------------------------------

def _ball_array() -> np.ndarray:
    """Return uncollected balls as (N, 2) array."""
    uncollected = [b for i, b in enumerate(state.balls) if i not in state.collected]
    if not uncollected:
        return np.empty((0, 2))
    return np.array(uncollected)


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------

def _set_initial_heading():
    """Point the robot toward the first path segment."""
    if state.smooth_path is not None and len(state.smooth_path) > 1:
        d = state.smooth_path[1] - state.smooth_path[0]
        if np.linalg.norm(d) > 1e-6:
            state.robot_heading = float(np.arctan2(d[1], d[0]))


def do_plan():
    """Plan based on current phase."""
    balls = _ball_array()
    if len(balls) == 0:
        state.status = "done"
        state.plan = None
        state.smooth_path = None
        state.nn_path = None
        state.opt_path = None
        return

    if state.phase == 1:
        result = plan_nearest_cluster(balls, state.robot_pos)
        if result is None:
            state.status = "done"
            return
        state.plan = result
        state.smooth_path = result["path"]
        state.nn_path = None
        state.opt_path = None
        state.path_idx = 0
        state.trail = [state.robot_pos.copy()]
        _set_initial_heading()
        state.status = "executing"

    else:  # Phase 2
        result = plan_full_sweep(balls, state.robot_pos)
        if result is None:
            state.status = "done"
            return
        state.plan = result
        state.nn_path = result["nn_path"]
        state.opt_path = result["opt_path"]
        state.smooth_path = result["opt_path"]
        state.path_idx = 0
        state.trail = [state.robot_pos.copy()]
        _set_initial_heading()
        state.comparison_timer = COMPARISON_PAUSE_SEC
        state.status = "comparing"


def do_replan():
    """Replan from current position (phase-aware)."""
    balls = _ball_array()
    if len(balls) == 0:
        state.status = "done"
        state.smooth_path = None
        state.nn_path = None
        state.opt_path = None
        return

    if state.phase == 1:
        result = plan_nearest_cluster(balls, state.robot_pos)
        if result is None:
            state.status = "done"
            return
        state.plan = result
        state.smooth_path = result["path"]
        state.nn_path = None
        state.opt_path = None
    else:
        result = plan_full_sweep(balls, state.robot_pos)
        if result is None:
            state.status = "done"
            return
        state.plan = result
        state.nn_path = result["nn_path"]
        state.opt_path = result["opt_path"]
        state.smooth_path = result["opt_path"]

    state.path_idx = 0
    state.replan_count += 1
    _set_initial_heading()
    # Continue executing (no comparison pause on replan)
    state.status = "executing"


# ---------------------------------------------------------------------------
# Animation step
# ---------------------------------------------------------------------------

def step(dt: float):
    """Advance simulation by dt seconds."""
    if state.paused or state.status == "idle" or state.status == "done":
        return

    # Comparison pause (Phase 2)
    if state.status == "comparing":
        state.comparison_timer -= dt
        if state.comparison_timer <= 0:
            state.status = "executing"
        return

    if state.status != "executing" or state.smooth_path is None:
        return

    path = state.smooth_path
    if state.path_idx >= len(path) - 1:
        state.status = "done"
        return

    # Move robot along path
    dist_budget = ROBOT_SPEED * dt
    while dist_budget > 0 and state.path_idx < len(path) - 1:
        target = path[state.path_idx + 1]
        to_target = target - state.robot_pos
        d = np.linalg.norm(to_target)

        if d <= dist_budget:
            state.robot_pos = target.copy()
            dist_budget -= d
            state.path_idx += 1
        else:
            direction = to_target / d
            state.robot_pos = state.robot_pos + direction * dist_budget
            dist_budget = 0

    # Update heading
    if state.path_idx < len(path) - 1:
        direction = path[state.path_idx + 1] - state.robot_pos
        if np.linalg.norm(direction) > 1e-6:
            state.robot_heading = float(np.arctan2(direction[1], direction[0]))

    state.trail.append(state.robot_pos.copy())

    # Collect balls within intake range — remove them from the field
    to_remove = []
    for i, b in enumerate(state.balls):
        if i not in state.collected:
            if np.linalg.norm(b - state.robot_pos) < COLLECTION_RADIUS:
                to_remove.append(i)
    for idx in reversed(to_remove):
        state.balls.pop(idx)
        # Remap collected indices
        state.collected = {
            (i - 1 if i > idx else i)
            for i in state.collected if i != idx
        }

    # Check if path finished
    if state.path_idx >= len(path) - 1:
        remaining = _ball_array()
        if len(remaining) > 0 and state.phase in (1, 2):
            do_replan()
        else:
            state.status = "done"


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def on_click(event):
    if event.inaxes is None:
        return

    x, y = event.xdata, event.ydata
    if x is None or y is None:
        return

    if event.button == 1:  # Left click — place ball
        state.balls.append(np.array([x, y]))
    elif event.button == 3:  # Right click — remove nearest ball
        if not state.balls:
            return
        dists = [np.linalg.norm(b - np.array([x, y])) for b in state.balls]
        nearest = int(np.argmin(dists))
        if dists[nearest] < REMOVE_RADIUS:
            state.balls.pop(nearest)
            # Remap collected indices (everything after removed ball shifts down)
            new_collected = set()
            for i in state.collected:
                if i < nearest:
                    new_collected.add(i)
                elif i > nearest:
                    new_collected.add(i - 1)
            state.collected = new_collected


def on_key(event):
    key = event.key

    if key == " ":
        if state.status in ("idle", "done"):
            state.status = "planning"
            do_plan()

    elif key == "1":
        state.phase = 1
        if state.status in ("idle", "done"):
            state.nn_path = None
            state.opt_path = None

    elif key == "2":
        state.phase = 2

    elif key == "s":
        # Scatter random balls
        n = np.random.randint(8, 16)
        for _ in range(n):
            x = np.random.uniform(0.5, FIELD_LENGTH - 0.5)
            y = np.random.uniform(0.5, FIELD_WIDTH - 0.5)
            state.balls.append(np.array([x, y]))

    elif key == "r":
        state.reset()

    elif key == "p":
        state.paused = not state.paused

    elif key == "n":
        # Add a random ball (test replanning)
        x = np.random.uniform(0.5, FIELD_LENGTH - 0.5)
        y = np.random.uniform(0.5, FIELD_WIDTH - 0.5)
        state.balls.append(np.array([x, y]))
        # Trigger replan if executing
        if state.status == "executing" and state.phase in (1, 2):
            do_replan()

    elif key == "d":
        state.show_nn_path = not state.show_nn_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.subplots_adjust(bottom=0.1)
    draw_field(ax)

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)

    dt = 1.0 / FPS

    def animate(_frame):
        step(dt)
        redraw(ax)

    _anim = FuncAnimation(fig, animate, interval=1000 // FPS, cache_frame_data=False)
    plt.show()


if __name__ == "__main__":
    main()
