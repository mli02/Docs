# Ball Collection Path Optimization Plan

## Context

With `GamePieceVision` providing field-relative ball positions (`List<Translation2d>`), we need a system that dynamically plans optimal paths to sweep up balls while shooting on the move. The robot has a wide intake and dual turrets that can track the hub while driving, enabling continuous intake + shoot-on-the-move.

**Key constraint**: Choreo **cannot** generate paths at runtime. PathPlanner **can**, and the codebase already uses it (`TrajectoryFollowerCommand`, `PathPlannerPath`, `BreadHolonomicDriveController`). This plan builds entirely on the existing PathPlanner infrastructure.

**Usage**: Both autonomous routines and driver-triggered teleop (button press).

## Strategy: Cluster-Priority Collection

The robot partitions all visible balls into clusters, scores each cluster by **density relative to travel cost**, collects the best one, then replans and chains to the next. This approach fits FRC constraints:

- **Limited detection range** (~5m) — we never see all balls at once, so a global path is fragile
- **Balls move/disappear** — opponents collect them, they roll, new ones enter FOV
- **Maximizes balls-per-second** — dense nearby clusters yield more points than chasing lone distant balls
- **Lightweight computation** — small clusters mean fast planning, enabling tight replan loops

---

## Architecture

```
GamePieceVision               BallCollectionPlanner           CollectBallsCommand
(ball positions)              (solver + path gen)             (execution + replan)

List<Translation2d> ------>  1. Partition into clusters   +--> PathPlannerPath
                             2. Score: size/(dist+0.5)    |    (best cluster only)
                             3. Order within cluster   ---+
                                (nearest-neighbor)        --> TrajectoryFollowerCommand
                             4. Build PathPlannerPath          (drives the path)
                                                          --> Superstructure.INTAKE_SCORE
                                                               (intake + shoot-on-move)

                             On path completion or replan trigger:
                               Re-detect balls → recluster → score → chain to next
```

---

## 1: `BallCollectionPlanner` — Solver + Path Generator

**New file**: `src/main/java/frc/robot/util/BallCollectionPlanner.java`

Pure utility class (no subsystem state). Takes ball positions, produces a `PathPlannerPath`.

### Clustering

Partition all visible balls into clusters using BFS flood-fill.

**Algorithm**: For each unvisited ball, BFS-expand to all balls within `CLUSTER_RADIUS` (1.5m). Each ball belongs to exactly one cluster.

### Cluster Scoring

Each cluster is scored by: `size / (min_distance_to_robot + 0.5)`

- **Higher = better** — more balls per meter of travel
- **Distance bias (0.5m)** — prevents division-by-zero, roughly equals robot radius so anything within arm's reach scores similarly
- A cluster of 8 balls 3m away scores `8 / 3.5 = 2.29`, beating a lone ball 1m away at `1 / 1.5 = 0.67`

### Ordering Within Cluster

**Algorithm**: Greedy nearest-neighbor.
- Start at robot position
- Pick the nearest unvisited ball, add to ordered list
- Repeat until all balls in the cluster are ordered

For typical cluster sizes (3-8 balls), this runs in microseconds and is near-optimal. 2-opt refinement is unnecessary at this scale.

### PathPlannerPath Generation

```java
public class BallCollectionPlanner {
    private static final double CLUSTER_RADIUS_METERS = 1.5;
    private static final double CLUSTER_DISTANCE_BIAS = 0.5;
    private static final double MAX_VELOCITY = 3.5;        // m/s
    private static final double MAX_ACCELERATION = 3.0;     // m/s^2
    private static final double MAX_ANGULAR_VELOCITY = 2 * Math.PI;
    private static final double MAX_ANGULAR_ACCEL = 4 * Math.PI;

    /**
     * Partition all balls into clusters, score each, and plan a path
     * through the best one. Returns metadata for logging/display.
     */
    public static Optional<ClusterPlan> planBestCluster(
        List<Translation2d> ballPositions,
        Pose2d robotPose) {

        if (ballPositions.isEmpty()) return Optional.empty();

        // 1. Partition into clusters (BFS flood-fill)
        List<List<Translation2d>> clusters = findAllClusters(ballPositions);

        // 2. Score each cluster
        List<Translation2d> bestCluster = null;
        double bestScore = -1;
        double bestMinDist = 0;

        for (List<Translation2d> cluster : clusters) {
            double minDist = cluster.stream()
                .mapToDouble(b -> b.getDistance(robotPose.getTranslation()))
                .min().orElse(Double.MAX_VALUE);
            double score = cluster.size() / (minDist + CLUSTER_DISTANCE_BIAS);
            if (score > bestScore) {
                bestScore = score;
                bestMinDist = minDist;
                bestCluster = cluster;
            }
        }

        // 3. Order by nearest-neighbor
        List<Translation2d> ordered = nearestNeighborOrder(
            bestCluster, robotPose.getTranslation());

        // 4. Build path
        PathPlannerPath path = buildPath(robotPose, ordered);

        return Optional.of(new ClusterPlan(
            path, bestCluster.size(), bestMinDist, bestScore, clusters.size()));
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

        // Non-zero end velocity for smooth chaining to next cluster
        GoalEndState endState = new GoalEndState(0.5, robotPose.getRotation());

        PathPlannerPath path = new PathPlannerPath(
            waypoints, constraints, null, endState
        );
        path.preventFlipping = true;  // positions are already field-absolute
        return path;
    }

    /** BFS flood-fill clustering over all balls. */
    private static List<List<Translation2d>> findAllClusters(
            List<Translation2d> balls) {
        boolean[] visited = new boolean[balls.size()];
        List<List<Translation2d>> clusters = new ArrayList<>();

        for (int seed = 0; seed < balls.size(); seed++) {
            if (visited[seed]) continue;
            List<Translation2d> cluster = new ArrayList<>();
            Deque<Integer> queue = new ArrayDeque<>();
            queue.add(seed);
            visited[seed] = true;

            while (!queue.isEmpty()) {
                int curr = queue.poll();
                cluster.add(balls.get(curr));
                for (int i = 0; i < balls.size(); i++) {
                    if (!visited[i] && balls.get(curr).getDistance(balls.get(i))
                            <= CLUSTER_RADIUS_METERS) {
                        visited[i] = true;
                        queue.add(i);
                    }
                }
            }
            clusters.add(cluster);
        }
        return clusters;
    }
}

/** Result of cluster selection + path planning. */
public record ClusterPlan(
    PathPlannerPath path,
    int clusterSize,
    double minDistance,
    double score,
    int totalClusters
) {}
```

### Intake Width Consideration

The intake is wide, so the robot doesn't need to drive exactly over each ball. PathPlanner generates smooth splines that pass near intermediate waypoints — the intake width provides natural tolerance.

---

## 2: `CollectBallsCommand` — Execution + Cluster Chaining

**New file**: `src/main/java/frc/robot/commands/CollectBallsCommand.java`

The command runs in a loop: plan best cluster -> drive to it -> on completion, replan with remaining balls -> chain to next cluster. Continues until no balls remain or the command is interrupted.

```java
public class CollectBallsCommand extends Command {
    private static final double REPLAN_INTERVAL_SEC = 2.0;
    private static final double REPLAN_BALL_MOVED_THRESHOLD = 0.5; // meters

    private final Robot robot;
    private final GamePieceVision gamePieceVision;
    private final Swerve swerve;
    private final Superstructure superstructure;

    private Command currentPathCommand;
    private List<Translation2d> lastPlannedBalls;
    private Timer replanTimer = new Timer();
    private int replanCount = 0;
    private boolean finished = false;

    // Last plan metadata for logging
    private ClusterPlan lastPlan;

    @Override
    public void initialize() {
        superstructure.setWantedState(SuperState.INTAKE_SCORE);
        replanTimer.reset();
        replanTimer.start();
        replanCount = 0;
        planAndExecute();
    }

    private void planAndExecute() {
        List<Translation2d> balls = gamePieceVision.getDetectedBalls();

        if (balls.isEmpty()) {
            finished = true;
            return;
        }

        Optional<ClusterPlan> plan = BallCollectionPlanner.planBestCluster(
            balls, swerve.getPose()
        );

        if (plan.isPresent()) {
            lastPlan = plan.get();
            lastPlannedBalls = balls;
            currentPathCommand = new TrajectoryFollowerCommand(
                () -> plan.get().path(), swerve, 0.0, robot
            );
            currentPathCommand.initialize();
            logPlan();
        } else {
            finished = true;
        }
    }

    @Override
    public void execute() {
        if (currentPathCommand != null) {
            currentPathCommand.execute();

            // Path finished — chain to next cluster
            if (currentPathCommand.isFinished()) {
                replanFromCurrentState();
                return;
            }
        }

        // Periodic replan check (balls moved/appeared/disappeared)
        if (replanTimer.hasElapsed(REPLAN_INTERVAL_SEC)) {
            replanTimer.reset();
            List<Translation2d> currentBalls = gamePieceVision.getDetectedBalls();
            if (ballsChangedSignificantly(currentBalls, lastPlannedBalls)) {
                replanFromCurrentState();
            }
        }
    }

    private void replanFromCurrentState() {
        if (currentPathCommand != null) currentPathCommand.end(true);
        replanCount++;

        List<Translation2d> balls = gamePieceVision.getDetectedBalls();
        if (balls.isEmpty()) {
            finished = true;
            return;
        }

        Optional<ClusterPlan> plan = BallCollectionPlanner.planBestCluster(
            balls, swerve.getPose()
        );

        if (plan.isPresent()) {
            lastPlan = plan.get();
            lastPlannedBalls = balls;
            currentPathCommand = new TrajectoryFollowerCommand(
                () -> plan.get().path(), swerve,
                swerve.getRobotRelativeSpeeds(),  // smooth handoff
                0.0, robot
            );
            currentPathCommand.initialize();
            logPlan();
        } else {
            finished = true;
        }
    }

    private boolean ballsChangedSignificantly(
            List<Translation2d> current, List<Translation2d> planned) {
        if (current.size() != planned.size()) return true;
        for (Translation2d ball : planned) {
            boolean stillPresent = current.stream()
                .anyMatch(b -> b.getDistance(ball) < REPLAN_BALL_MOVED_THRESHOLD);
            if (!stillPresent) return true;
        }
        return false;
    }

    @Override
    public boolean isFinished() {
        return finished;
    }

    @Override
    public void end(boolean interrupted) {
        if (currentPathCommand != null) currentPathCommand.end(interrupted);
        superstructure.setWantedState(SuperState.IDLE);
        swerve.requestPercent(new ChassisSpeeds(), false);
    }

    private void logPlan() {
        if (lastPlan == null) return;
        Logger.recordOutput("BallCollection/ClusterSize", lastPlan.clusterSize());
        Logger.recordOutput("BallCollection/ClusterDistance", lastPlan.minDistance());
        Logger.recordOutput("BallCollection/ClusterScore", lastPlan.score());
        Logger.recordOutput("BallCollection/TotalClusters", lastPlan.totalClusters());
        Logger.recordOutput("BallCollection/ReplanCount", replanCount);
    }
}
```

**Replan triggers**:
- Current cluster path completed (chain to next best cluster)
- A ball disappeared (collected by opponent or left FOV)
- A new ball appeared (entered camera FOV)
- A ball moved >0.5m from expected position
- Periodic check every ~2s

---

## 3: Integration

### ButtonBindings.java — Teleop Trigger

```java
driverController.rightBumper()
    .whileTrue(new CollectBallsCommand(robot, gamePieceVision, swerve, superstructure));
```

### AutonomousSelector.java — Auto Routine

```java
new SequentialCommandGroup(
    new TrajectoryFollowerCommand(() -> pathToMidfield, swerve, true, 0.0, robot),
    new CollectBallsCommand(robot, gamePieceVision, swerve, superstructure)
)
```

---

## Logging & Visualization

```java
// In BallCollectionPlanner:
Logger.recordOutput("BallCollection/AllBalls", /* Pose2d[] all detected */);
Logger.recordOutput("BallCollection/PlannedOrder", /* Pose2d[] ordered waypoints */);
Logger.recordOutput("BallCollection/PathLength", totalPathDistance);

// In CollectBallsCommand:
Logger.recordOutput("BallCollection/State", /* "PLANNING" | "EXECUTING" | "REPLANNING" | "DONE" */);
Logger.recordOutput("BallCollection/RemainingBalls", gamePieceVision.getDetectedBalls().size());
Logger.recordOutput("BallCollection/ClusterSize", lastPlan.clusterSize());
Logger.recordOutput("BallCollection/ClusterScore", lastPlan.score());
Logger.recordOutput("BallCollection/ReplanCount", replanCount);
```

---

## Key Files to Create

| File | Purpose |
|------|---------|
| `src/.../util/BallCollectionPlanner.java` | Clustering, scoring, NN ordering, path generation |
| `src/.../commands/CollectBallsCommand.java` | Command loop with cluster chaining + replan logic |

## Key Files to Modify

| File | Purpose |
|------|---------|
| `src/.../ButtonBindings.java` | Add teleop binding |
| `src/.../autonomous/AutonomousSelector.java` | Add ball collection auto routines |

## Existing Files Reused (No Changes)

| File | What We Reuse |
|------|--------------|
| `TrajectoryFollowerCommand.java` | Follows PathPlannerPath, already supports startingSpeeds |
| `BreadHolonomicDriveController.java` | PID path following |
| `Superstructure.java` | INTAKE_SCORE state (intake + shoot-on-move) |
| `ShotCalculator.java` | Turret tracking + shoot-on-move |
| `GamePieceVision.java` | `getDetectedBalls()` from detection plan |

---

## Verification

1. **Cluster selection**: Scatter balls — robot should go to the densest/closest cluster, not the single nearest ball
2. **Cluster chaining**: After collecting first cluster, robot automatically replans and chains to next best
3. **Edge cases**: 0 balls (finishes immediately), 1 ball (simple straight path), all balls in one cluster (collects all, done), each ball isolated (degrades to nearest-first)
4. **Mid-drive replan**: Remove/add balls during execution — verify smooth replan with no jerk
5. **AdvantageScope**: Verify cluster selection metadata (size, distance, score, total clusters) logs correctly
6. **Shoot-on-the-move**: Turrets track hub and fire while robot collects

---

## Future Enhancements (Not in scope)

- **Obstacle avoidance**: PathPlanner pathfinding with obstacle zones (other robots)
- **Score-oriented ordering**: Bias toward balls closer to hub
- **Hopper capacity**: Return to shoot when full if shoot-on-the-move isn't working well
- **Adaptive cluster radius**: Widen radius when few balls remain, tighten when field is dense
