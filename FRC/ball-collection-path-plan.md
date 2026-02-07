# Ball Collection Path Optimization Plan

## Context

With `GamePieceVision` providing field-relative ball positions (`List<Translation2d>`), we need a system that dynamically plans optimal paths to sweep up balls while shooting on the move. The robot has a wide intake and dual turrets that can track the hub while driving, so the strategy is: drive continuous sweep paths through **clusters** of balls, intake them, and shoot simultaneously. After sweeping a cluster, re-snapshot the field and replan for the next group.

**Key constraint**: Choreo **cannot** generate paths at runtime. PathPlanner **can**, and the codebase already uses it (`TrajectoryFollowerCommand`, `PathPlannerPath`, `BreadHolonomicDriveController`). This plan builds entirely on the existing PathPlanner infrastructure.

**Usage**: Both autonomous routines and driver-triggered teleop (button press).

---

## Architecture Overview

```
GamePieceVision                    BallCollectionPlanner              CollectBallsCommand
(ball positions)                   (solver + path gen)                (command execution)

List<Translation2d> ------->  1. Cluster nearby balls          +--> Generate PathPlannerPath
                              2. Order clusters (greedy)       |    for current cluster
                              3. Generate sweep waypoints  ----+
                              4. Return PathPlannerPath         --> TrajectoryFollowerCommand
                                                                    (drives the path)
                                                               --> Superstructure.INTAKE_SCORE
                                                                    (intake + shoot-on-move)
                              After cluster complete:
                              Re-snapshot --- replan next cluster --> repeat
```

---

## Step 1: `BallCollectionPlanner` -- Solver + Path Generator

**New file**: `src/main/java/frc/robot/util/BallCollectionPlanner.java`

This is a pure utility class (no subsystem state). It takes ball positions and produces a `PathPlannerPath`.

### 1A. Ball Clustering

Group nearby balls so the robot sweeps through clusters in one motion rather than zigzagging to individual balls.

**Algorithm**: Simple distance-based clustering.
- Pick the ball closest to the robot as the seed
- Add all balls within `CLUSTER_RADIUS` (e.g., 1.5m) of any ball already in the cluster
- Repeat until no more balls can be added to this cluster
- The remaining balls form future clusters (replanned after this cluster is collected)

```java
public class BallCollectionPlanner {
    private static final double CLUSTER_RADIUS_METERS = 1.5;
    private static final double MAX_VELOCITY = 3.5;        // m/s
    private static final double MAX_ACCELERATION = 3.0;     // m/s^2
    private static final double MAX_ANGULAR_VELOCITY = 2 * Math.PI;
    private static final double MAX_ANGULAR_ACCEL = 4 * Math.PI;

    /**
     * Given all detected balls and the robot's current pose, plan a path
     * through the nearest cluster of balls.
     */
    public static Optional<PathPlannerPath> planNextCluster(
        List<Translation2d> ballPositions,
        Pose2d robotPose,
        RobotConfig robotConfig) { ... }
}
```

### 1B. Waypoint Ordering Within a Cluster

Once we have a cluster of balls, order them to minimize travel distance.

**Algorithm**: Greedy nearest-neighbor starting from robot position.
- Start at robot pose
- Pick the nearest unvisited ball, add to ordered list
- Repeat until all balls in the cluster are ordered

For typical cluster sizes (3-8 balls), greedy nearest-neighbor is near-optimal and runs in microseconds. No need for full TSP.

### 1C. PathPlannerPath Generation

Convert the ordered ball positions into a `PathPlannerPath` for the `TrajectoryFollowerCommand`:

```java
private static PathPlannerPath buildPath(
    Pose2d robotPose,
    List<Translation2d> orderedBalls) {

    // Build Pose2d list: robot position + each ball
    // Rotation component = direction of travel (tangent heading)
    List<Pose2d> poses = new ArrayList<>();

    Translation2d current = robotPose.getTranslation();
    poses.add(robotPose);

    for (Translation2d ball : orderedBalls) {
        // Direction of travel = heading toward this ball from previous point
        Rotation2d heading = ball.minus(current).getAngle();
        poses.add(new Pose2d(ball, heading));
        current = ball;
    }

    List<Waypoint> waypoints = PathPlannerPath.waypointsFromPoses(poses);
    PathConstraints constraints = new PathConstraints(
        MAX_VELOCITY, MAX_ACCELERATION,
        MAX_ANGULAR_VELOCITY, MAX_ANGULAR_ACCEL
    );

    // End at low speed (not zero -- robot continues to next cluster)
    // Holonomic rotation: face intake direction (robot forward)
    GoalEndState endState = new GoalEndState(
        0.5,  // slow but not stopped
        robotPose.getRotation()  // maintain current heading
    );

    PathPlannerPath path = new PathPlannerPath(
        waypoints, constraints, null, endState
    );
    path.preventFlipping = true;  // positions are already field-absolute
    return path;
}
```

### 1D. Intake Width Consideration

The intake is wide, so the robot doesn't need to drive exactly over each ball -- just close enough. Waypoints can be placed at ball positions directly since PathPlanner generates smooth splines that pass near (not necessarily through) intermediate waypoints. The intake width provides natural tolerance.

---

## Step 2: `CollectBallsCommand` -- Command Execution Loop

**New file**: `src/main/java/frc/robot/commands/CollectBallsCommand.java`

A command that repeatedly: snapshot -> plan cluster -> execute sweep -> replan.

```java
public class CollectBallsCommand extends Command {
    private final Robot robot;
    private final GamePieceVision gamePieceVision;
    private final Swerve swerve;
    private final Superstructure superstructure;

    private Command currentPathCommand;
    private boolean finished = false;

    @Override
    public void initialize() {
        // Set Superstructure to INTAKE_SCORE (intake + track hub + shoot when ready)
        superstructure.setWantedState(SuperState.INTAKE_SCORE);
        planNextCluster();
    }

    @Override
    public void execute() {
        // If current path command finished, plan next cluster
        if (currentPathCommand == null || currentPathCommand.isFinished()) {
            currentPathCommand.end(false);
            planNextCluster();
        }

        // Run the current path command
        if (currentPathCommand != null) {
            currentPathCommand.execute();
        }
    }

    private void planNextCluster() {
        List<Translation2d> balls = gamePieceVision.getDetectedBalls();

        if (balls.isEmpty()) {
            finished = true;
            return;
        }

        Optional<PathPlannerPath> path = BallCollectionPlanner.planNextCluster(
            balls, swerve.getPose(), robot.robotConfig
        );

        if (path.isPresent()) {
            currentPathCommand = new TrajectoryFollowerCommand(
                () -> path.get(), swerve, 0.0, robot
            );
            currentPathCommand.initialize();
        } else {
            finished = true;
        }
    }

    @Override
    public boolean isFinished() {
        return finished;
    }

    @Override
    public void end(boolean interrupted) {
        if (currentPathCommand != null) {
            currentPathCommand.end(true);
        }
        superstructure.setWantedState(SuperState.IDLE);
        swerve.requestPercent(new ChassisSpeeds(), false);
    }
}
```

**Lifecycle**:
1. `initialize()`: Set Superstructure to INTAKE_SCORE, plan first cluster
2. `execute()`: Run current path. When path completes, re-snapshot balls and plan next cluster
3. `isFinished()`: True when no more balls are detected
4. `end()`: Stop driving, return Superstructure to IDLE

### Why Replan Per-Cluster (Not Per-Ball or Continuously)

- **Per-ball replanning**: Wasteful -- the intake is wide, you're collecting multiple balls per sweep
- **Continuous replanning**: Risks oscillating between plans, computationally heavier
- **Per-cluster replanning**: Natural breakpoint. After sweeping a cluster, the field state has changed (balls collected, maybe new ones visible). Replanning here gives fresh information without thrashing.

---

## Step 3: Integration Points

### Robot.java -- Wire Up

```java
// In robotPeriodic() -- already handled by GamePieceVision.updateInputs()
// No additional wiring needed beyond what the detection plan already provides
```

### ButtonBindings.java -- Teleop Trigger

```java
// Bind to driver button (e.g., right bumper)
driverController.rightBumper()
    .whileTrue(new CollectBallsCommand(robot, gamePieceVision, swerve, superstructure));
```

Using `whileTrue` so the command runs while the button is held and cancels when released -- giving the driver full control.

### AutonomousSelector.java -- Auto Routine

```java
// Example auto: drive to midfield, then collect all visible balls
new SequentialCommandGroup(
    new TrajectoryFollowerCommand(() -> pathToMidfield, swerve, true, 0.0, robot),
    new CollectBallsCommand(robot, gamePieceVision, swerve, superstructure)
)
```

---

## Step 4: Logging & Visualization

Log everything for AdvantageScope debugging:

```java
// In BallCollectionPlanner:
Logger.recordOutput("BallCollection/ClusterBalls", /* Pose2d[] of balls in current cluster */);
Logger.recordOutput("BallCollection/PlannedPath", /* Pose2d[] of waypoints */);
Logger.recordOutput("BallCollection/ClusterCount", clusterSize);

// In CollectBallsCommand:
Logger.recordOutput("BallCollection/State", /* "PLANNING" | "EXECUTING" | "REPLANNING" | "DONE" */);
Logger.recordOutput("BallCollection/RemainingBalls", gamePieceVision.getDetectedBalls().size());
```

In AdvantageScope: Ball positions render as markers on the field, planned path renders as a line. This makes it easy to debug cluster selection and path quality.

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `src/.../util/BallCollectionPlanner.java` | **Create** -- Clustering, ordering, PathPlannerPath generation |
| `src/.../commands/CollectBallsCommand.java` | **Create** -- Command loop: snapshot -> plan -> execute -> replan |

## Key Files to Modify

| File | Purpose |
|------|---------|
| `src/.../ButtonBindings.java` | **Modify** -- Add teleop binding for CollectBallsCommand |
| `src/.../autonomous/AutonomousSelector.java` | **Modify** -- Add ball collection auto routines |

## Existing Files Reused (No Changes Needed)

| File | What We Reuse |
|------|--------------|
| `TrajectoryFollowerCommand.java` | Follows the generated PathPlannerPath -- no changes |
| `BreadHolonomicDriveController.java` | PID controller for path following -- no changes |
| `Superstructure.java` | INTAKE_SCORE state already handles intake + shoot-on-move |
| `ShotCalculator.java` | Turret tracking + shoot-on-move -- no changes |
| `GamePieceVision.java` | Provides `getDetectedBalls()` -- from detection plan |

---

## Simulation & Verification

1. **Simulation test**: In MapleSim, verify `GamePieceVisionIOSim` detects balls -> `BallCollectionPlanner` generates valid paths -> robot drives to balls
2. **Cluster test**: Place 10+ balls in simulation, verify clustering groups nearby balls correctly and ordering minimizes travel
3. **Replan test**: Remove balls mid-execution (simulate another robot picking them up), verify the command replans correctly
4. **Shoot-on-move test**: Verify Superstructure INTAKE_SCORE state works during path following -- turrets track hub, balls are fired as they're loaded
5. **AdvantageScope**: Visualize planned paths overlaid on ball positions, verify they look reasonable
6. **Edge cases**:
   - 0 balls detected -> command finishes immediately
   - 1 ball detected -> simple drive-to-ball path
   - All balls in one cluster -> single sweep, no replanning
   - Balls spread across field -> multiple clusters, sequential sweeps

---

## Future Enhancements (Not in scope)

- **Obstacle avoidance**: Use PathPlanner's pathfinding with obstacle zones (other robots)
- **Score-oriented ordering**: Prioritize balls closer to the hub to minimize travel after collection
- **Multi-robot coordination**: If alliance partner has ball detection, coordinate who collects which balls
- **Hopper capacity**: Track balls in hopper, return to shoot when full instead of continuous SOTM
