# Game Piece (Yellow Ball) Detection System Plan

## Context

The robot needs to detect yellow balls (2026 "Fuel" game pieces) on the field and know their field-relative positions. This feeds into a future path optimization system (Choreo) that will plan optimal collection routes. Detection must run on the Mac mini coprocessor to minimize RoboRIO load. PhotonVision already runs on the Mac mini for AprilTag detection.

**Key discovery**: PR [#2158](https://github.com/PhotonVision/photonvision/pull/2158) adds native CoreML object detection to PhotonVision for macOS. This means we can use PhotonVision for **both** AprilTags and ball detection on the Mac mini, reusing the existing PhotonCamera API. No separate Python service needed.

---

## Architecture Overview

```
Mac Mini (Coprocessor)                    RoboRIO
+---------------------------+    NT4     +-----------------------------+
|  PhotonVision (mac branch)|<--------->|                             |
|  +- AprilTag pipeline(s)  |          |  Vision subsystem           |
|  +- Object Detection      |          |    (existing, AprilTags)    |
|     pipeline (CoreML/YOLO)|          |                             |
|                           |          |  GamePieceVision subsystem  |
|  Camera(s)                |          |    (NEW - reads detections, |
|                           |          |     computes field-relative |
|                           |          |     ball positions)         |
|                           |          |                             |
|                           |          |  Superstructure             |
|                           |          |    (consumes ball positions |
|                           |          |     for future path opt)    |
+---------------------------+          +-----------------------------+
```

**Data flow**:
1. PhotonVision captures frames, runs CoreML YOLO model -> detects balls
2. Detections published over NT4 via standard PhotonVision protocol (yaw, pitch, area, bounding box)
3. `GamePieceVision` subsystem on RoboRIO reads detections via `PhotonCamera` API
4. Estimates distance using known ball diameter + camera intrinsics (pinhole model)
5. Transforms to field-relative positions using robot pose from swerve odometry
6. Exposes `List<Translation2d>` for downstream consumers (Superstructure, path planner)

---

## Step 1: Build PhotonVision from `mac` Branch

- Clone PhotonVision repo, checkout the `mac` branch from PR #2158
- Follow the macOS build instructions (requires JDK 24, Swift 6.2)
- Build and deploy to Mac mini
- This gives us object detection with CoreML backend alongside existing AprilTag support

**Note on model flexibility**: The `mac` branch uses CoreML as the inference backend but PhotonVision's post-processing is YOLO-specific. If a non-YOLO model (DETR, RT-DETR) is needed later, we'd need to either contribute a new post-processing backend to PhotonVision or build a separate service. For yellow ball detection, YOLO is the right tool -- it's fast, accurate for simple round objects, and well-supported.

---

## Step 2: Train YOLO Model for Yellow Balls

### 2A. Model Selection

**Recommended: YOLO26n (nano)** -- released Jan 14, 2026.
- 40.9 mAP on COCO, 43% faster CPU inference than predecessors
- NMS-free end-to-end design (lower latency, simpler deployment)
- CoreML export officially supported
- Nano size is ideal for real-time FRC use (speed > marginal accuracy gains from larger models)

Fallback: YOLOv11n if YOLO26 has CoreML conversion issues with PhotonVision's `mac` branch (the branch was built against YOLOv11 -- may need to verify YOLO26 compatibility).

### 2B. Existing Datasets (Start Here)

Two community datasets already exist on Roboflow Universe for 2026 Fuel:

1. **FRC 2026 Fuel by -wrw23** (https://universe.roboflow.com/-wrw23/frc-2026-fuel) -- 464 images, labeled, multiple export formats (YOLO, COCO, etc.)
2. **FRC 2026 Fuel by frcroboraiders** (https://universe.roboflow.com/frcroboraiders/frc-2026-fuel-sbrdk) -- 706 images, labeled, pre-trained model available

**Action**: Download both in YOLO format, merge into a single dataset. This gives you ~1,170 labeled images as a starting point -- enough for a solid initial model.

```bash
# Download via Roboflow Python SDK
pip install roboflow
python -c "
from roboflow import Roboflow
rf = Roboflow(api_key='YOUR_KEY')
# Download dataset 1
ds1 = rf.workspace('-wrw23').project('frc-2026-fuel').version(2).download('yolov11')
# Download dataset 2
ds2 = rf.workspace('frcroboraiders').project('frc-2026-fuel-sbrdk').version(1).download('yolov11')
"
```

### 2C. Iterative Training Pipeline (Seed -> Auto-label -> Refine -> Retrain)

This is the key workflow to continuously improve the model with minimal manual labeling effort:

```
+-------------------------------------------------------------+
|  PHASE 1: Bootstrap (one-time)                              |
|  Community datasets (1,170 imgs) -> Train base model        |
+-------------------------------------------------------------+
|  PHASE 2: Collect raw data                                  |
|  Record video at practice/scrimmage -> extract frames       |
+-------------------------------------------------------------+
|  PHASE 3: Auto-label with current best model                |
|  Run model on raw frames -> generate predicted labels       |
+-------------------------------------------------------------+
|  PHASE 4: Human review & correction                         |
|  Fix wrong/missed detections in Roboflow or CVAT            |
|  (MUCH faster than labeling from scratch)                   |
+-------------------------------------------------------------+
|  PHASE 5: Retrain on expanded dataset                       |
|  Merge corrected labels -> fine-tune model                  |
|  Go back to Phase 2 with new model                          |
+-------------------------------------------------------------+
```

#### Phase 1: Bootstrap -- Train Base Model

```bash
# Train on merged community datasets
yolo train \
  model=yolo26n.pt \
  data=fuel_merged.yaml \
  epochs=150 \
  imgsz=640 \
  batch=16 \
  patience=30 \
  augment=True \
  mosaic=1.0 \
  mixup=0.1 \
  hsv_h=0.015 \
  hsv_s=0.7 \
  hsv_v=0.4
```

Key training parameters:
- `patience=30`: Early stopping -- prevents overfitting on small dataset
- `mosaic=1.0`: Combines 4 images into 1, simulates varied scenes (critical for small datasets)
- `hsv_s=0.7, hsv_v=0.4`: Aggressive color augmentation -- essential because arena lighting varies dramatically between venues
- `mixup=0.1`: Light mixup augmentation for regularization

Expected result: A model that detects yellow balls reasonably well (~70-85% mAP) but may struggle with:
- Your specific camera angle/resolution
- Your specific arena lighting
- Balls partially occluded by robots
- Balls against yellow-ish field elements

#### Phase 2: Collect Raw Data from Your Robot

Record video from the actual ball detection camera during practice. This captures your specific conditions:
- Your camera's resolution, FOV, and mounting angle
- Your arena's lighting
- Real game scenarios (balls near robots, walls, partially obscured)

```bash
# Extract frames from video (1 frame per second to avoid near-duplicates)
ffmpeg -i practice_match.mp4 -vf "fps=1" frames/frame_%04d.jpg
```

Aim for 200-500 frames per collection round. Prioritize diversity:
- Different distances (close, mid, far)
- Different lighting (bright, dim, backlighting)
- Different counts (0 balls, 1 ball, many balls)
- Edge cases (balls touching each other, balls near yellow elements, partial occlusion)

#### Phase 3: Auto-label with Current Model

Use your trained model to generate predicted labels on the new raw frames:

```python
from ultralytics import YOLO

model = YOLO("runs/detect/train/weights/best.pt")

# Predict on new frames, save labels in YOLO format
results = model.predict(
    source="frames/",
    save_txt=True,        # Save YOLO-format label files
    save_conf=True,       # Include confidence in label files
    conf=0.25,            # Low threshold -- catch everything, fix false positives in review
    iou=0.45,
    project="auto_labeled",
    name="round1"
)
```

This generates `.txt` label files for every frame -- each with predicted bounding boxes. At `conf=0.25`, you'll get some false positives, but that's intentional: it's faster to delete a wrong box than to draw a missed one from scratch.

#### Phase 4: Human Review & Correction

Upload auto-labeled images + predicted labels to a labeling tool for human correction:

**Option A: Roboflow (Recommended for FRC teams)**
- Upload images + YOLO labels via web UI or API
- Roboflow renders predicted boxes as editable annotations
- Reviewers fix errors: delete false positives, adjust boxes, add missed detections
- Typically 3-5x faster than labeling from scratch

**Option B: CVAT (Free, self-hosted)**
- Import images + YOLO annotations
- Use CVAT's annotation UI to correct
- Export corrected labels in YOLO format

**What to focus on during review:**
- Delete false positives (non-ball objects detected as balls)
- Add missed balls (false negatives -- especially distant or occluded ones)
- Tighten loose bounding boxes (box should tightly fit the ball)
- Don't need pixel-perfect -- within ~5px is fine for detection

#### Phase 5: Retrain on Expanded Dataset

Merge the corrected new labels with the original dataset and fine-tune:

```bash
# Fine-tune from the previous best weights (transfer learning)
yolo train \
  model=runs/detect/train/weights/best.pt \
  data=fuel_expanded.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  patience=20 \
  lr0=0.001           # Lower learning rate for fine-tuning (default is 0.01)
```

Key: start from `best.pt` (your previous model), not from the COCO pretrained weights. This preserves what the model already learned and refines it with the new data. The lower learning rate (`lr0=0.001`) prevents catastrophic forgetting.

**Repeat Phases 2-5** after each practice/scrimmage. Each cycle:
- Adds 200-500 corrected images
- Takes ~30 min of human review time (auto-labels do 80% of the work)
- Measurably improves accuracy on your specific conditions

Typical progression:
| Round | Total Images | Expected mAP | Notes |
|-------|-------------|--------------|-------|
| 0 (bootstrap) | ~1,170 | 70-85% | Community data only |
| 1 | ~1,500 | 80-90% | + your camera/lighting |
| 2 | ~2,000 | 88-95% | + edge cases from practice |
| 3+ | ~2,500+ | 93%+ | Diminishing returns, focus on hard cases |

### 2D. Alternative: Zero-Shot Auto-Labeling for Cold Start

If you want to skip the community datasets entirely and build from your own data:

1. Use **Grounding DINO** or **YOLO-World** (zero-shot detectors) to auto-label your raw frames with the text prompt `"yellow ball"` or `"fuel"`
2. Review and correct the auto-labels in Roboflow/CVAT
3. Train your YOLO model on the corrected labels

```python
# Using Autodistill (Roboflow's framework) for zero-shot labeling
from autodistill_grounded_sam import GroundedSAM
from autodistill.detection import CaptionOntology

ontology = CaptionOntology({"yellow ball": "Fuel"})
base_model = GroundedSAM(ontology=ontology)
base_model.label(input_folder="frames/", output_folder="labeled/")
```

This is useful if you can't find community datasets or want labels tailored entirely to your camera's perspective.

### 2E. Export to CoreML for PhotonVision

```bash
# Export best model to CoreML format
yolo export model=runs/detect/train/weights/best.pt format=coreml imgsz=640

# Output: runs/detect/train/weights/best.mlmodel (or best.mlpackage)
```

Upload to PhotonVision:
- Rename to follow PhotonVision convention: `Fuel-640-640-yolo26n.mlmodel`
- Create labels file: `Fuel-640-640-yolo26n-labels.txt` containing a single line: `Fuel`
- Upload both files via PhotonVision's Settings -> Object Detection UI

### 2F. Validation Before Deployment

Before deploying to the robot, validate on a held-out test set:

```bash
# Validate on test split
yolo val model=best.pt data=fuel.yaml split=test

# Key metrics to check:
# - mAP@0.5 > 0.90 (90%+ of balls detected with correct boxes)
# - Precision > 0.90 (few false positives)
# - Recall > 0.85 (few missed balls)
# - Inference time < 30ms on Mac mini (for real-time use)
```

Also run qualitative checks:
- Test with 0 balls in frame (should produce 0 detections)
- Test with balls at max range (5m+) -- expect lower confidence
- Test with partial occlusion -- should still detect
- Test with similar-colored objects (yellow bumpers, etc.) -- should NOT detect

---

## Step 3: Camera Configuration Decision

Two viable approaches -- recommend deciding based on hardware availability:

**Option A: Dedicated camera for ball detection (Recommended)**
- Mount a separate camera (e.g., wide-angle USB cam, Arducam OV9281) angled toward the ground/field
- Wider FOV catches more balls, optimized mounting angle for ground-level objects
- No pipeline switching or frame sharing with AprilTags
- Add a new `PhotonCamera("ballCam")` in the Java code

**Option B: Shared camera with dual pipelines**
- Use one of the existing AprilTag cameras
- PhotonVision supports multiple pipelines per camera, but only one active at a time
- Would need pipeline switching or running at alternating frames -- adds complexity and reduces effective FPS for both tasks
- Not recommended unless hardware-constrained

Either way, the camera needs calibration in PhotonVision (standard checkerboard calibration). The calibration data provides focal length and distortion coefficients needed for distance estimation.

---

## Step 4: Java Subsystem -- `GamePieceVision`

Following the existing codebase IO pattern. New files:

### `src/main/java/frc/robot/subsystems/gamePieceVision/GamePieceVisionIO.java`

```java
public interface GamePieceVisionIO {
  @AutoLog
  public static class GamePieceVisionIOInputs {
    // Flat arrays for NT serialization (Translation2d[] not supported by AutoLog)
    public double[] ballXPositions = new double[0];    // field X coords (meters)
    public double[] ballYPositions = new double[0];    // field Y coords (meters)
    public double[] ballConfidences = new double[0];   // detection confidence [0,1]
    public int ballCount = 0;
    public boolean connected = false;
    public double latencyMs = 0.0;
  }

  default void updateInputs(GamePieceVisionIOInputs inputs, Pose2d robotPose) {}
}
```

### `src/main/java/frc/robot/subsystems/gamePieceVision/GamePieceVisionIOPhoton.java`

Real implementation -- reads from PhotonCamera, computes field-relative positions:

- Construct with `new PhotonCamera("ballCam")` and camera-to-robot `Transform3d`
- In `updateInputs()`:
  1. Call `camera.getAllUnreadResults()` to get latest detections
  2. For each detected target, extract yaw, pitch, and bounding box area
  3. Estimate distance using pinhole model: `distance = (BALL_DIAMETER * focalLength) / boundingBoxHeightPixels`
     - Alternative: use pitch angle: `distance = (cameraHeight - BALL_RADIUS) / tan(pitch)`
  4. Compute camera-relative position from yaw + distance
  5. Transform to robot-relative using camera-to-robot `Transform3d`
  6. Transform to field-relative using `robotPose`
  7. Populate the inputs arrays

**Distance estimation math** (pitch-based, simpler and more robust):
```
groundDistance = (cameraHeight - ballRadius) / tan(cameraPitch + targetPitch)
```
Where:
- `cameraHeight` = camera Z from `CAMERA_TRANSFORM` (known from CAD)
- `ballRadius` = 0.5 * ball diameter (known from game manual)
- `cameraPitch` = camera pitch angle from `CAMERA_TRANSFORM`
- `targetPitch` = pitch angle to target center from PhotonVision

### `src/main/java/frc/robot/subsystems/gamePieceVision/GamePieceVisionIOSim.java`

Simulation implementation -- uses MapleSim's arena:

- In `updateInputs()`:
  1. Get all ball positions from `SimulatedArena.getInstance().getGamePiecesArrayByType("Fuel")`
  2. Filter to balls within a reasonable detection range (e.g., <5m from robot)
  3. Optionally simulate camera FOV limits and add noise
  4. Populate inputs arrays directly from the Pose3d positions

This reuses the existing simulation infrastructure already in Robot.java line 391:
`SimulatedArena.getInstance().getGamePiecesArrayByType("Fuel")`

### `src/main/java/frc/robot/subsystems/gamePieceVision/GamePieceVision.java`

Main subsystem class:

```java
public class GamePieceVision extends SubsystemBase {
  private final GamePieceVisionIO io;
  private final GamePieceVisionIOInputsAutoLogged inputs = new GamePieceVisionIOInputsAutoLogged();
  private Supplier<Pose2d> poseSupplier;

  // Public accessor for other subsystems
  public List<Translation2d> getDetectedBalls() { ... }

  public void updateInputs() {
    io.updateInputs(inputs, poseSupplier.get());
  }

  public void processState() {
    Logger.processInputs("GamePieceVision", inputs);
    Logger.recordOutput("GamePieceVision/BallPositions", /* Pose2d[] for AdvantageScope viz */);
    Logger.recordOutput("GamePieceVision/BallCount", inputs.ballCount);
  }
}
```

---

## Step 5: Integration into Robot.java

Following the existing pattern in Robot.java:

```java
// Declare
public GamePieceVision gamePieceVision;
public PhotonCamera ballCam;

// In constructor, sim branch:
GamePieceVisionIO gamePieceVisionIO = new GamePieceVisionIOSim();
gamePieceVision = new GamePieceVision(gamePieceVisionIO, swerve::getPose);

// In constructor, real branch:
ballCam = new PhotonCamera("ballCam");
GamePieceVisionIO gamePieceVisionIO = new GamePieceVisionIOPhoton(ballCam, Constants.Vision.BALL_CAM_TRANSFORM);
gamePieceVision = new GamePieceVision(gamePieceVisionIO, swerve::getPose);

// In robotPeriodic():
gamePieceVision.updateInputs();
// ... after CommandScheduler.run() ...
gamePieceVision.processState();
```

---

## Step 6: Constants

Add to `Constants.java`:

```java
public static class GamePieceVision {
  public static final double BALL_DIAMETER_METERS = /* from 2026 game manual */;
  public static final double MAX_DETECTION_RANGE_METERS = 5.0;
  public static final Transform3d BALL_CAM_TRANSFORM = new Transform3d(
      /* camera position from CAD */
  );
}
```

---

## Key Files to Create/Modify

| File | Action |
|------|--------|
| `src/.../gamePieceVision/GamePieceVisionIO.java` | **Create** -- IO interface with @AutoLog inputs |
| `src/.../gamePieceVision/GamePieceVisionIOPhoton.java` | **Create** -- PhotonCamera + distance estimation |
| `src/.../gamePieceVision/GamePieceVisionIOSim.java` | **Create** -- MapleSim ball positions |
| `src/.../gamePieceVision/GamePieceVision.java` | **Create** -- Main subsystem |
| `src/.../constants/Constants.java` | **Modify** -- Add GamePieceVision constants |
| `src/.../Robot.java` | **Modify** -- Instantiate and wire up subsystem |

---

## Future: Path Optimization with Choreo

The `GamePieceVision.getDetectedBalls()` returns `List<Translation2d>` in field coordinates. A future path optimizer would:
1. Read current ball positions from `GamePieceVision`
2. Use a TSP-like solver to find optimal collection order
3. Generate Choreo trajectories between waypoints
4. Execute trajectories with `TrajectoryFollowerCommand`

The subsystem interface is designed to make this straightforward -- field-relative `Translation2d` positions are exactly what Choreo needs for waypoints.

---

## Verification Plan

1. **Simulation test**: Run the robot in simulation, verify `GamePieceVisionIOSim` picks up "Fuel" game pieces from MapleSim arena and logs them correctly in AdvantageScope
2. **Unit test**: Verify distance estimation math with known inputs (camera height, pitch, expected distances)
3. **Integration test**: With PhotonVision running on Mac mini (mac branch), verify detections flow through NT4 to the RoboRIO subsystem
4. **Field test**: Place balls at known positions, verify field-relative estimates are within ~0.3m accuracy
5. **AdvantageScope visualization**: Ball positions should appear correctly overlaid on the field view
