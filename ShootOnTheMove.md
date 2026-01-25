# FRC Shoot-on-the-Move Guide

**Covers:** Java (WPILib) | Swerve with Turret | Swerve without Turret

---

## Table of Contents

1. [Introduction & Conceptual Foundation](#1-introduction--conceptual-foundation)  
2. [The Core Math](#2-the-core-math)  
3. [System Prerequisites](#3-system-prerequisites)  
4. [Implementation Approaches](#4-implementation-approaches)  
5. [Code Architecture](#5-code-architecture)  
6. [Lookup Table Creation & Tuning](#6-lookup-table-creation--tuning)  
7. [Turret vs. Non-Turret Implementations](#7-turret-vs-non-turret-implementations)  
8. [Latency Compensation](#8-latency-compensation)  
9. [Testing & Validation Protocol](#9-testing--validation-protocol)  
10. [Common Pitfalls & Debugging](#10-common-pitfalls--debugging)  
11. [Advanced Topics](#11-advanced-topics)  
12. [Reference Resources](#12-reference-resources)

---

## 1\. Introduction & Conceptual Foundation

### Why Is Shooting While Moving Different?

When your robot is stationary and shoots a game piece, the projectile travels in a predictable arc toward the target. But when your robot is moving, something fundamentally changes: **the projectile inherits your robot's velocity**.

Think of it like throwing a ball from a moving car. If you throw the ball straight forward, it doesn't just move at your throwing speed, it moves at your throwing speed *plus* the car's speed. The same principle applies to your shooter.

### The Two Key Effects

When shooting while moving, you need to compensate for two things:

#### 1\. Aiming Offset (Where to Point)

From your robot's reference frame, the target appears to move in the **opposite direction** of your robot's motion. If you're driving left, the target appears to drift right relative to your robot. You need to "lead" the target by aiming where it will be when the projectile arrives, not where it is now.

#### 2\. Velocity Adjustment (How Hard to Shoot)

The projectile's actual launch velocity is the vector sum of your shooter's velocity and your robot's velocity. Depending on your direction of motion:

- Moving toward the target → projectile is faster → may overshoot  
- Moving away from the target → projectile is slower → may undershoot  
- Moving laterally → projectile curves to the side

### The Mental Model: Virtual Target

The simplest way to think about shoot-on-the-move is the **virtual target** concept:

```
Instead of aiming at the actual target, calculate where you
WOULD need to aim if you were stationary to hit the same spot.
This offset position is your "virtual target."
```

Once you have the virtual target position, you can use all your existing static shooting code, lookup tables, trajectory calculations, etc: as if you were standing still. 

### Diagram: Static vs. Moving Shot

```
STATIC SHOT:                    MOVING SHOT:

   Target                          Target  Virtual Target (where it would land)
     |                               |              |
     |                               |      <-------|
     |                               |    (so the offset needs to be opposite
     ▼                                   to robot motion)

  [Robot]                    ---> [Robot] --->
  (stationary)               (moving right)

  Projectile goes            Projectile curves right due to
  straight to target         inherited velocity, so aim left
```

---

## 2\. The Core Math

This section explains the math behind shoot-on-the-move. 

### Velocity Compensation Formula

The core velocity compensation formula is:

```
Virtual Target Position = Actual Target Position + Offset

Where:
Offset = (-t × vx, -t × vy)
```

**Variables:**

- `t` \= time of flight (how long the projectile is in the air, in seconds)  
- `vx` \= robot's velocity in the X direction (m/s, field-relative)  
- `vy` \= robot's velocity in the Y direction (m/s, field-relative)

**Why the negative sign?** Because we're compensating for the robot's motion. If the robot moves in the \+X direction, the projectile will drift \+X, so we aim in the \-X direction (behind where the target actually is in our reference frame).

### Calculating Time of Flight

Time of flight depends on your projectile's trajectory. Here are three approaches, from simple to complex:

#### Method 1: Simple Parabolic (Ignoring Air Resistance)

For a projectile launched at angle θ with initial velocity v₀:

```
t = (v₀ × sin(θ) + √((v₀ × sin(θ))² + 2g × Δh)) / g
```

Where:

- `g` \= 9.81 m/s² (gravity)  
- `Δh` \= target height \- launch height (positive if target is higher)

For targets at the same height as launch:

```
t = (2 × v₀ × sin(θ)) / g
```

#### Method 2: Lookup Table Based (USE THIS)

Instead of calculating, measure time of flight empirically at various distances:

| Distance (m) | Time of Flight (s) |
| :---- | :---- |
| 1.0 | 0.35 |
| 2.0 | 0.50 |
| 3.0 | 0.65 |
| 4.0 | 0.80 |
| 5.0 | 0.95 |

Then interpolate for intermediate distances.

#### Method 3: Numerical Integration (Includes Drag) (NOT RECOMMENDED)

For highest accuracy, numerically integrate the equations of motion including air resistance. This is covered in [Section 11: Advanced Topics](#11-advanced-topics).

### The Iterative Problem

Here's the catch: calculating the virtual target requires knowing the time of flight. But the time of flight depends on the distance to the target. And the distance changes when you offset the target\!

**The solution: Iterate.**

```java
public Pose2d solveVirtualTarget(Pose2d actualTarget,
                                  Pose2d robotPose,
                                  ChassisSpeeds velocity,
                                  int iterations) {
    Pose2d virtualTarget = actualTarget;

    for (int i = 0; i < iterations; i++) {
        // Calculate distance to current virtual target
        double distance = robotPose.getTranslation()
                          .getDistance(virtualTarget.getTranslation());

        // Get time of flight for that distance
        double timeOfFlight = getTimeOfFlight(distance);

        // Calculate new offset
        double offsetX = -timeOfFlight * velocity.vxMetersPerSecond;
        double offsetY = -timeOfFlight * velocity.vyMetersPerSecond;

        // Update virtual target
        virtualTarget = new Pose2d(
            actualTarget.getX() + offsetX,
            actualTarget.getY() + offsetY,
            actualTarget.getRotation()
        );
    }

    return virtualTarget;
}
```

**How many iterations?** In practice, 2-3 iterations are probably sufficient for convergence. The error should decrease exponentially with each iteration.

### 

### Converting Between Coordinate Frames

**Critical:** The velocity must be in the same coordinate frame as your target position (usually field-relative).

If you have robot-relative velocity from your drivetrain:

```java
// Convert robot-relative velocity to field-relative
public ChassisSpeeds toFieldRelative(ChassisSpeeds robotRelative,
                                      Rotation2d robotHeading) {
    return new ChassisSpeeds(
        robotRelative.vxMetersPerSecond * robotHeading.getCos()
            - robotRelative.vyMetersPerSecond * robotHeading.getSin(),
        robotRelative.vxMetersPerSecond * robotHeading.getSin()
            + robotRelative.vyMetersPerSecond * robotHeading.getCos(),
        robotRelative.omegaRadiansPerSecond
    );
}
```

WPILib's `ChassisSpeeds.fromFieldRelativeSpeeds()` can also help with these conversions.

---

## 

## 

## 

## 

## 3\. System Prerequisites

Before implementing shoot-on-the-move, ensure you have these foundational systems working reliably.

### 3.1 Reliable Odometry / Pose Estimation

You need to know **where your robot is** on the field with reasonable accuracy.

**Recommended: SwerveDrivePoseEstimator**

```java
private final SwerveDrivePoseEstimator poseEstimator;

public DriveSubsystem() {
    poseEstimator = new SwerveDrivePoseEstimator(
        kinematics,
        getGyroRotation(),
        getModulePositions(),
        new Pose2d()  // Initial pose
    );
}

public void periodic() {
    // Update with wheel odometry every loop
    poseEstimator.update(getGyroRotation(), getModulePositions());

    // Add vision measurements when available (with latency)
    if (hasVisionTarget()) {
        poseEstimator.addVisionMeasurement(
            getVisionPose(),
            getVisionTimestamp(),
            getVisionStdDevs()  // Trust level
        );
    }
}
```

### 

### 3.2 Robot Velocity Measurement

You need to know **how fast your robot is moving** in field-relative coordinates.

**From Swerve Module States**

```java
public ChassisSpeeds getFieldRelativeVelocity() {
    // Get robot-relative speeds from modules
    ChassisSpeeds robotRelative = kinematics.toChassisSpeeds(
        getModuleStates()
    );

    // Convert to field-relative
    return ChassisSpeeds.fromRobotRelativeSpeeds(
        robotRelative,
        poseEstimator.getEstimatedPosition().getRotation()
    );
}
```

### 3.3 Working Static Shooting

**You cannot have consistent moving shots without consistent static shots first.**

Before adding motion compensation, verify:

- [ ] Robot can hit the target from various static positions  
- [ ] Lookup tables are populated and accurate  
- [ ] Shooter reaches target RPM quickly   
- [ ] Hood/pivot angle reaches setpoint quickly

---

## 4\. Implementation Approaches

There are several valid approaches to shoot-on-the-move. Here are the three most common, with trade-offs for each.

### Approach A: Virtual Target Method (Recommended)

**Concept:** Offset the target position based on robot velocity, then treat it as a static shot.

**Pros:**

- Easiest to understand and debug  
- Reuses existing static shooting code  
- Works with lookup tables directly

**Cons:**

- Iterative solution adds small computational overhead  
- May need tuning of iteration count

**Implementation Summary:**

1. Get robot pose and velocity (field-relative)  
2. Calculate time of flight for estimated distance  
3. Compute virtual target: `actual + (t × -velocity)`  
4. Iterate 2-3 times to converge  
5. Use virtual target distance for lookup tables  
6. Aim at virtual target heading

### Approach B: Direct Vector Compensation

**Concept:** Calculate the required launch velocity vector to hit the target, accounting for robot motion.

**Pros:**

- Mathematically "pure" solution  
- No iteration required  
- Can optimize for specific constraints (fixed angle, fixed speed)

**Cons:**

- More complex math  
- Harder to integrate with lookup tables

### Approach C: Predictive Position (Future Pose)

**Concept:** Predict where the robot will be when the shot is ready, use that position for calculations.

**Pros:**

- Simple implementation  
- Naturally handles mechanical latency  
- Good for "shot preparation time" scenarios

**Cons:**

- Assumes constant velocity during prediction window  
- Doesn't directly account for projectile flight time

**Implementation:**

```java
// Predict robot position in 0.1 seconds
double predictionTime = 0.10;  // Adjust based on your system
Pose2d futurePose = currentPose.plus(
    new Transform2d(
        velocity.vxMetersPerSecond * predictionTime,
        velocity.vyMetersPerSecond * predictionTime,
        new Rotation2d(velocity.omegaRadiansPerSecond * predictionTime)
    )
);
// Use futurePose for all shooting calculations
```

**Best practice:** Combine this with Approach A—predict future pose, then apply virtual target offset.

---

## 5\. Code Architecture

This section provides complete, working Java code for implementing shoot-on-the-move using WPILib.

### 5.1 ShootOnMoveCalculator.java

The core calculation class:

```java
package frc.robot.util;

import edu.wpi.first.math.geometry.Pose2d;
import edu.wpi.first.math.geometry.Translation2d;
import edu.wpi.first.math.interpolation.InterpolatingDoubleTreeMap;
import edu.wpi.first.math.kinematics.ChassisSpeeds;

public class ShootOnMoveCalculator {

    // Lookup table for time of flight vs. distance
    private final InterpolatingDoubleTreeMap timeOfFlightTable;

    // Number of iterations for virtual target convergence
    private static final int DEFAULT_ITERATIONS = 3;

    public ShootOnMoveCalculator() {
        timeOfFlightTable = new InterpolatingDoubleTreeMap();
        // Populate with measured or calculated values
        // Distance (m) -> Time of Flight (s)
        timeOfFlightTable.put(1.0, 0.35);
        timeOfFlightTable.put(2.0, 0.50);
        timeOfFlightTable.put(3.0, 0.65);
        timeOfFlightTable.put(4.0, 0.80);
        timeOfFlightTable.put(5.0, 0.95);
        timeOfFlightTable.put(6.0, 1.10);
    }

    /**
     * Get the time of flight for a given distance.
     * @param distanceMeters Distance to target in meters
     * @return Time of flight in seconds
     */
    public double getTimeOfFlight(double distanceMeters) {
        // Clamp to table bounds
        distanceMeters = Math.max(1.0, Math.min(6.0, distanceMeters));
        return timeOfFlightTable.get(distanceMeters);
    }

    /**
     * Calculate the virtual target position accounting for robot velocity.
     *
     * @param actualTarget The real target position on the field
     * @param robotPose Current robot pose
     * @param velocity Robot velocity in field-relative coordinates
     * @return The virtual target to aim at
     */
    public Pose2d getVirtualTarget(Pose2d actualTarget,
                                    Pose2d robotPose,
                                    ChassisSpeeds velocity) {
        return getVirtualTarget(actualTarget, robotPose, velocity, DEFAULT_ITERATIONS);
    }

   

























 /**
     * Calculate the virtual target with specified iteration count.
     */
    public Pose2d getVirtualTarget(Pose2d actualTarget,
                                    Pose2d robotPose,
                                    ChassisSpeeds velocity,
                                    int iterations) {
        Translation2d targetTranslation = actualTarget.getTranslation();
        Translation2d robotTranslation = robotPose.getTranslation();

        Translation2d virtualTargetTranslation = targetTranslation;

        for (int i = 0; i < iterations; i++) {
            // Calculate distance to current virtual target
            double distance = robotTranslation.getDistance(virtualTargetTranslation);

            // Get time of flight for that distance
            double tof = getTimeOfFlight(distance);

            // Calculate offset (opposite to robot motion)
            double offsetX = -tof * velocity.vxMetersPerSecond;
            double offsetY = -tof * velocity.vyMetersPerSecond;

            // Update virtual target position
            virtualTargetTranslation = new Translation2d(
                targetTranslation.getX() + offsetX,
                targetTranslation.getY() + offsetY
            );
        }

        return new Pose2d(virtualTargetTranslation, actualTarget.getRotation());
    }











    /**
     * Calculate the heading the robot should face to aim at a target.
     *
     * @param robotPose Current robot pose
     * @param targetPose Target to aim at (can be virtual target)
     * @return Heading in radians (field-relative)
     */
    public double getTargetHeading(Pose2d robotPose, Pose2d targetPose) {
        Translation2d robotToTarget = targetPose.getTranslation()
                                      .minus(robotPose.getTranslation());
        return Math.atan2(robotToTarget.getY(), robotToTarget.getX());
    }

    /**
     * Get the distance to the virtual target.
     */
    public double getVirtualTargetDistance(Pose2d robotPose, Pose2d virtualTarget) {
        return robotPose.getTranslation().getDistance(virtualTarget.getTranslation());
    }

    /**
     * Check if the robot velocity is low enough to be considered stationary.
     * @param velocity Robot velocity
     * @param threshold Speed threshold in m/s
     * @return true if robot is effectively stationary
     */
    public boolean isStationary(ChassisSpeeds velocity, double threshold) {
        double speed = Math.hypot(velocity.vxMetersPerSecond,
                                   velocity.vyMetersPerSecond);
        return speed < threshold;
    }
}
```

### 

### 5.2 ShooterLookupTable.java

Manages shooter parameters based on distance:

```java
package frc.robot.util;

import edu.wpi.first.math.interpolation.InterpolatingDoubleTreeMap;

public class ShooterLookupTable {

    private final InterpolatingDoubleTreeMap distanceToRPM;
    private final InterpolatingDoubleTreeMap distanceToAngle;

    public ShooterLookupTable() {
        distanceToRPM = new InterpolatingDoubleTreeMap();
        distanceToAngle = new InterpolatingDoubleTreeMap();

        // Populate tables with measured values
        // These are examples - replace with your actual tuned values!

        // Distance (m) -> Shooter RPM
        distanceToRPM.put(1.0, 2000.0);
        distanceToRPM.put(1.5, 2200.0);
        distanceToRPM.put(2.0, 2500.0);
        distanceToRPM.put(2.5, 2800.0);
        distanceToRPM.put(3.0, 3200.0);
        distanceToRPM.put(3.5, 3600.0);
        distanceToRPM.put(4.0, 4000.0);
        distanceToRPM.put(4.5, 4400.0);
        distanceToRPM.put(5.0, 4800.0);

        // Distance (m) -> Hood/Pivot Angle (degrees)
        distanceToAngle.put(1.0, 55.0);
        distanceToAngle.put(1.5, 50.0);
        distanceToAngle.put(2.0, 45.0);
        distanceToAngle.put(2.5, 42.0);
        distanceToAngle.put(3.0, 38.0);
        distanceToAngle.put(3.5, 35.0);
        distanceToAngle.put(4.0, 32.0);
        distanceToAngle.put(4.5, 30.0);
        distanceToAngle.put(5.0, 28.0);
    }

    /**
     * Get the shooter RPM for a given distance.
     * @param distanceMeters Distance to target
     * @return Target RPM for shooter flywheel
     */
    public double getRPM(double distanceMeters) {
        // Clamp to safe bounds
        distanceMeters = Math.max(1.0, Math.min(5.0, distanceMeters));
        return distanceToRPM.get(distanceMeters);
    }

    /**
     * Get the hood/pivot angle for a given distance.
     * @param distanceMeters Distance to target
     * @return Target angle in degrees
     */
    public double getAngleDegrees(double distanceMeters) {
        distanceMeters = Math.max(1.0, Math.min(5.0, distanceMeters));
        return distanceToAngle.get(distanceMeters);
    }

    /**
     * Add or update a data point in the RPM table.
     */
    public void setRPMDataPoint(double distance, double rpm) {
        distanceToRPM.put(distance, rpm);
    }

    /**
     * Add or update a data point in the angle table.
     */
    public void setAngleDataPoint(double distance, double angleDegrees) {
        distanceToAngle.put(distance, angleDegrees);
    }
}
```

### 

### 5.3 ShootWhileMovingCommand.java

The command that ties everything together:

```java
package frc.robot.commands;

import edu.wpi.first.math.geometry.Pose2d;
import edu.wpi.first.math.geometry.Rotation2d;
import edu.wpi.first.math.kinematics.ChassisSpeeds;
import edu.wpi.first.wpilibj2.command.Command;
import frc.robot.subsystems.DriveSubsystem;
import frc.robot.subsystems.ShooterSubsystem;
import frc.robot.subsystems.PivotSubsystem;
import frc.robot.util.ShootOnMoveCalculator;
import frc.robot.util.ShooterLookupTable;

public class ShootWhileMovingCommand extends Command {

    private final DriveSubsystem drive;
    private final ShooterSubsystem shooter;
    private final PivotSubsystem pivot;
    private final ShootOnMoveCalculator calculator;
    private final ShooterLookupTable lookupTable;

    // Target position (e.g., speaker location)
    private final Pose2d targetPose;

    // Tolerances for "ready to shoot" check
    private static final double HEADING_TOLERANCE_RAD = Math.toRadians(2.0);
    private static final double RPM_TOLERANCE = 50.0;
    private static final double ANGLE_TOLERANCE_DEG = 1.0;

    public ShootWhileMovingCommand(DriveSubsystem drive,
                                    ShooterSubsystem shooter,
                                    PivotSubsystem pivot,
                                    Pose2d targetPose) {
        this.drive = drive;
        this.shooter = shooter;
        this.pivot = pivot;
        this.targetPose = targetPose;

        this.calculator = new ShootOnMoveCalculator();
        this.lookupTable = new ShooterLookupTable();

        addRequirements(shooter, pivot);
        // Note: We don't require drive so operator can still control movement
    }

    @Override
    public void initialize() {
        // Start spinning up shooter immediately
        // We'll refine the RPM as we get better distance estimates
    }

    @Override
    public void execute() {
        // 1. Get current robot state
        Pose2d robotPose = drive.getPoseEstimate();
        ChassisSpeeds velocity = drive.getFieldRelativeVelocity();

        // 2. Calculate virtual target
        Pose2d virtualTarget = calculator.getVirtualTarget(
            targetPose, robotPose, velocity, 3);

        // 3. Get shooting parameters based on virtual target distance
        double distance = calculator.getVirtualTargetDistance(robotPose, virtualTarget);
        double targetRPM = lookupTable.getRPM(distance);
        double targetAngle = lookupTable.getAngleDegrees(distance);

        // 4. Calculate heading to virtual target
        double targetHeading = calculator.getTargetHeading(robotPose, virtualTarget);

        // 5. Command subsystems
        shooter.setTargetRPM(targetRPM);
        pivot.setAngleDegrees(targetAngle);

        // 6. Request drive to rotate toward target
        // This works with field-oriented driving - robot maintains
        // translation control while we override rotation
        drive.setTargetHeading(targetHeading);
    }

    /**
     * Check if all subsystems are ready to shoot.
     */
    public boolean isReadyToShoot() {
        Pose2d robotPose = drive.getPoseEstimate();
        ChassisSpeeds velocity = drive.getFieldRelativeVelocity();
        Pose2d virtualTarget = calculator.getVirtualTarget(
            targetPose, robotPose, velocity, 3);

        double targetHeading = calculator.getTargetHeading(robotPose, virtualTarget);
        double currentHeading = robotPose.getRotation().getRadians();
        double headingError = Math.abs(targetHeading - currentHeading);

        // Normalize heading error to [-pi, pi]
        while (headingError > Math.PI) headingError -= 2 * Math.PI;
        headingError = Math.abs(headingError);

        double distance = calculator.getVirtualTargetDistance(robotPose, virtualTarget);
        double targetRPM = lookupTable.getRPM(distance);
        double targetAngle = lookupTable.getAngleDegrees(distance);

        boolean headingReady = headingError < HEADING_TOLERANCE_RAD;
        boolean rpmReady = Math.abs(shooter.getCurrentRPM() - targetRPM) < RPM_TOLERANCE;
        boolean angleReady = Math.abs(pivot.getCurrentAngle() - targetAngle) < ANGLE_TOLERANCE_DEG;

        return headingReady && rpmReady && angleReady;
    }

    @Override
    public void end(boolean interrupted) {
        shooter.stop();
        drive.clearTargetHeading();
    }

    @Override
    public boolean isFinished() {
        return false;  // Run until interrupted or shot is complete
    }
}
```

### 5.4 Integration with Autonomous

Example of using shoot-while-moving in auto:

```java
public Command getShootWhileDrivingAuto() {
    return Commands.sequence(
        // Start driving toward game pieces
        new DriveToPositionCommand(drive, pickupPose)
            .alongWith(
                // While driving, prepare shooter for next shot
                new ShootWhileMovingCommand(drive, shooter, pivot, speakerPose)
            ),

        // When ready, trigger the actual shot
        new InstantCommand(() -> indexer.feedNote()),

        // Wait for note to leave
        new WaitCommand(0.2),

        // Continue to next action
        new IntakeCommand(intake)
    );
}
```

---

## 

## 

## 

## 

## 6\. Lookup Table Creation & Tuning

Getting accurate lookup tables is critical for consistent shooting. This section covers the methodology for creating and tuning them.

### 6.1 Static Shot Characterization

#### Procedure

**Step 1: Set Up Measurement Positions**

Mark positions on the field at regular intervals:

- Start at 1 meter from target, increment by 0.5m  
- Go out to maximum expected shooting distance  
- Mark positions with tape for repeatability

**Step 2: Initial RPM/Angle Finding**

At each distance:

1. Start with a conservative (low) RPM  
2. Adjust until shots consistently hit the target  
3. Record the RPM  
4. Adjust angle for optimal trajectory (not too flat, not too arced)  
5. Record the (shooter) angle

**Step 3: Consistency Verification**

For each (distance, RPM, angle) combination:

1. Take 10 consecutive shots  
2. Record hit rate  
3. If \<80% hit rate, investigate:  
   - Mechanical issues (wobble, inconsistent compression)  
   - Feeding issues (gamepiece orientation, speed)  
   - Environmental (battery voltage)  
4. Re-tune if needed

**Step 4: Record in Spreadsheet**

```
| Distance (m) | RPM  | Angle (deg) | Hit Rate | Notes           |
|--------------|------|-------------|----------|-----------------|
| 1.0          | 2000 | 55          | 95%      |                 |
| 1.5          | 2200 | 50          | 90%      |                 |
| 2.0          | 2500 | 45          | 85%      |                 |
| 2.5          | 2800 | 42          | 80%      |                 |
| ...          | ...  | ...         | ...      |                 |
```

### 6.2 Time of Flight Calibration (use A or C)

#### Option A: Camera 

1. Record shots at 60/120 FPS  
2. Count frames from release to target impact  
3. Calculate: `ToF = frames / framerate`

#### Option B: Physics Calculation

Use projectile motion equations:

```java
public double calculateTimeOfFlight(double distance, double launchAngle,
                                     double launchVelocity, double heightDiff) {
    double angleRad = Math.toRadians(launchAngle);
    double vy = launchVelocity * Math.sin(angleRad);
    double g = 9.81;

    // Solve: heightDiff = vy*t - 0.5*g*t^2
    // Using quadratic formula
    double a = -0.5 * g;
    double b = vy;
    double c = -heightDiff;

    double discriminant = b*b - 4*a*c;
    if (discriminant < 0) return 0.5;  // Default fallback

    double t1 = (-b + Math.sqrt(discriminant)) / (2*a);
    double t2 = (-b - Math.sqrt(discriminant)) / (2*a);

    // Return the positive solution
    return (t1 > 0) ? t1 : t2;
}
```

#### Option C: Stopwatch

Less accurate but works:

1. Have someone watch the target  
2. Start timer at shot, stop at impact  
3. Average over multiple shots

---

## 

## 

## 

## 

## 

## 

## 

## 

## 

## 7\. Turret vs. Non-Turret Implementations

The shoot-on-the-move calculation is the same regardless of mechanism, but how you apply the compensation differs.

### 7.1 With Turret

When you have a turret, it handles aiming while the drivetrain moves freely.

#### Turret Aiming

```java
public class TurretSubsystem extends SubsystemBase {

    private final ShootOnMoveCalculator calculator;

    /**
     * Set turret to track target with velocity feedforward.
     */
    public void trackTarget(Pose2d targetPose, Pose2d robotPose,
                            ChassisSpeeds robotVelocity) {
        // Calculate virtual target
        Pose2d virtualTarget = calculator.getVirtualTarget(
            targetPose, robotPose, robotVelocity, 3);

        // Calculate required turret angle (relative to robot)
        double fieldHeading = calculator.getTargetHeading(robotPose, virtualTarget);
        double robotHeading = robotPose.getRotation().getRadians();
        double turretAngle = fieldHeading - robotHeading;

        // Normalize to turret range
        turretAngle = normalizeAngle(turretAngle);

        // Calculate feedforward for turret velocity
        double turretVelocityFF = calculateTurretVelocityFeedforward(
            robotPose, virtualTarget, robotVelocity);

        // Command turret with position setpoint + velocity feedforward
        setTurretPosition(turretAngle, turretVelocityFF);
    }

    /**
     * Calculate turret angular velocity needed to track target while robot moves.
     * This is Team 254's velocity feedforward approach.
     */
    private double calculateTurretVelocityFeedforward(Pose2d robotPose,
                                                       Pose2d targetPose,
                                                       ChassisSpeeds robotVelocity) {
        Translation2d robotToTarget = targetPose.getTranslation()
                                      .minus(robotPose.getTranslation());
        double distance = robotToTarget.getNorm();

        if (distance < 0.1) return 0.0;  // Avoid division by zero

        // Calculate tangential velocity component
        double targetAngle = Math.atan2(robotToTarget.getY(), robotToTarget.getX());
        double robotHeading = robotPose.getRotation().getRadians();

        // Velocity perpendicular to target direction causes turret rotation
        double vx = robotVelocity.vxMetersPerSecond;
        double vy = robotVelocity.vyMetersPerSecond;

        // Project velocity onto perpendicular direction
        double perpX = -Math.sin(targetAngle);
        double perpY = Math.cos(targetAngle);
        double tangentialVelocity = vx * perpX + vy * perpY;

        // Angular velocity = tangential velocity / distance
        double angularVelocity = tangentialVelocity / distance;

        // Also account for robot rotation
        angularVelocity -= robotVelocity.omegaRadiansPerSecond;

        return angularVelocity;
    }
}
```

### 

### 7.2 Without Turret (Swerve Robot Rotation)

When the robot itself rotates to aim, use swerve's ability to translate while rotating.

#### Drive Subsystem Integration

```java
public class DriveSubsystem extends SubsystemBase {

    // Target heading for auto-aim (null = manual control)
    private Double targetHeading = null;
    private final PIDController headingController;

    public DriveSubsystem() {
        headingController = new PIDController(5.0, 0.0, 0.2);
        headingController.enableContinuousInput(-Math.PI, Math.PI);
        headingController.setTolerance(Math.toRadians(2.0));
    }

    /**
     * Set a target heading for auto-aim.
     * @param headingRadians Field-relative heading in radians
     */
    public void setTargetHeading(double headingRadians) {
        this.targetHeading = headingRadians;
    }

    public void clearTargetHeading() {
        this.targetHeading = null;
    }

    /**
     * Drive with translation from operator, rotation from auto-aim.
     * @param xSpeed Field-relative X speed (m/s)
     * @param ySpeed Field-relative Y speed (m/s)
     */
    public void driveWithAutoAim(double xSpeed, double ySpeed) {
        double omega;

        if (targetHeading != null) {
            // Use PID to rotate toward target
            double currentHeading = getPoseEstimate().getRotation().getRadians();
            omega = headingController.calculate(currentHeading, targetHeading);

            // Clamp rotation speed
            omega = Math.max(-4.0, Math.min(4.0, omega));
        } else {
            // No auto-aim, operator has full control
            omega = operatorRotationInput;
        }

        // Apply field-relative drive
        ChassisSpeeds speeds = ChassisSpeeds.fromFieldRelativeSpeeds(
            xSpeed, ySpeed, omega, getPoseEstimate().getRotation());

        setModuleStates(kinematics.toSwerveModuleStates(speeds));
    }
}
```

#### Operator Controls

Allow operator to maintain translation control while auto-aim handles rotation:

```java
public class DriveCommand extends Command {

    @Override
    public void execute() {
        double xSpeed = -joystick.getLeftY() * MAX_SPEED;  // Field forward/back
        double ySpeed = -joystick.getLeftX() * MAX_SPEED;  // Field left/right

        if (shootButton.getAsBoolean()) {
            // Auto-aim mode: operator controls translation, system controls rotation
            drive.driveWithAutoAim(xSpeed, ySpeed);
        } else {
            // Normal mode: operator controls everything
            double rotSpeed = -joystick.getRightX() * MAX_ANGULAR_SPEED;
            drive.driveFieldRelative(xSpeed, ySpeed, rotSpeed);
        }
    }
}
```

---

## 8\. Latency Compensation (OPTIONAL)

Real-world systems have delays between sensing, processing, and mechanical response. Properly accounting for latency is essential for accurate moving shots.

### 8.1 Sources of Latency

| Source | Typical Delay | Description |
| :---- | :---- | :---- |
| Camera capture | 20-50ms | Time for image sensor to capture frame |
| Image processing | 10-30ms | Vision pipeline processing time |
| Network latency | 5-10ms | RoboRIO to coprocessor communication |
| Control loop | 10-20ms | Time between sensor read and motor command |
| Mechanical response | 50-200ms | Shooter spinup, turret movement |

**Total typical latency: 100-300ms**

### 8.2 Vision Latency Compensation

WPILib's pose estimator handles vision latency automatically when you provide timestamps:

```java
// When adding vision measurements, use the capture timestamp
public void addVisionMeasurement(Pose2d visionPose, double timestampSeconds) {
    // The pose estimator interpolates historical odometry
    // to properly fuse the delayed vision measurement
    poseEstimator.addVisionMeasurement(
        visionPose,
        timestampSeconds,
        VecBuilder.fill(0.5, 0.5, Math.toRadians(10))  // Standard deviations
    );
}

// Get timestamp from PhotonVision/Limelight
double captureTime = result.getTimestampSeconds();
// Or: Timer.getFPGATimestamp() - result.getLatencyMillis() / 1000.0
```

### 8.3 Mechanical Lead Time

Account for the time it takes your mechanism to respond:

```java
public class ShootWhileMovingCommand extends Command {

    // Total system latency to account for
    private static final double LEAD_TIME_SECONDS = 0.15;

    @Override
    public void execute() {
        Pose2d currentPose = drive.getPoseEstimate();
        ChassisSpeeds velocity = drive.getFieldRelativeVelocity();

        // Predict where robot will be when shot actually happens
        Pose2d predictedPose = predictFuturePose(currentPose, velocity, LEAD_TIME_SECONDS);

        // Use predicted pose for all calculations
        Pose2d virtualTarget = calculator.getVirtualTarget(
            targetPose, predictedPose, velocity, 3);

        // ... rest of shooting logic
    }

    private Pose2d predictFuturePose(Pose2d current, ChassisSpeeds velocity, double dt) {
        return current.plus(new Transform2d(
            velocity.vxMetersPerSecond * dt,
            velocity.vyMetersPerSecond * dt,
            new Rotation2d(velocity.omegaRadiansPerSecond * dt)
        ));
    }
}
```

### 8.4 Velocity Filtering

Raw velocity measurements can be noisy. Apply filtering to get smoother estimates:

```java
public class VelocityFilter {

    private final LinearFilter xFilter;
    private final LinearFilter yFilter;
    private final LinearFilter omegaFilter;

    public VelocityFilter() {
        // Moving average over 5 samples (~100ms at 50Hz)
        // Adjust based on your noise level
        xFilter = LinearFilter.movingAverage(5);
        yFilter = LinearFilter.movingAverage(5);
        omegaFilter = LinearFilter.movingAverage(5);
    }

    public ChassisSpeeds filter(ChassisSpeeds raw) {
        return new ChassisSpeeds(
            xFilter.calculate(raw.vxMetersPerSecond),
            yFilter.calculate(raw.vyMetersPerSecond),
            omegaFilter.calculate(raw.omegaRadiansPerSecond)
        );
    }

    public void reset() {
        xFilter.reset();
        yFilter.reset();
        omegaFilter.reset();
    }
}
```

**Trade-off:** More filtering \= smoother but more lag. Less filtering \= responsive but noisy. Start with a 5 sample average and adjust.

---

## 

## 9\. Common Pitfalls & Debugging

### 9.1 Wrong Coordinate Frame

**Symptom:** Shots miss in seemingly random directions, or compensation makes shots worse.

**Cause:** Velocity is in robot-relative coordinates but calculations expect field-relative (or vice versa).

**Fix:**

```java
// Ensure velocity is field-relative before calculations
ChassisSpeeds fieldRelativeVelocity = ChassisSpeeds.fromRobotRelativeSpeeds(
    robotRelativeVelocity,
    robotPose.getRotation()
);
```

### 9.2 Sign Errors

**Symptom:** Moving left makes shots miss right (opposite of expected).

**Cause:** Velocity sign is inverted somewhere.

### 9.3 Inconsistent Static Shots

**Symptom:** Moving shots are wildly inconsistent.

**Cause:** If static shots aren't consistent, moving shots can't be either.

**Fix:** Don't attempt moving shots until static shooting is solid. Check:

- Mechanical issues (loose bolts, worn wheels)  
- Shooter spinup time (wait for RPM to stabilize)  
- Feeding consistency (note orientation, compression)

### 9.4 Outdated Velocity Measurements

**Symptom:** Shots lag behind—accurate when velocity is constant, miss during accel/decel.

**Cause:** Velocity filter has too much lag.

**Fix:** Reduce filter size or use prediction to compensate:

```java
// Predict velocity forward to compensate for filter lag
ChassisSpeeds predictedVelocity = new ChassisSpeeds(
    currentVelocity.vxMetersPerSecond + acceleration.vxMetersPerSecond * filterLag,
    currentVelocity.vyMetersPerSecond + acceleration.vyMetersPerSecond * filterLag,
    currentVelocity.omegaRadiansPerSecond
);
```

### 9.5 Ignoring Rotational Velocity

**Symptom:** Shots are accurate when driving straight, miss when robot is also rotating.

**Cause:** Robot rotation adds velocity to the shooter location.

**Fix:** Account for angular velocity contribution:

```java
// Shooter offset from robot center
Translation2d shooterOffset = new Translation2d(0.2, 0.0);  // 20cm forward

// Additional linear velocity from rotation
double omega = robotVelocity.omegaRadiansPerSecond;
double additionalVx = -omega * shooterOffset.getY();
double additionalVy = omega * shooterOffset.getX();

ChassisSpeeds adjustedVelocity = new ChassisSpeeds(
    robotVelocity.vxMetersPerSecond + additionalVx,
    robotVelocity.vyMetersPerSecond + additionalVy,
    omega
);
```

### 9.6 Debugging Checklist

When shots aren't hitting:

1. **Verify static shots work** at the current distance  
2. **Verify** robot pose is reasonable  
3. **Verify** velocity direction matches joystick  
4. **Verify** virtual target is offset opposite to motion  
5. **Verify** calculated distance/RPM/angle are reasonable  
6. **Check mechanical** \- is shooter at correct RPM? Pivot at correct angle?  
7. **Check timing** \- are you shooting before subsystems reach setpoints?

---

## 11\. Advanced Topics (Ignore for now)

For teams looking to push accuracy further, here are advanced techniques.

### 11.1 Air Resistance (Drag)

Air resistance causes:

- Reduced horizontal velocity over time  
- Increased time of flight  
- Steeper descent angle at target

#### Simple Drag Model

```java
public class DragAdjustedCalculator {

    // Drag coefficient (tune empirically)
    private static final double DRAG_FACTOR = 0.05;  // Approximate 5% velocity loss per second

    public double getAdjustedTimeOfFlight(double distance, double launchVelocity) {
        // Without drag
        double basicToF = distance / (launchVelocity * Math.cos(Math.toRadians(45)));

        // With drag, projectile slows down, so it takes longer
        // Approximate: ToF increases by drag factor
        return basicToF * (1 + DRAG_FACTOR * basicToF);
    }
}
```

#### Empirical Drag Measurement

1. Drop game piece from known height (e.g., 5m)  
2. Measure time to hit ground  
3. Compare to theoretical (no drag): t \= sqrt(2h/g)  
4. Difference indicates drag effect

### 11.2 Magnus Effect

The Magnus effect causes spinning projectiles to curve. For backspin shooters, this typically means:

- Ball rises more than expected  
- Ball maintains altitude longer  
- Trajectory is flatter

**When it matters:**

- High-spin shooters (\>3000 RPM on ball)  
- Long-distance shots (\>4m)  
- Precision shots at edges of target

**How to account for it:**

- Adjust lookup tables empirically  
- No simple formula—test and tune

### 11.3 Multi-Shot Sequences

When shooting multiple game pieces rapidly:

```java
public class MultiShotCalculator {

    private static final double SHOT_INTERVAL = 0.25;  // 250ms between shots

    public List<ShootingParameters> calculateSequence(
            Pose2d robotPose,
            ChassisSpeeds velocity,
            Pose2d targetPose,
            int numShots) {

        List<ShootingParameters> sequence = new ArrayList<>();

        for (int i = 0; i < numShots; i++) {
            double timeOffset = i * SHOT_INTERVAL;

            // Predict robot position at this shot's release time
            Pose2d predictedPose = predictPose(robotPose, velocity, timeOffset);

            // Calculate virtual target for this shot
            Pose2d virtualTarget = calculator.getVirtualTarget(
                targetPose, predictedPose, velocity);

            double distance = predictedPose.getTranslation()
                              .getDistance(virtualTarget.getTranslation());

            sequence.add(new ShootingParameters(
                lookupTable.getRPM(distance),
                lookupTable.getAngleDegrees(distance),
                calculator.getTargetHeading(predictedPose, virtualTarget)
            ));
        }

        return sequence;
    }
}
```

### 11.4 Trajectory Optimization

Some teams like 1690 use numerical optimization to solve for the perfect shot parameters. This involves:

1. Define objective: minimize miss distance  
2. Define constraints: fixed launch position, target position, shooter limits  
3. Solve using nonlinear optimization (e.g., Sleipnir library)

This is significantly more complex with little gain IMO  
---

## 

## 12\. Reference Resources

### Team Code Repositories

- **Team 254 (2019)** \- Turret velocity feedforward implementation  
    
  - GitHub: `Team254/FRC-2019-Public`  
  - File: `Superstructure.java` (lines 280-320)


- **Team 6328 (2022-2024)** \- Shot calculator implementations  
    
  - GitHub: `Mechanical-Advantage/RobotCode2024`  
  - Various shooting utilities

### WPILib Documentation

- [SwerveDrivePoseEstimator](https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-pose-estimators.html)  
- [InterpolatingDoubleTreeMap](https://github.wpilib.org/allwpilib/docs/release/java/edu/wpi/first/math/interpolation/InterpolatingDoubleTreeMap.html)  
- [ChassisSpeeds](https://github.wpilib.org/allwpilib/docs/release/java/edu/wpi/first/math/kinematics/ChassisSpeeds.html)

### Tools

- **Desmos 3D Trajectory Calculator**: [https://www.desmos.com/3d/rbrerrotsx](https://www.desmos.com/3d/rbrerrotsx)  
  - Visualize projectile paths with drag  
  - Test different angles and velocities

### Community Discussions

- [Chief Delphi: Shoot on the move from the code perspective](https://www.chiefdelphi.com/t/shoot-on-the-move-from-the-code-perspective/511815)  
- [Chief Delphi: Shooting on the Move Thoughts](https://www.chiefdelphi.com/t/shooting-on-the-move-thoughts/512169)  
- [Chief Delphi: Ball turret movement compensation](https://www.chiefdelphi.com/t/have-ball-turret-compensate-for-robot-left-and-right-movement/381782)

---

