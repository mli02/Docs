"""
FRC field constants and matplotlib drawing utilities.

Every draw_* function returns the artist(s) it created so callers can
remove/update them later.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ---------------------------------------------------------------------------
# Field constants (meters)
# ---------------------------------------------------------------------------
FIELD_LENGTH = 16.5
FIELD_WIDTH = 8.1
ROBOT_RADIUS = 0.45
BALL_RADIUS = 0.12
INTAKE_WIDTH = 0.9
ROBOT_SIZE = ROBOT_RADIUS * 2  # side length of the square robot

# Colors
FIELD_COLOR = "#e8e8e8"
FIELD_BORDER_COLOR = "#555555"
BALL_COLOR = "#ffb800"          # gold
BALL_COLLECTED_COLOR = "#aaaaaa"
ROBOT_COLOR = "#3080d0"
INTAKE_COLOR = "#60c060"
NN_PATH_COLOR = "#cc3333"       # red
OPT_PATH_COLOR = "#22aa44"      # green
CLUSTER_HIGHLIGHT = "#ffe066"


# ---------------------------------------------------------------------------
# Drawing functions
# ---------------------------------------------------------------------------

def draw_field(ax: plt.Axes):
    """Draw the field outline, center line, and configure axes."""
    ax.set_xlim(-0.5, FIELD_LENGTH + 0.5)
    ax.set_ylim(-0.5, FIELD_WIDTH + 0.5)
    ax.set_aspect("equal")
    ax.set_facecolor(FIELD_COLOR)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")

    # Field border
    rect = patches.Rectangle(
        (0, 0), FIELD_LENGTH, FIELD_WIDTH,
        linewidth=2, edgecolor=FIELD_BORDER_COLOR, facecolor="none",
    )
    ax.add_patch(rect)

    # Center line
    ax.plot(
        [FIELD_LENGTH / 2, FIELD_LENGTH / 2], [0, FIELD_WIDTH],
        color=FIELD_BORDER_COLOR, linewidth=1, linestyle="--", alpha=0.4,
    )

    ax.set_title("Ball Collection Path Simulator", fontsize=12, fontweight="bold")


def draw_robot(ax: plt.Axes, x: float, y: float, heading: float):
    """Draw the robot as a blue square with heading arrow and intake zone.

    Returns list of artists.
    """
    artists = []

    # Robot body (rotated square)
    half = ROBOT_SIZE / 2
    corners = np.array([[-half, -half], [half, -half],
                        [half, half], [-half, half]])
    cos_h, sin_h = np.cos(heading), np.sin(heading)
    rot = np.array([[cos_h, -sin_h], [sin_h, cos_h]])
    corners = corners @ rot.T + np.array([x, y])
    body = patches.Polygon(corners, closed=True,
                           facecolor=ROBOT_COLOR, edgecolor="black",
                           linewidth=1.5, alpha=0.85, zorder=10)
    ax.add_patch(body)
    artists.append(body)

    # Heading arrow
    arrow_len = ROBOT_SIZE * 0.7
    dx, dy = arrow_len * cos_h, arrow_len * sin_h
    arrow = ax.annotate(
        "", xy=(x + dx, y + dy), xytext=(x, y),
        arrowprops=dict(arrowstyle="->", color="white", lw=2),
        zorder=11,
    )
    artists.append(arrow)

    # Intake zone (green rectangle at front)
    intake_half_w = INTAKE_WIDTH / 2
    intake_depth = 0.15
    intake_corners = np.array([
        [half, -intake_half_w],
        [half + intake_depth, -intake_half_w],
        [half + intake_depth, intake_half_w],
        [half, intake_half_w],
    ])
    intake_corners = intake_corners @ rot.T + np.array([x, y])
    intake = patches.Polygon(intake_corners, closed=True,
                             facecolor=INTAKE_COLOR, edgecolor="black",
                             linewidth=1, alpha=0.7, zorder=10)
    ax.add_patch(intake)
    artists.append(intake)

    return artists


def draw_ball(ax: plt.Axes, x: float, y: float, collected: bool = False):
    """Draw a ball. Gold if uncollected, gray if collected. Returns artist."""
    color = BALL_COLLECTED_COLOR if collected else BALL_COLOR
    edge = "#888888" if collected else "#cc8800"
    alpha = 0.4 if collected else 1.0
    circle = patches.Circle(
        (x, y), BALL_RADIUS * 2,  # visual radius slightly larger for visibility
        facecolor=color, edgecolor=edge, linewidth=1.2,
        alpha=alpha, zorder=5,
    )
    ax.add_patch(circle)
    return circle


def draw_path(ax: plt.Axes, points: np.ndarray, color: str = "blue",
              linestyle: str = "-", label: str = None, linewidth: float = 2.0,
              marker_color: str = None):
    """Draw a path polyline with optional waypoint markers. Returns artists."""
    if len(points) < 2:
        return []

    artists = []
    line, = ax.plot(
        points[:, 0], points[:, 1],
        color=color, linestyle=linestyle, linewidth=linewidth,
        label=label, alpha=0.8, zorder=4,
    )
    artists.append(line)

    if marker_color:
        scatter = ax.scatter(
            points[:, 0], points[:, 1],
            color=marker_color, s=30, zorder=6, edgecolors="black", linewidth=0.5,
        )
        artists.append(scatter)

    return artists
