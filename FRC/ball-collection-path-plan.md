# Ball Collection Path Optimization Plan

## Context

With `GamePieceVision` providing field-relative ball positions (`List<Translation2d>`), we need a system that dynamically plans optimal paths to sweep up balls while shooting on the move. The robot has a wide intake and dual turrets that can track the hub while driving, enabling continuous intake + shoot-on-the-move.

**Key constraint**: Choreo **cannot** generate paths at runtime. PathPlanner **can**, and the codebase already uses it (`TrajectoryFollowerCommand`, `PathPlannerPath`, `BreadHolonomicDriveController`). This plan builds entirely on the existing PathPlanner infrastructure.

**Usage**: Both autonomous routines and driver-triggered teleop (button press).

**This plan is implemented in two phases:**
1. **Phase 1**: Drive to the nearest cluster of balls and stop. Get the core pipeline working end-to-end.
2. **Phase 2**: Generate one smooth continuous path through ALL balls with shoot-on-the-move, and seamless mid-path replanning.

---

# Phase 1: Drive to Nearest Cluster

Goal: Get the full pipeline working — vision detects balls, planner generates a path, robot drives to them. Simple, testable, no shoot-on-the-move yet.

## Architecture (Phase 1)

```
GamePieceVision               BallCollectionPlanner           CollectBallsCommand
(ball positions)              (solver + path gen)             (command execution)

List<Translation2d> ------>  1. Cluster nearby balls     +--> PathPlannerPath
                             2. Order within cluster     |    (nearest cluster only)
                                (nearest-neighbor)   ----+
                             3. Build PathPlannerPath     --> TrajectoryFollowerCommand
                                                              (drives the path, stops)
                                                         --> Superstructure.INTAKE
                                                              (intake only, no shooting)
```

## 1.1: `BallCollectionPlanner` -- Solver + Path Generator

**New file**: `src/main/java/frc/robot/util/BallCollectionPlanner.java`

Pure utility class (no subsystem state). Takes ball positions, produces a `PathPlannerPath`.

### Clustering

Group nearby balls so the robot sweeps through a cluster in one motion.

**Algorithm**: Distance-based flood-fill clustering.
- Pick the ball closest to the robot as the seed
- Add all balls within `CLUSTER_RADIUS` (e.g., 1.5m) of any ball already in the cluster
- Repeat until no more balls can be added
- Return only this cluster (remaining balls handled by replan in Phase 2)

### Ordering Within Cluster

**Algorithm**: Greedy nearest-neighbor.
- Start at robot position
- Pick the nearest unvisited ball, add to ordered list
- Repeat until all balls in the cluster are ordered

For typical cluster sizes (3-8 balls), this runs in microseconds and is near-optimal.

### PathPlannerPath Generation

```java
public class BallCollectionPlanner {
    private static final double CLUSTER_RADIUS_METERS = 1.5;
    private static final double MAX_VELOCITY = 3.5;        // m/s
    private static final double MAX_ACCELERATION = 3.0;     // m/s^2
    private static final double MAX_ANGULAR_VELOCITY = 2 * Math.PI;
    private static final double MAX_ANGULAR_ACCEL = 4 * Math.PI;

    /**
     * Plan a path through the nearest cluster of balls.
     * Returns empty if no balls detected.
     */
    public static Optional<PathPlannerPath> planNextCluster(
        List<Translation2d> ballPositions,
        Pose2d robotPose) {

        if (ballPositions.isEmpty()) return Optional.empty();

        // 1. Find nearest cluster
        List<Translation2d> cluster = findNearestCluster(ballPositions, robotPose);

        // 2. Order by nearest-neighbor
        List<Translation2d> ordered = nearestNeighborOrder(cluster, robotPose.getTranslation());

        // 3. Build path
        return Optional.of(buildPath(robotPose, ordered));
    }

    private static PathPlannerPath buildPath(
            Pose2d robotPose, List<Translation2d> orderedBalls) {

        List<Pose2d> poses = new ArrayList<>();
        Translation2d current = robotPose.getTranslation();
        poses.add(robotPose);

        for (Translation2d ball : orderedBalls) {
            // Rotation = direction of travel (spline tangent), NOT robot heading
            Rotation2d heading = ball.minus(current).getAngle();
            poses.add(new Pose2d(ball, heading));
            current = ball;
        }

        List<Waypoint> waypoints = PathPlannerPath.waypointsFromPoses(poses);
        PathConstraints constraints = new PathConstraints(
            MAX_VELOCITY, MAX_ACCELERATION,
            MAX_ANGULAR_VELOCITY, MAX_ANGULAR_ACCEL
        );

        // Phase 1: stop at the end of the cluster
        GoalEndState endState = new GoalEndState(0.0, robotPose.getRotation());

        PathPlannerPath path = new PathPlannerPath(
            waypoints, constraints, null, endState
        );
        path.preventFlipping = true;  // positions are already field-absolute
        return path;
    }
}
```

### Intake Width Consideration

The intake is wide, so the robot doesn't need to drive exactly over each ball. PathPlanner generates smooth splines that pass near intermediate waypoints — the intake width provides natural tolerance.

## 1.2: `CollectBallsCommand` -- Phase 1 (Single Cluster)

**New file**: `src/main/java/frc/robot/commands/CollectBallsCommand.java`

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
        superstructure.setWantedState(SuperState.INTAKE);
        planAndExecute();
    }

    private void planAndExecute() {
        List<Translation2d> balls = gamePieceVision.getDetectedBalls();

        if (balls.isEmpty()) {
            finished = true;
            return;
        }

        Optional<PathPlannerPath> path = BallCollectionPlanner.planNextCluster(
            balls, swerve.getPose()
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
    public void execute() {
        if (currentPathCommand != null) {
            currentPathCommand.execute();
        }
    }

    @Override
    public boolean isFinished() {
        return finished
            || (currentPathCommand != null && currentPathCommand.isFinished());
    }

    @Override
    public void end(boolean interrupted) {
        if (currentPathCommand != null) currentPathCommand.end(interrupted);
        superstructure.setWantedState(SuperState.IDLE);
        swerve.requestPercent(new ChassisSpeeds(), false);
    }
}
```

## 1.3: Integration

### ButtonBindings.java -- Teleop Trigger

```java
driverController.rightBumper()
    .whileTrue(new CollectBallsCommand(robot, gamePieceVision, swerve, superstructure));
```

### AutonomousSelector.java -- Auto Routine

```java
new SequentialCommandGroup(
    new TrajectoryFollowerCommand(() -> pathToMidfield, swerve, true, 0.0, robot),
    new CollectBallsCommand(robot, gamePieceVision, swerve, superstructure)
)
```

## 1.4: Phase 1 Verification

1. **Sim test**: Place a cluster of 3-5 balls in MapleSim, verify robot drives to them
2. **Edge cases**: 0 balls (finishes immediately), 1 ball (simple straight path), balls in a line, balls in a tight group
3. **AdvantageScope**: Verify planned path overlaid on ball positions looks correct
4. **Intake test**: Verify Superstructure INTAKE state runs while path is followed

---

# Phase 2: Smooth Continuous Path Through All Balls

Goal: One smooth path through ALL visible balls, shoot-on-the-move, and seamless mid-drive replanning.

## Architecture (Phase 2)

```
GamePieceVision                BallCollectionPlanner              CollectBallsCommand
(ball positions)               (solver + path gen)                (execution + replan)

List<Translation2d> ------>  1. Order ALL balls              +--> ONE PathPlannerPath
                                (nearest-neighbor + 2-opt)   |    through all balls
                             2. Build single smooth path ----+
                                                              --> TrajectoryFollowerCommand
                                                                   (continuous drive)
                                                              --> Superstructure.INTAKE_SCORE
                                                                   (intake + shoot-on-move)

                             Periodic replan check (every ~2s):
                             If balls moved significantly:
                               Replan from current pose + current velocity
                               --> seamless trajectory handoff
```

## 2.1: Upgraded Ordering — Nearest-Neighbor + 2-Opt

Phase 1 uses pure nearest-neighbor. Phase 2 adds **2-opt refinement** to eliminate path crossings.

### Why 2-Opt Over Full TSP

| Algorithm | Complexity | Quality | Notes |
|-----------|-----------|---------|-------|
| Nearest-neighbor | O(N^2) | ~75-80% optimal | Fast, can produce crossing paths |
| NN + 2-opt | O(N^2) per pass | ~95%+ optimal | Eliminates crossings, fast enough |
| Held-Karp (exact DP) | O(2^N * N^2) | 100% optimal | Feasible for N<=15, overkill |

**2-opt** iteratively improves the path: pick two edges, check if swapping their endpoints shortens the total distance. Repeat until no improving swap exists.

```java
/**
 * Improve a tour by repeatedly swapping pairs of edges.
 * Eliminates path crossings, which are the main source of wasted distance.
 */
private static List<Translation2d> twoOptImprove(List<Translation2d> tour) {
    boolean improved = true;
    while (improved) {
        improved = false;
        for (int i = 0; i < tour.size() - 1; i++) {
            for (int j = i + 2; j < tour.size(); j++) {
                double currentDist = dist(tour, i, i+1) + dist(tour, j, j+1);
                double swappedDist = dist(tour, i, j) + dist(tour, i+1, j+1);
                if (swappedDist < currentDist) {
                    // Reverse the segment between i+1 and j
                    Collections.reverse(tour.subList(i + 1, j + 1));
                    improved = true;
                }
            }
        }
    }
    return tour;
}
```

For N=15 balls, 2-opt converges in ~5-20 iterations and runs in <1ms. Combined with nearest-neighbor as the seed, this produces excellent paths.

## 2.2: Single Smooth Path Through All Balls

Instead of cluster-by-cluster, generate ONE `PathPlannerPath` through all detected balls:

```java
public static Optional<PathPlannerPath> planFullSweep(
        List<Translation2d> ballPositions,
        Pose2d robotPose) {

    if (ballPositions.isEmpty()) return Optional.empty();

    // 1. Order all balls: nearest-neighbor seed + 2-opt refinement
    List<Translation2d> ordered = nearestNeighborOrder(ballPositions, robotPose.getTranslation());
    ordered = twoOptImprove(ordered);

    // 2. Build one smooth path through all of them
    return Optional.of(buildSweepPath(robotPose, ordered));
}

private static PathPlannerPath buildSweepPath(
        Pose2d robotPose, List<Translation2d> orderedBalls) {

    List<Pose2d> poses = new ArrayList<>();
    Translation2d current = robotPose.getTranslation();
    poses.add(robotPose);

    for (Translation2d ball : orderedBalls) {
        Rotation2d heading = ball.minus(current).getAngle();
        poses.add(new Pose2d(ball, heading));
        current = ball;
    }

    List<Waypoint> waypoints = PathPlannerPath.waypointsFromPoses(poses);
    PathConstraints constraints = new PathConstraints(
        MAX_VELOCITY, MAX_ACCELERATION,
        MAX_ANGULAR_VELOCITY, MAX_ANGULAR_ACCEL
    );

    // Non-zero end velocity -- robot can keep moving if replanned
    GoalEndState endState = new GoalEndState(0.5, robotPose.getRotation());

    PathPlannerPath path = new PathPlannerPath(
        waypoints, constraints, null, endState
    );
    path.preventFlipping = true;
    return path;
}
```

## 2.3: Seamless Mid-Drive Replanning

The key insight: `path.generateTrajectory(currentSpeeds, currentRotation, robotConfig)` takes the current `ChassisSpeeds` as input. So replanning from the current position at the current velocity produces a **smooth handoff** — no jerk, no stopping.

```java
// In CollectBallsCommand (Phase 2 version):

private static final double REPLAN_INTERVAL_SEC = 2.0;
private static final double REPLAN_BALL_MOVED_THRESHOLD = 0.5; // meters

@Override
public void execute() {
    if (currentPathCommand != null) {
        currentPathCommand.execute();
    }

    // Check if we should replan
    if (replanTimer.hasElapsed(REPLAN_INTERVAL_SEC)) {
        replanTimer.reset();

        List<Translation2d> currentBalls = gamePieceVision.getDetectedBalls();
        if (ballsChangedSignificantly(currentBalls, lastPlannedBalls)) {
            // Replan from current pose + current velocity = smooth handoff
            replanFromCurrentState(currentBalls);
        }
    }
}

private void replanFromCurrentState(List<Translation2d> balls) {
    if (currentPathCommand != null) currentPathCommand.end(true);

    Optional<PathPlannerPath> path = BallCollectionPlanner.planFullSweep(
        balls, swerve.getPose()
    );

    if (path.isPresent()) {
        // Use CURRENT speeds for smooth transition
        currentPathCommand = new TrajectoryFollowerCommand(
            () -> path.get(), swerve,
            swerve.getRobotRelativeSpeeds(),  // smooth handoff
            0.0, robot
        );
        currentPathCommand.initialize();
        lastPlannedBalls = balls;
    }
}

private boolean ballsChangedSignificantly(
        List<Translation2d> current, List<Translation2d> planned) {
    // Replan if: ball count changed, or any ball moved > threshold
    if (current.size() != planned.size()) return true;
    for (Translation2d ball : planned) {
        boolean stillPresent = current.stream()
            .anyMatch(b -> b.getDistance(ball) < REPLAN_BALL_MOVED_THRESHOLD);
        if (!stillPresent) return true;
    }
    return false;
}
```

**Replan triggers**:
- A ball disappeared (collected by another robot or left the field)
- A new ball appeared (entered camera FOV)
- A ball moved >0.5m from its expected position (kicked by another robot)
- Current path completed (all planned balls swept)

## 2.4: Shoot-On-The-Move Integration

Phase 2 uses `SuperState.INTAKE_SCORE` instead of `INTAKE`:

```java
@Override
public void initialize() {
    // Intake balls + track hub + shoot automatically when loaded
    superstructure.setWantedState(SuperState.INTAKE_SCORE);
    planFullSweep();
}
```

The existing `Superstructure.intaking_scoring()` already handles this:
- `robot.intake.requestIntake()` runs the intake
- `shotCalculator.calculate(hubLocation)` tracks the hub with turrets
- `readyToShoot()` checks all subsystem tolerances
- When ready, the indexer fires automatically

No changes needed to `Superstructure`, `ShotCalculator`, or turret/hood/shooter subsystems.

---

## Logging & Visualization (Both Phases)

```java
// In BallCollectionPlanner:
Logger.recordOutput("BallCollection/AllBalls", /* Pose2d[] all detected */);
Logger.recordOutput("BallCollection/PlannedOrder", /* Pose2d[] ordered waypoints */);
Logger.recordOutput("BallCollection/PathLength", totalPathDistance);

// In CollectBallsCommand:
Logger.recordOutput("BallCollection/Phase", /* "PHASE1_CLUSTER" | "PHASE2_SWEEP" */);
Logger.recordOutput("BallCollection/State", /* "PLANNING" | "EXECUTING" | "REPLANNING" | "DONE" */);
Logger.recordOutput("BallCollection/RemainingBalls", gamePieceVision.getDetectedBalls().size());
Logger.recordOutput("BallCollection/ReplanCount", replanCount);
```

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `src/.../util/BallCollectionPlanner.java` | **Create** -- Clustering, NN ordering, 2-opt, path generation |
| `src/.../commands/CollectBallsCommand.java` | **Create** -- Command loop with replan logic |

## Key Files to Modify

| File | Purpose |
|------|---------|
| `src/.../ButtonBindings.java` | **Modify** -- Add teleop binding |
| `src/.../autonomous/AutonomousSelector.java` | **Modify** -- Add ball collection auto routines |

## Existing Files Reused (No Changes)

| File | What We Reuse |
|------|--------------|
| `TrajectoryFollowerCommand.java` | Follows PathPlannerPath, already supports startingSpeeds |
| `BreadHolonomicDriveController.java` | PID path following |
| `Superstructure.java` | INTAKE and INTAKE_SCORE states |
| `ShotCalculator.java` | Turret tracking + shoot-on-move |
| `GamePieceVision.java` | `getDetectedBalls()` from detection plan |

---

## Verification

### Phase 1
1. Place 3-5 balls in MapleSim cluster -> robot drives to them and stops
2. Test 0, 1, and many balls
3. Verify AdvantageScope shows planned path correctly

### Phase 2
1. Place 10+ balls spread across field -> robot drives one smooth sweep through all
2. Remove balls mid-drive -> verify smooth replan (no jerk)
3. Verify turrets track hub and balls are shot while driving
4. Compare NN-only vs NN+2-opt paths in AdvantageScope (2-opt should eliminate crossings)
5. Measure total sweep time vs naive approach

---

## Future Enhancements (Not in scope)

- **Obstacle avoidance**: PathPlanner pathfinding with obstacle zones (other robots)
- **Score-oriented ordering**: Bias toward balls closer to hub
- **Hopper capacity**: Return to shoot when full if SOTM isn't working well
- **Exact TSP (Held-Karp)**: Only if 2-opt quality proves insufficient (unlikely)
