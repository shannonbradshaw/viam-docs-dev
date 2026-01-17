# Stationary Vision Tutorial

**Status:** 🟡 Draft

**Time:** ~1.5 hours
**Components:** Camera + Compute
**Physics required:** None (rendered images only)

---

## Before You Begin

### What is Viam?

Viam lets you build robotics applications the way you build other software. Viam abstracts away hardware concerns and services for common tasks to enable you to focus on your core robotics application. Declare your hardware in a config, write control logic against well-defined APIs for everything, push updates through a CLI. Viam is the development workflow you're used to, applied to physical machines.

Viam works with any hardware:

| Category | Examples |
|----------|----------|
| Cameras | Webcams, depth cameras, thermal, CSI |
| Arms | 6-DOF robot arms, collaborative arms |
| Bases | Wheeled, tracked, holonomic, drones |
| Motors | DC, stepper, servo, brushless |
| Sensors | IMU, GPS, ultrasonic, temperature, humidity |
| Grippers | Parallel jaw, vacuum, custom end effectors |
| Boards | Raspberry Pi, Jetson, Orange Pi, ESP32 |
| LiDAR | 2D and 3D scanning |
| Encoders | Rotary, absolute, incremental |
| Gantries | Linear actuators, multi-axis systems |

If your hardware isn't on the list, you can add support with a custom module by implementing the appropriate API.

This tutorial uses the simplest work cell (camera + compute) to teach patterns that apply to *all* Viam applications.

### What You'll Learn

By the end of this tutorial, you'll understand how to:

| Skill | What It Means | Applies To |
|-------|---------------|------------|
| Configure components | Add hardware to a Viam machine | Any sensor, actuator, or peripheral |
| Add services | Attach capabilities like ML inference | Vision, navigation, motion planning |
| Write control logic | Code that reads sensors and makes decisions | Any automation task |
| Configure automation | Set up data capture, triggers, and alerts | Production monitoring |
| Scale with fragments | Reuse configurations across machines | Any fleet, any size |
| Manage fleets | Monitor, update, and debug remotely | Production operations |
| Build customer apps | Create products on top of Viam | Shipping to your customers |

**These patterns are the same whether you're working with a camera, a robot arm, or a warehouse full of mobile robots.**

## Scenario

You're building a **quality inspection station** for a manufacturing line. Parts move past a camera on a conveyor. Your system must:

1. Detect when a part is present
2. Classify it as PASS or FAIL
3. Log results and trigger alerts on failures
4. Scale to multiple inspection stations
5. Ship as a product your customers can use

---

## What You'll Build

A working inspection system with:

- A camera streaming live images
- An ML model classifying parts as pass/fail
- Business logic that triggers alerts on failures
- A second station added to your fleet
- A dashboard showing inspection results across stations
- A customer-facing web app with your branding

---

## Tutorial Flow

### Part 1: Prototype (~25 min)

**Goal:** Get a working detection pipeline on one simulated camera.

**Skills:** Installing viam-server, connecting a machine to Viam, component configuration, adding services, writing SDK code.

#### 1.1 Launch the Simulation

Click the button below to launch your simulation environment:

[BUTTON: Launch Simulation]

After a few seconds, you'll see a split-screen view:

[SCREENSHOT: Simulation interface showing work cell on left, terminal on right]

**Left panel:** A 3D view of your work cell—a conveyor belt with an overhead camera. Parts will appear here during the tutorial.

**Right panel:** A terminal connected to the Linux machine running this simulation. This is the same terminal you'd use if you SSH'd into a Raspberry Pi or any other device.

> **What you're looking at:** This isn't a sandbox or a toy. It's an actual Linux machine running in the cloud with simulated hardware attached. Everything you do here—installing software, configuring components, writing code—works exactly the same way on real hardware.

#### 1.2 Create a Machine in Viam

Before the simulated machine can talk to Viam, you need to create a machine entry in the Viam app. This is where you'll configure components, view data, and manage your machine.

**Create an account** (if you don't have one):

1. Open [app.viam.com](https://app.viam.com) in a new browser tab
2. Click **Sign Up** and create an account with your email or Google/GitHub

[SCREENSHOT: Viam app sign-up page]

**Create a new machine:**

1. From the Viam app home screen, click **+ Add machine**
2. Give your machine a name like `inspection-station-1`
3. Click **Add machine**

[SCREENSHOT: Add machine dialog with name field]

You'll land on your machine's page. Notice the status indicator shows **Offline**—that's expected. The machine exists in Viam's cloud, but nothing is running on your simulated hardware yet.

**Get the install command:**

1. Click the **Setup** tab
2. You'll see a `curl` command that looks like this:

```bash
curl -fsSL https://app.viam.com/install | sh -s -- --apisecret <your-secret>
```

3. Click the **Copy** button to copy this command

[SCREENSHOT: Setup tab showing the install command with copy button highlighted]

> **Keep this tab open.** You'll paste this command into the simulation terminal in the next step.

This command downloads and installs `viam-server`, then configures it with credentials that link it to this specific machine in your Viam account. Every Viam machine—whether it's a Raspberry Pi in your garage or an industrial robot in a factory—starts the same way.

#### 1.3 Install viam-server

Now you'll install `viam-server` on the simulation machine. This is the software that runs on every Viam-managed device—it connects to the cloud, loads your configuration, and provides APIs for controlling components.

**Run the install command:**

1. Click in the terminal panel on the right side of your simulation
2. Paste the install command you copied from the Viam app (Ctrl+V or Cmd+V)
3. Press Enter

You'll see output as the installer runs:

```
Downloading viam-server...
Installing to /usr/local/bin/viam-server...
Creating configuration directory...
Starting viam-server...
```

[SCREENSHOT: Terminal showing successful viam-server installation]

The installation takes about 30 seconds. When it completes, `viam-server` starts automatically as a background service.

**Verify the connection:**

Switch back to your Viam app browser tab. The status indicator should now show **Online** with a green dot.

[SCREENSHOT: Machine page showing Online status]

This is the moment: the Linux machine you're looking at in the simulation is now connected to Viam's cloud. You can configure it, monitor it, and control it from anywhere in the world.

> **Troubleshooting:**
> - **Still showing Offline?** Wait 10-15 seconds and refresh the page. The connection can take a moment to establish.
> - **Installation failed?** Make sure you copied the entire command, including the `--apisecret` flag and its value.
> - **Permission denied?** The install script should handle this, but if you see permission errors, prefix the command with `sudo`.

This is the same process you'd follow on real hardware. SSH into a Raspberry Pi, run the install command, and it connects to Viam. The only difference here is that your "SSH" is a browser-based terminal.

#### 1.4 Configure the Camera

Your machine is online but empty—it doesn't know about any hardware yet. You'll now add the camera as a *component*.

In Viam, a component is any piece of hardware: cameras, motors, arms, sensors, grippers. You configure components by declaring what they are, and Viam handles the drivers and communication.

**Add a camera component:**

1. In the Viam app, click the **Config** tab
2. Click **+ Add component**
3. For **Type**, select `camera`
4. For **Model**, select `webcam` (this is the *driver* model—the software that knows how to talk to this type of camera)

   > The simulated camera presents itself as a standard webcam to the operating system—just like a USB camera would on a real machine.

5. Name it `inspection-cam`
6. Click **Create**

[SCREENSHOT: Add component dialog with camera settings]

**Configure the camera source:**

After creating the component, you'll see a configuration panel. The `webcam` model needs to know which video device to use.

1. In the **Attributes** section, click the **video_path** dropdown
2. Select the available video device (typically `/dev/video0` or similar)
3. Click **Save config** in the top right

[SCREENSHOT: Camera configuration panel with video_path selected]

When you save, viam-server automatically reloads and applies the new configuration. You don't need to restart anything—the system picks up changes within seconds.

> **What just happened:** You declared "this machine has a camera called `inspection-cam`" by editing configuration in a web UI. Behind the scenes, viam-server loaded the appropriate driver, connected to the video device, and made the camera available through Viam's camera API. You'd do exactly the same thing for a motor, an arm, or any other component—just select a different type and model.

#### 1.5 Test the Camera

Let's verify the camera is working. Every component in Viam has a built-in test panel right in the configuration view.

**Open the test panel:**

1. You should still be on the **Configure** tab with your `inspection-cam` selected
2. Look for the **Test** section at the bottom of the camera's configuration panel
3. Click **Toggle stream** to start the live feed

You should see a live video feed from the simulated camera—an overhead view of the conveyor/staging area.

[SCREENSHOT: Camera test panel showing live feed in Configure tab]

**Capture an image:**

Click **Get image** to capture a single frame. The image appears in the panel and can be downloaded.

> **What you're seeing:** This isn't a special debugging view. The test panel uses the exact same APIs that your code will use. When you click "Get image," Viam calls the camera's `GetImage` method—the same method you'll call from Python or Go in a few minutes.

This pattern applies to all components. Motors have test controls for setting velocity. Arms have controls for moving joints. You can test any component directly from its configuration panel.

#### 1.6 Add a Vision Service

Now you'll add machine learning to your camera. In Viam, ML capabilities are provided by *services*—higher-level functionality that operates on components.

**Components vs. Services:**
- **Components** are hardware: cameras, motors, arms
- **Services** are capabilities: vision (ML inference), navigation (path planning), motion (arm kinematics)

Services often *use* components. A **vision service** takes images from a camera, runs them through an ML model, and returns structured results—detections with bounding boxes and labels, or classifications with confidence scores. Your code calls the vision service API; the service handles everything else.

To work with ML models, the vision service needs an **ML model service**. The ML model service loads a trained model (TensorFlow, ONNX,or PyTorch) and exposes an `Infer()` method that takes input tensors and returns output tensors. The vision service handles the rest: converting camera images to the tensor format the model expects, calling the ML model service, and interpreting the raw tensor outputs into usable detections or classifications.

When using computer vision, as in this tutorial, you need to configure both: first the ML model service (which loads the model), then the vision service (which connects the camera to the model).

**Add the ML model service:**

The ML model service loads a trained model and makes it available for inference.

1. In the Viam app, click the **Configure** tab
2. Click **+** next to your machine in the left sidebar
3. Select **Service**, then **ML model**
4. Search for `TFLite CPU` and select it
5. Name it `part-classifier`
6. Click **Create**

[SCREENSHOT: Add service dialog for ML model]

**Select a model from the registry:**

1. In the `part-classifier` configuration panel, click **Select model**
2. Click the **Registry** tab
3. Search for `part-quality-classifier` (a model we created for this tutorial that classifies parts as PASS or FAIL)
4. Select it from the list
5. Click **Save config**

[SCREENSHOT: Select model dialog showing registry models]

> **Your own models:** For a different application, you'd train a model on your specific data and upload it to the registry. The registry handles versioning and deployment of ML models across your fleet.

**Add the vision service:**

Now add a vision service that connects your camera to the ML model service. The vision service captures images, sends them through the model, and returns detections you can use in your code.

1. Click **+** next to your machine
2. Select **Service**, then **Vision**
3. Search for `ML model` and select it
4. Name it `part-detector`
5. Click **Create**

**Link the vision service to the camera and model:**

1. In the `part-detector` configuration panel, find the **Default Camera** dropdown
2. Select `inspection-cam`
3. Find the **ML Model** dropdown
4. Select `part-classifier` (the ML model service you just created)
5. Click **Save config**

[SCREENSHOT: Vision service configuration linked to ML model]

**Test the vision service:**

1. You should still be on the **Configure** tab
2. Find the `part-detector` service you just created
3. Look for the **Test** section at the bottom of its configuration panel
4. If not already selected, select `inspection-cam` as the camera source
5. Click **Get detections**

You should see the camera image with detection results—bounding boxes around detected parts with labels (PASS or FAIL) and confidence scores.

[SCREENSHOT: Vision service test panel showing detection results with bounding boxes]

> **What you've built:** A complete ML inference pipeline. The vision service grabs an image from the camera, runs it through the TensorFlow Lite model, and returns structured detection results. This same pattern works for any ML task—object detection, classification, segmentation—you just swap the model.

You've now configured a working inspection system entirely through the Viam app—no code yet. Next, you'll write code to interact with this system programmatically.

#### 1.7 Run an Inspection Session

So far you've configured everything through the Viam app. Now you'll write code that connects to your machine remotely and runs inspections—the same code that will eventually run in production.

During development, you run this code on your laptop. It connects to the machine over the network, uses the camera and vision service you configured, and lets you iterate quickly without deploying anything. When you're ready for production, you upload your module to the Viam registry and add it to your machine's configuration—just like you added the ML model service earlier. The machine pulls the module and runs your service. No revisions required for production.

This is the **module-first development pattern**: prototype your code in a package that will ultimately become your production logic, test it locally against remote hardware, then publish to the registry and configure your machines to use it.

Viam provides SDKs for Python, Go, TypeScript, C++, and Flutter. We'll use Python and Go here—choose whichever you're more comfortable with.

##### Set up your project

Create a minimal project with two files: your service logic and a CLI to test it.

{{< tabs >}}
{{% tab name="Go" %}}

```bash
mkdir inspection-module && cd inspection-module
go mod init inspection-module
go get go.viam.com/rdk
```

Create two files:

```
inspection-module/
├── inspector.go    # Your service logic
├── main.go         # CLI for testing
└── go.mod
```

{{% /tab %}}
{{% tab name="Python" %}}

```bash
mkdir inspection-module && cd inspection-module
python3 -m venv venv && source venv/bin/activate
pip install viam-sdk Pillow
```

Create two files:

```
inspection-module/
├── inspector.py    # Your service logic
└── cli.py          # CLI for testing
```

{{% /tab %}}
{{< /tabs >}}

The key insight: your service logic lives in one file and the CLI imports it. During development, you run the CLI on your laptop—it connects to the remote machine and uses the camera and vision service over the network. You iterate locally without deploying anything.

##### Write the CLI

Before writing service logic, create the CLI that connects to your machine and converts it to dependencies. This CLI stays the same across iterations—you only change what you call on the inspector.

{{< tabs >}}
{{% tab name="Go" %}}

Create `main.go`:

```go
package main

import (
	"context"
	"flag"
	"fmt"

	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/robot/client"
	"go.viam.com/utils/rpc"
)

func main() {
	host := flag.String("host", "", "Machine address")
	apiKey := flag.String("api-key", "", "API key")
	apiKeyID := flag.String("api-key-id", "", "API key ID")
	flag.Parse()

	ctx := context.Background()
	logger := logging.NewLogger("cli")

	// 1. Connect to the remote machine
	machine, err := client.New(ctx, *host, logger,
		client.WithDialOptions(rpc.WithEntityCredentials(*apiKeyID,
			rpc.Credentials{Type: rpc.CredentialsTypeAPIKey, Payload: *apiKey})))
	if err != nil {
		logger.Fatal(err)
	}
	defer machine.Close(ctx)

	// 2. Convert machine resources to Dependencies
	deps := make(resource.Dependencies)
	for _, name := range machine.ResourceNames() {
		r, err := machine.ResourceByName(name)
		if err != nil {
			continue
		}
		deps[name] = r
	}

	// 3. Create inspector with Dependencies - same call the module would make
	cfg := Config{
		Camera:        "inspection-cam",
		VisionService: "part-detector",
	}
	inspector, err := NewInspector(deps, cfg, logger)
	if err != nil {
		logger.Fatal(err)
	}

	// TODO: Call inspector methods here
	fmt.Println("Inspector ready")
}
```

{{% /tab %}}
{{% tab name="Python" %}}

Create `cli.py`:

```python
import asyncio
import sys
from viam.robot.client import RobotClient

from inspector import Inspector, Config

async def main():
    host = sys.argv[1] if len(sys.argv) > 1 else ""
    api_key = sys.argv[2] if len(sys.argv) > 2 else ""
    api_key_id = sys.argv[3] if len(sys.argv) > 3 else ""

    if not all([host, api_key, api_key_id]):
        print("Usage: python cli.py HOST API_KEY API_KEY_ID")
        return

    # 1. Connect to the remote machine
    robot = await RobotClient.at_address(
        host,
        RobotClient.Options.with_api_key(api_key=api_key, api_key_id=api_key_id)
    )

    # 2. Convert machine resources to dependencies dict
    deps = {}
    for name in robot.resource_names:
        deps[name] = robot.get_component(name)

    # 3. Create inspector with dependencies - same call the module would make
    cfg = Config(camera="inspection-cam", vision_service="part-detector")
    inspector = await Inspector.new(deps, cfg)

    # TODO: Call inspector methods here
    print("Inspector ready")

    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
```

{{% /tab %}}
{{< /tabs >}}

The key is step 2→3: convert machine resources to a `Dependencies` map, then pass it to `NewInspector`. This is exactly what the module system does when running your code in production. The constructor signature is identical in both contexts.

**Get your API credentials:**

1. In the Viam app, go to your machine's page
2. Click the **Code sample** tab
3. Toggle **Include API key** to see your credentials
4. Copy the host address, API key, and API key ID

[SCREENSHOT: Code sample tab showing API credentials]

Now you'll build the inspector through three iterations, testing each change against real hardware.

##### Iteration 1: Capture an image

Start with the simplest operation—grab an image from the camera.

{{< tabs >}}
{{% tab name="Go" %}}

Create `inspector.go`:

```go
package main

import (
	"context"
	"image/jpeg"
	"os"

	"go.viam.com/rdk/components/camera"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/vision"
)

// Config declares which dependencies the inspector needs by name.
type Config struct {
	Camera        string
	VisionService string
}

// Inspector is your service. It holds references to its dependencies.
type Inspector struct {
	cam      camera.Camera
	detector vision.Service
	camName  string
	logger   logging.Logger
}

// NewInspector creates an inspector by extracting dependencies from the map.
// This signature is what the module system calls in production.
func NewInspector(deps resource.Dependencies, cfg Config, logger logging.Logger) (*Inspector, error) {
	cam, err := camera.FromDependencies(deps, cfg.Camera)
	if err != nil {
		return nil, err
	}
	detector, err := vision.FromDependencies(deps, cfg.VisionService)
	if err != nil {
		return nil, err
	}

	return &Inspector{
		cam:      cam,
		detector: detector,
		camName:  cfg.Camera,
		logger:   logger,
	}, nil
}

func (i *Inspector) CaptureImage(ctx context.Context) error {
	img, _, err := i.cam.Image(ctx, "", nil)
	if err != nil {
		return err
	}

	f, err := os.Create("snapshot.jpg")
	if err != nil {
		return err
	}
	defer f.Close()

	return jpeg.Encode(f, img, nil)
}
```

Update `main.go` to call it:

```go
// Replace the TODO line with:
if err := inspector.CaptureImage(ctx); err != nil {
    logger.Fatal(err)
}
fmt.Println("Saved snapshot.jpg")
```

{{% /tab %}}
{{% tab name="Python" %}}

Create `inspector.py`:

```python
from dataclasses import dataclass
from viam.components.camera import Camera
from viam.services.vision import VisionClient

@dataclass
class Config:
    camera: str
    vision_service: str

class Inspector:
    def __init__(self, cam: Camera, detector: VisionClient, cam_name: str):
        self.cam = cam
        self.detector = detector
        self.cam_name = cam_name

    @classmethod
    async def new(cls, deps: dict, cfg: Config) -> "Inspector":
        """Create an inspector by extracting dependencies from the map.
        This signature is what the module system calls in production."""
        cam = deps.get(cfg.camera) or next(
            (v for k, v in deps.items() if k.name == cfg.camera), None
        )
        detector = deps.get(cfg.vision_service) or next(
            (v for k, v in deps.items() if k.name == cfg.vision_service), None
        )
        return cls(cam, detector, cfg.camera)

    async def capture_image(self) -> None:
        img = await self.cam.get_image()
        img.save("snapshot.jpg")
```

Update `cli.py` to call it:

```python
# Replace the TODO line with:
await inspector.capture_image()
print("Saved snapshot.jpg")
```

{{% /tab %}}
{{< /tabs >}}

**Test it:**

```bash
go run . -host YOUR_HOST -api-key YOUR_KEY -api-key-id YOUR_KEY_ID
# or: python cli.py YOUR_HOST YOUR_KEY YOUR_KEY_ID
```

```
Inspector ready
Saved snapshot.jpg
```

Open `snapshot.jpg`—you should see the current view from your inspection camera. This image was captured on the remote machine and transferred to your laptop.

##### Iteration 2: Run detection

Add a method to run the ML model and get classification results.

{{< tabs >}}
{{% tab name="Go" %}}

Add to `inspector.go`:

```go
type DetectionResult struct {
	Label      string
	Confidence float64
}

func (i *Inspector) Detect(ctx context.Context) (*DetectionResult, error) {
	detections, err := i.detector.DetectionsFromCamera(ctx, i.camName, nil)
	if err != nil {
		return nil, err
	}

	if len(detections) == 0 {
		return &DetectionResult{Label: "NO_DETECTION", Confidence: 0}, nil
	}

	// Find highest confidence detection
	best := detections[0]
	for _, d := range detections[1:] {
		if d.Score() > best.Score() {
			best = d
		}
	}

	return &DetectionResult{Label: best.Label(), Confidence: best.Score()}, nil
}
```

Update `main.go`:

```go
// Replace previous call with:
result, err := inspector.Detect(ctx)
if err != nil {
    logger.Fatal(err)
}
fmt.Printf("Detection: %s (%.1f%% confidence)\n", result.Label, result.Confidence*100)
```

{{% /tab %}}
{{% tab name="Python" %}}

Add to `inspector.py`:

```python
from dataclasses import dataclass

@dataclass
class DetectionResult:
    label: str
    confidence: float

class Inspector:
    # ... existing __init__ and capture_image ...

    async def detect(self) -> DetectionResult:
        detections = await self.detector.get_detections_from_camera(self.cam_name)

        if not detections:
            return DetectionResult(label="NO_DETECTION", confidence=0.0)

        best = max(detections, key=lambda d: d.confidence)
        return DetectionResult(label=best.class_name, confidence=best.confidence)
```

Update `cli.py`:

```python
# Replace previous call with:
result = await inspector.detect()
print(f"Detection: {result.label} ({result.confidence*100:.1f}% confidence)")
```

{{% /tab %}}
{{< /tabs >}}

**Test it:**

```bash
go run . -host YOUR_HOST -api-key YOUR_KEY -api-key-id YOUR_KEY_ID
```

```
Inspector ready
Detection: PASS (94.2% confidence)
```

You're now running ML inference on the remote machine from your laptop. The image capture and model execution happen on the machine; only the results come back.

##### Iteration 3: Add inspection logic with reject placeholder

Add the complete inspection method that determines whether to reject a part. For now, `would_reject` is just a flag—you'll connect it to an actual reject mechanism later.

{{< tabs >}}
{{% tab name="Go" %}}

Add to `inspector.go`:

```go
type InspectionResult struct {
	Label       string
	Confidence  float64
	WouldReject bool
}

func (i *Inspector) Inspect(ctx context.Context) (*InspectionResult, error) {
	detection, err := i.Detect(ctx)
	if err != nil {
		return nil, err
	}

	// Reject if FAIL detected with sufficient confidence
	wouldReject := detection.Label == "FAIL" && detection.Confidence > 0.7

	return &InspectionResult{
		Label:       detection.Label,
		Confidence:  detection.Confidence,
		WouldReject: wouldReject,
	}, nil
}
```

Update `main.go`:

```go
// Replace previous call with:
result, err := inspector.Inspect(ctx)
if err != nil {
    logger.Fatal(err)
}
fmt.Printf("Inspection: %s (%.1f%% confidence)\n", result.Label, result.Confidence*100)
fmt.Printf("Would reject: %v\n", result.WouldReject)
```

{{% /tab %}}
{{% tab name="Python" %}}

Add to `inspector.py`:

```python
@dataclass
class InspectionResult:
    label: str
    confidence: float
    would_reject: bool

class Inspector:
    # ... existing methods ...

    async def inspect(self) -> InspectionResult:
        detection = await self.detect()

        # Reject if FAIL detected with sufficient confidence
        would_reject = detection.label == "FAIL" and detection.confidence > 0.7

        return InspectionResult(
            label=detection.label,
            confidence=detection.confidence,
            would_reject=would_reject
        )
```

Update `cli.py`:

```python
# Replace previous call with:
result = await inspector.inspect()
print(f"Inspection: {result.label} ({result.confidence*100:.1f}% confidence)")
print(f"Would reject: {result.would_reject}")
```

{{% /tab %}}
{{< /tabs >}}

**Test it:**

```bash
go run . -host YOUR_HOST -api-key YOUR_KEY -api-key-id YOUR_KEY_ID
```

```
Inspector ready
Inspection: PASS (94.2% confidence)
Would reject: false
```

Or if a defect is detected:

```
Inspection: FAIL (87.3% confidence)
Would reject: true
```

The `would_reject` flag doesn't do anything yet—there's no reject mechanism. You'll add that hardware and connect it in Part 3.

##### What you've built

In three iterations, you went from nothing to a working inspection system:

1. **Capture image** — Proved you can access remote hardware
2. **Run detection** — Added ML inference
3. **Inspection logic** — Made a decision (reject or not)

Each iteration was: edit → rebuild → run → see results. No deployment, no waiting. Your code ran on your laptop while the hardware ran on the machine.

Notice the pattern: your `NewInspector` function takes `resource.Dependencies` and extracts what it needs by name. The CLI builds that Dependencies map from the remote machine; in production, the module system provides it. **Same constructor, same code, different context.** That's module-first development.

**Checkpoint:** You can write code that talks to your machine. The inspection logic is ready—it just needs hardware to act on its decisions.

---

### Part 2: Automate (~15 min)

**Goal:** Configure continuous data capture and alerting so inspections run automatically.

**Skills:** Data capture configuration, cloud sync, filtered cameras, triggers and notifications.

In Part 1, you set up the detection pipeline and wrote inspection logic using the module-first pattern. The `would_reject` flag is a placeholder—you'll connect it to real hardware in Part 3. First, let's get the rest of the system working: continuous data capture, cloud sync, and failure alerts. We're building a complete prototype quickly, then circling back to close the control loop.

Data capture in Viam is configuration, not code. You enable capture on components and services, and Viam handles the rest—storing locally, syncing to the cloud, making it queryable. No scripts to deploy, no processes to manage.

#### 2.1 Configure Data Capture

**Enable data capture on the vision service:**

1. In the Viam app, go to your machine's **Config** tab
2. Find the `part-detector` vision service
3. Click the **Data capture** section to expand it
4. Toggle **Enable data capture** to on
5. Set the capture frequency: `2` seconds
6. Select the method to capture: `GetDetectionsFromCamera`
7. Click **Save config**

[SCREENSHOT: Vision service data capture configuration]

**Also capture camera images:**

You want the raw images alongside detection results—so you can review what the model saw and use images to improve your model later.

1. Find the `inspection-cam` camera in your config
2. Expand **Data capture**
3. Toggle **Enable data capture** to on
4. Set frequency: `2` seconds (matching the vision service)
5. Click **Save config**

[SCREENSHOT: Camera data capture configuration]

**Verify it's working:**

1. Go to the **Control** tab
2. Find the `part-detector` vision service
3. You should see a small indicator showing data is being captured

The machine is now capturing detection results and images every 2 seconds—whether or not you're connected.

#### 2.2 View Data in the Cloud

Data captured on the machine automatically syncs to Viam's cloud. You don't need to configure sync separately—it happens in the background.

**Check the data:**

1. In the Viam app, click **Data** in the left sidebar (at the organization level, not the machine)
2. Wait 1-2 minutes for initial sync
3. You should see detection results and images appearing

[SCREENSHOT: Data tab showing captured detections]

**Verify the data includes:**

- **Detection results** — Each row shows label (PASS/FAIL) and confidence score
- **Camera images** — Click any row to see the image that was analyzed
- **Timestamps** — When each capture occurred
- **Machine ID** — Which machine captured it (matters when you have multiple stations)

**Filter and query:**

1. Click **Filter** and select your machine: `inspection-station-1`
2. Set time range to "Last hour"
3. You can also filter by component to see only vision service results or only camera images

[SCREENSHOT: Data tab with filters applied]

This data serves multiple purposes:
- **Compliance** — Auditable record of every inspection
- **Quality trends** — "FAIL rate increased 20% this week"
- **Model improvement** — Export images to retrain your ML model
- **Incident review** — "Show me all FAILs from Tuesday's shift"

#### 2.3 Add a Filtered Camera for Failures

You're capturing every inspection, but you want to treat failures specially—capture higher-resolution images and trigger alerts. A *filtered camera* wraps your existing camera and vision service, only outputting when detections match your criteria.

**Create the filtered camera:**

1. In the Viam app, go to **Config** tab
2. Click **+ Create component**
3. For **Type**, select `camera`
4. For **Model**, search for and select `filtered-camera`
5. Name it `fail-detector-cam`
6. Click **Create**

**Configure the filter:**

```json
{
  "camera": "inspection-cam",
  "vision_service": "part-detector",
  "classifications": {
    "labels": ["FAIL"]
  },
  "confidence_threshold": 0.7
}
```

This camera only outputs an image when `part-detector` detects FAIL with ≥70% confidence.

[SCREENSHOT: Filtered camera configuration]

**Enable data capture on it:**

1. On `fail-detector-cam`, expand **Data capture**
2. Toggle **Enable data capture** to on
3. Set frequency: `1` second (check more frequently for failures)
4. Click **Save config**

**Verify it works:**

1. Go to the **Control** tab
2. Find `fail-detector-cam`
3. The stream shows nothing most of the time—it only shows an image when a FAIL is detected
4. Wait for a failure (or trigger one in the simulation) and confirm you see the image

Now you're capturing all inspections at 2-second intervals, plus high-frequency capture specifically when failures occur.

#### 2.4 Configure Failure Alerts

Capturing failure data is useful for analysis, but you need to know immediately when defects occur. Viam's trigger system sends notifications when specific events happen—no code required.

**Add a trigger:**

1. In the Viam app, go to **Config** tab
2. Scroll to the **Triggers** section
3. Click **+ Add trigger**
4. Configure:
   - **Name**: `fail-alert`
   - **Event type**: `Data has been synced to the cloud`
   - **Data source**: Select `fail-detector-cam`

**Add email notification:**

1. Under **Notifications**, click **Add notification**
2. Select **Email**
3. Enter your email address
4. Set **Seconds between notifications**: `3600` (one alert per hour max—you don't want inbox spam)
5. Click **Save config**

[SCREENSHOT: Trigger configuration with email notification]

**Test the alert:**

1. In the simulation, trigger a FAIL detection (place a defective part)
2. Wait 1-2 minutes for the data to sync
3. Check your email—you should receive a failure notification

[SCREENSHOT: Email notification received]

> **Going further:** You can configure webhook notifications to integrate with Slack, PagerDuty, or custom systems. The webhook receives the detection data as JSON, and your endpoint can format and route alerts however you need.

#### 2.5 Development vs. Production

You now have two ways to run inspections:

| Development (Part 1) | Production (Part 2) |
|---------------------|---------------------|
| Your inspector code runs on your laptop | Data capture runs on the machine |
| You trigger inspections manually | Inspections run continuously |
| Results print to your terminal | Results sync to cloud |
| Good for: testing, debugging, iterating on logic | Good for: ongoing monitoring, compliance, alerting |

**Both remain valuable.** Your inspector code from Part 1 is still useful:
- Test changes to inspection logic before deploying
- Debug issues by running inspections manually
- Add new features (like the reject mechanism in Part 3)

Data capture provides the production foundation:
- Runs 24/7 without intervention
- Creates audit trail for compliance
- Powers dashboards and alerting
- Feeds data back for ML model improvement

> **The pattern:** The machine runs viam-server with configured components and services. Data capture handles continuous operation. Triggers handle alerting. Your module code (when deployed) handles control logic like rejection. You configure the platform; you don't deploy scripts.

**Checkpoint:** Inspection data flows continuously from machine to cloud. You get alerts when failures occur. All through configuration—no code deployed to the machine yet.

---

### Part 3: Control (~10 min)

**Goal:** Add a reject mechanism and connect it to your inspection logic.

**Skills:** Adding actuators, updating module dependencies, closing the control loop.

#### 3.1 Add the Reject Mechanism

Your inspection system detects failures but doesn't act on them yet. The `would_reject` flag in your code is just a placeholder. Now you'll add hardware to actually reject defective parts.

**Add the reject mechanism to your work cell:**

Click the button below to add a part rejector to your simulation:

[BUTTON: Add Reject Mechanism]

The simulation now shows a pneumatic pusher mounted beside the conveyor. When activated, it pushes parts into a reject bin.

[SCREENSHOT: Work cell with reject mechanism visible]

**Configure it in Viam:**

1. In the Viam app, go to your machine's **Config** tab
2. Click **+ Create component**
3. For **Type**, select `motor`
4. For **Model**, select `gpio` (or the appropriate model for your simulation)
5. Name it `rejector`
6. Click **Create**

**Configure the motor:**

Set the board and pin that controls the rejector:

```json
{
  "board": "local",
  "pins": {
    "pwm": "32"
  }
}
```

[SCREENSHOT: Rejector motor configuration]

**Test it manually:**

1. Go to the **Control** tab
2. Find the `rejector` motor
3. Click **Run** to activate it briefly
4. Watch the simulation—the pusher should extend and retract

[SCREENSHOT: Motor control panel with Run button]

The hardware works. Now connect it to your inspection logic.

#### 3.2 Update Your Code

Add the rejector to your inspector so it can act on failures.

{{< tabs >}}
{{% tab name="Go" %}}

**Update `inspector.go`:**

First, add the motor to your imports and Config:

```go
import (
	// ... existing imports ...
	"go.viam.com/rdk/components/motor"
)

// Config declares which dependencies the inspector needs by name.
type Config struct {
	Camera        string
	VisionService string
	Rejector      string  // Add this
}
```

Update `NewInspector` to extract the motor:

```go
func NewInspector(deps resource.Dependencies, cfg Config, logger logging.Logger) (*Inspector, error) {
	cam, err := camera.FromDependencies(deps, cfg.Camera)
	if err != nil {
		return nil, err
	}
	detector, err := vision.FromDependencies(deps, cfg.VisionService)
	if err != nil {
		return nil, err
	}
	rejector, err := motor.FromDependencies(deps, cfg.Rejector)
	if err != nil {
		return nil, err
	}

	return &Inspector{
		cam:      cam,
		detector: detector,
		rejector: rejector,
		camName:  cfg.Camera,
		logger:   logger,
	}, nil
}
```

Add the rejector field to the struct:

```go
type Inspector struct {
	cam      camera.Camera
	detector vision.Service
	rejector motor.Motor  // Add this
	camName  string
	logger   logging.Logger
}
```

Add a `Reject` method:

```go
func (i *Inspector) Reject(ctx context.Context) error {
	// Activate the rejector briefly to push the part
	if err := i.rejector.GoFor(ctx, 100, 1, nil); err != nil {
		return err
	}
	i.logger.Info("Part rejected")
	return nil
}
```

Update `Inspect` to call `Reject`:

```go
func (i *Inspector) Inspect(ctx context.Context) (*InspectionResult, error) {
	detection, err := i.Detect(ctx)
	if err != nil {
		return nil, err
	}

	shouldReject := detection.Label == "FAIL" && detection.Confidence > 0.7

	// Actually reject the part
	if shouldReject {
		if err := i.Reject(ctx); err != nil {
			i.logger.Errorw("Failed to reject part", "error", err)
		}
	}

	return &InspectionResult{
		Label:      detection.Label,
		Confidence: detection.Confidence,
		Rejected:   shouldReject,  // Renamed from WouldReject
	}, nil
}
```

Update the result struct:

```go
type InspectionResult struct {
	Label      string
	Confidence float64
	Rejected   bool  // Was WouldReject, now actually happens
}
```

{{% /tab %}}
{{% tab name="Python" %}}

**Update `inspector.py`:**

First, add the motor import and update Config:

```python
from viam.components.motor import Motor

@dataclass
class Config:
    camera: str
    vision_service: str
    rejector: str  # Add this
```

Update the `new` method to extract the motor:

```python
@classmethod
async def new(cls, deps: dict, cfg: Config) -> "Inspector":
    cam = next((v for k, v in deps.items() if k.name == cfg.camera), None)
    detector = next((v for k, v in deps.items() if k.name == cfg.vision_service), None)
    rejector = next((v for k, v in deps.items() if k.name == cfg.rejector), None)
    return cls(cam, detector, rejector, cfg.camera)
```

Update `__init__`:

```python
def __init__(self, cam: Camera, detector: VisionClient, rejector: Motor, cam_name: str):
    self.cam = cam
    self.detector = detector
    self.rejector = rejector  # Add this
    self.cam_name = cam_name
```

Add a `reject` method:

```python
async def reject(self) -> None:
    """Activate the rejector to push the part off the line."""
    await self.rejector.go_for(rpm=100, revolutions=1)
    print("Part rejected")
```

Update `inspect` to call `reject`:

```python
async def inspect(self) -> InspectionResult:
    detection = await self.detect()

    should_reject = detection.label == "FAIL" and detection.confidence > 0.7

    # Actually reject the part
    if should_reject:
        try:
            await self.reject()
        except Exception as e:
            print(f"Failed to reject part: {e}")

    return InspectionResult(
        label=detection.label,
        confidence=detection.confidence,
        rejected=should_reject  # Renamed from would_reject
    )
```

Update the result class:

```python
@dataclass
class InspectionResult:
    label: str
    confidence: float
    rejected: bool  # Was would_reject, now actually happens
```

{{% /tab %}}
{{< /tabs >}}

**Update `main.go` (or `cli.py`):**

Add the rejector to your config:

{{< tabs >}}
{{% tab name="Go" %}}

```go
cfg := Config{
    Camera:        "inspection-cam",
    VisionService: "part-detector",
    Rejector:      "rejector",  // Add this
}
```

Update the output:

```go
fmt.Printf("Inspection: %s (%.1f%% confidence)\n", result.Label, result.Confidence*100)
fmt.Printf("Rejected: %v\n", result.Rejected)
```

{{% /tab %}}
{{% tab name="Python" %}}

```python
cfg = Config(
    camera="inspection-cam",
    vision_service="part-detector",
    rejector="rejector"  # Add this
)
```

Update the output:

```python
print(f"Inspection: {result.label} ({result.confidence*100:.1f}% confidence)")
print(f"Rejected: {result.rejected}")
```

{{% /tab %}}
{{< /tabs >}}

#### 3.3 Test the Complete Loop

Run your updated code:

```bash
go run . -host YOUR_HOST -api-key YOUR_KEY -api-key-id YOUR_KEY_ID
```

With a passing part:
```
Inspector ready
Inspection: PASS (94.2% confidence)
Rejected: false
```

With a failing part:
```
Inspector ready
Inspection: FAIL (87.3% confidence)
Part rejected
Rejected: true
```

Watch the simulation—when a FAIL is detected, the rejector activates and pushes the part into the reject bin.

[SCREENSHOT: Simulation showing part being rejected]

**You've closed the control loop.** Your system now:
1. **Sees** — Camera captures the part
2. **Thinks** — Vision service classifies it
3. **Acts** — Rejector removes defective parts

This is the complete sense-think-act cycle that defines robotic systems.

#### 3.4 The Pattern

Look at how little changed to add an actuator:

1. **Config** — Added one field: `Rejector string`
2. **Constructor** — Added one extraction: `motor.FromDependencies`
3. **Logic** — Added one method call: `i.Reject(ctx)`

The module-first pattern made this easy. Your constructor already takes `Dependencies`—adding a new dependency is just one more extraction. The CLI already builds the Dependencies map—the motor is automatically included.

When you deploy this as a module, the same code runs on the machine. The module system provides the Dependencies; your constructor extracts what it needs. Nothing changes.

**Checkpoint:** Your inspection system takes action. Detect → Decide → Reject. The control loop is closed.

---

### Part 4: Scale (~10 min)

**Goal:** Add a second inspection station.

**Skills:** Configuration reuse with fragments, fleet basics.

#### 3.1 Create a Fragment

You have one working inspection station. Now imagine you need 10 more—or 100. Manually copying configuration to each machine would be tedious and error-prone.

Viam solves this with *fragments*: reusable configuration blocks that can be applied to any machine. Think of a fragment as a template. Define your camera, vision service, data capture, and triggers once, then apply that template to as many machines as you need.

**Create a fragment from your configuration:**

1. In the Viam app, click **Fragments** in the left sidebar
2. Click **+ Create fragment**
3. Name it `inspection-station`
4. Click **Create**

[SCREENSHOT: Create fragment dialog]

**Add your configuration to the fragment:**

Now you'll copy the configuration from your machine into the fragment.

1. Go back to your `inspection-station-1` machine
2. Click the **Config** tab, then click the **JSON** toggle (top right) to see the raw configuration
3. Copy the entire JSON configuration

[SCREENSHOT: JSON config view with copy button]

4. Return to your fragment
5. Paste the configuration into the fragment editor
6. Click **Save**

[SCREENSHOT: Fragment editor with pasted configuration]

Your fragment now contains everything: the camera, filtered camera, ML model service, vision service, data capture settings, and trigger configuration. Any machine with this fragment applied will have this exact setup.

> **Fragments are powerful.** When you update a fragment, every machine using it receives the update automatically. Change a detection threshold once, and 100 stations update. This is how you manage configuration at scale.

#### 3.2 Add a Second Machine

Let's spin up a second inspection station and apply the fragment.

**Launch a second simulation:**

Click the button below to launch a second work cell:

[BUTTON: Launch Second Station]

This opens another browser tab with an identical simulation environment—conveyor, camera, the works. But this machine doesn't have any Viam configuration yet.

[SCREENSHOT: Second simulation tab]

**Create the machine and install viam-server:**

Follow the same steps from Part 1:

1. In the Viam app, click **+ Add machine**
2. Name it `inspection-station-2`
3. Copy the install command from the **Setup** tab
4. Paste and run it in the second simulation's terminal
5. Wait for the machine to come online

**Apply the fragment:**

Instead of manually configuring everything, you'll apply your fragment.

1. On `inspection-station-2`, go to the **Config** tab
2. Click **+ Add fragment**
3. Select `inspection-station` from the dropdown
4. Click **Add**
5. Click **Save config**

[SCREENSHOT: Adding fragment to machine]

Within seconds, the machine reloads its configuration. It now has the camera, vision service, data capture, and alerting—all from the fragment.

**Verify it works:**

1. Go to the **Control** tab
2. Check the camera feed
3. Run a detection

Both stations are now running identical inspection logic.

[SCREENSHOT: Fleet view showing both machines online]

**Checkpoint:** Two stations running identical inspection logic. You didn't copy-paste configuration—you used a fragment.

---

### Part 5: Fleet (~10 min)

**Goal:** Manage both stations as a fleet.

**Skills:** Fleet monitoring, pushing updates.

#### 5.1 View Your Fleet

With multiple machines running, you need a way to monitor them together—not clicking through each one individually.

**Open the fleet view:**

1. In the Viam app, click **Fleet** in the left sidebar (or **Machines** in some views)
2. You'll see a list of all machines in your organization

[SCREENSHOT: Fleet view showing both inspection stations]

The fleet view shows:
- **Status:** Online/offline for each machine
- **Last seen:** When each machine last connected
- **Location:** If you've tagged machines by location

**Check machine health:**

Click on either machine to see its details:
- Component status (is the camera responding?)
- Recent logs
- Resource usage (CPU, memory)

[SCREENSHOT: Machine detail view with status indicators]

**View aggregated data:**

1. Click the **Data** tab at the organization level
2. You'll see data from *all* machines combined
3. Filter by machine, time range, or data type

You can query: "How many FAIL detections across all stations in the last hour?" This is the foundation for dashboards and analytics.

[SCREENSHOT: Data tab showing aggregated events from both machines]

> **Two machines or two hundred:** This same view works regardless of fleet size. As you add machines, they appear here automatically. The fleet view is your single pane of glass for operations.

#### 5.2 Push a Configuration Update

One of the most powerful aspects of fragments is pushing updates. Let's change a setting and watch it propagate.

**Modify the fragment:**

Suppose you want to adjust the confidence threshold for failure alerts. Instead of alerting at 70% confidence, you want 80% to reduce false positives.

1. Go to **Fragments** in the left sidebar
2. Open your `inspection-station` fragment
3. Find the `fail-detector-cam` (filtered camera) configuration
4. Change `confidence_threshold` from `0.7` to `0.8`
5. Click **Save**

[SCREENSHOT: Editing fragment configuration]

**Watch the update propagate:**

1. Go back to the **Fleet** view
2. Watch both machines briefly show as "Configuring" or "Restarting"
3. Within 30 seconds, both machines are running the updated configuration

[SCREENSHOT: Machines showing configuration update in progress]

You didn't SSH into either machine. You didn't run any deployment commands. You changed the fragment, and Viam pushed the update automatically.

**Verify the change:**

1. Click into `inspection-station-1`
2. Go to **Config** tab and check the filtered camera
3. Confirm the confidence threshold is now 0.8

[SCREENSHOT: Updated confidence threshold in config]

> **This is fleet management.** Need to update an ML model across 50 machines? Update the fragment. Need to roll back a bad change? Revert the fragment. The machines sync automatically. This same pattern scales from 2 machines to 2,000.

**Checkpoint:** You can manage multiple machines from one place. Configuration changes propagate automatically.

---

### Part 6: Maintain (~10 min)

**Goal:** Debug and fix an issue.

**Skills:** Remote diagnostics, log analysis, incident response.

#### 6.1 Simulate a Problem

In production, things break. Cameras get dirty, cables loosen, lighting changes. Let's simulate a problem and practice debugging.

**Trigger the issue:**

Click the button below to simulate camera degradation on `inspection-station-1`:

[BUTTON: Degrade Camera]

This simulates what happens when a camera lens gets dirty or lighting conditions change—the image becomes noisy and blurry, making ML detection unreliable.

[SCREENSHOT: Simulation showing degraded camera view]

**Notice the anomaly:**

Within a few seconds, you should see signs of trouble:

1. **Data:** Detection results become inconsistent—lower confidence scores, missed detections
2. **Alerts:** You might receive unexpected alerts (or stop receiving expected ones)
3. **Logs:** Error messages or warnings from the vision service

In a real deployment, this is how you'd first learn about a problem—through monitoring data and alerts, not a phone call from the factory floor.

#### 6.2 Diagnose Remotely

Now let's investigate without physical access to the machine.

**Check the logs:**

1. In the Viam app, go to `inspection-station-1`
2. Click the **Logs** tab
3. Look for error messages or unusual output

[SCREENSHOT: Logs showing detection anomalies]

You might see:
- Lower confidence scores than usual
- Failed detections (no objects found when there should be)
- Timeout errors if the camera is struggling

**View the camera feed:**

1. Go to the **Control** tab
2. Open the `inspection-cam` stream
3. Look at the image quality

[SCREENSHOT: Degraded camera feed in Control tab]

The issue is immediately visible: the camera feed is noisy or blurred. You've identified the root cause without leaving your desk.

**Compare to the healthy station:**

1. Open `inspection-station-2` in another tab
2. View its camera feed
3. Confirm the image quality is normal

This comparison confirms the problem is isolated to station 1, not a systemic issue.

> **Remote diagnostics in practice:** You just debugged a hardware issue without physical access. In a real deployment, the machine could be in another building, another city, or another country. Viam gives you the same visibility regardless of location.

#### 6.3 Fix and Verify

Let's fix the issue and confirm the system recovers.

**Reset the camera:**

In a real scenario, you'd dispatch maintenance to clean or replace the camera. For this simulation, click the reset button:

[BUTTON: Reset Camera]

This restores the camera to normal operation.

**Verify the fix:**

1. Go back to `inspection-station-1`
2. Check the **Control** tab—the camera feed should be clear
3. Check the **Logs** tab—detection should be working normally
4. Wait for a few inspection cycles to confirm consistent results

[SCREENSHOT: Restored camera feed and normal logs]

**Document the incident:**

In production, you'd want to track this:
- When the issue started
- How it was detected
- What caused it
- How it was resolved

The data captured during the incident (the anomalous detections, the degraded images) is already in Viam's data service—you can query it later for incident reports or trend analysis.

**Checkpoint:** You've diagnosed and fixed a production issue remotely.

---

### Part 7: Productize (~15 min)

**Goal:** Build a customer-facing product.

**Skills:** Building apps with Viam SDKs, white-label deployment.

#### 7.1 Create a Customer Dashboard

You've built a working system—but right now, only you can see it through the Viam app. Your customers need their own interface, with your branding, showing only what they need to see.

Viam's SDKs let you build custom applications that connect to machines and query data. Let's create a simple dashboard that shows inspection results.

**Set up a TypeScript project:**

```bash
mkdir inspection-dashboard && cd inspection-dashboard
npm init -y
npm install @viamrobotics/sdk
```

**Create the dashboard:**

Create a file called `dashboard.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Inspection Dashboard</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .stats { display: flex; gap: 20px; margin: 20px 0; }
        .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; flex: 1; }
        .stat-value { font-size: 48px; font-weight: bold; }
        .pass { color: #22c55e; }
        .fail { color: #ef4444; }
        .station { background: #fff; border: 1px solid #e5e5e5; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .online { color: #22c55e; }
        .offline { color: #ef4444; }
    </style>
</head>
<body>
    <h1>Quality Inspection Dashboard</h1>

    <div class="stats">
        <div class="stat-card">
            <div>Today's Inspections</div>
            <div class="stat-value" id="total-count">--</div>
        </div>
        <div class="stat-card">
            <div>Pass Rate</div>
            <div class="stat-value pass" id="pass-rate">--%</div>
        </div>
        <div class="stat-card">
            <div>Failures</div>
            <div class="stat-value fail" id="fail-count">--</div>
        </div>
    </div>

    <h2>Stations</h2>
    <div id="stations"></div>

    <script type="module">
        import { createRobotClient, DataClient } from '@viamrobotics/sdk';

        // Replace with your credentials
        const API_KEY = 'YOUR_API_KEY';
        const API_KEY_ID = 'YOUR_API_KEY_ID';

        async function updateDashboard() {
            // Connect to Viam's data service
            const dataClient = await DataClient.createFromCredentials(
                API_KEY_ID,
                API_KEY
            );

            // Query detection results from the last 24 hours
            const results = await dataClient.tabularDataByFilter({
                filter: {
                    componentName: 'part-detector',
                    interval: {
                        start: new Date(Date.now() - 24 * 60 * 60 * 1000),
                        end: new Date()
                    }
                }
            });

            // Calculate stats
            const total = results.length;
            const fails = results.filter(r =>
                r.data.detections?.some(d => d.class_name === 'FAIL')
            ).length;
            const passRate = total > 0 ? ((total - fails) / total * 100).toFixed(1) : 0;

            // Update UI
            document.getElementById('total-count').textContent = total;
            document.getElementById('fail-count').textContent = fails;
            document.getElementById('pass-rate').textContent = `${passRate}%`;
        }

        // Update every 5 seconds
        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
```

**Run the dashboard:**

Open `dashboard.html` in your browser (or serve it with a local web server). You'll see live inspection statistics pulled from Viam's data service.

[SCREENSHOT: Customer dashboard showing inspection stats]

> **This is your product.** The dashboard has no Viam branding—it's your interface, powered by Viam's APIs. You can add your logo, customize the design, add features. The same APIs that power this simple page can power a full React application, a mobile app, or an enterprise dashboard.

#### 7.2 Set Up White-Label Auth

Your customers shouldn't log into Viam—they should log into *your* product. Viam supports white-label authentication so you can use your own identity provider.

**Configure custom authentication:**

1. In the Viam app, go to **Organization Settings**
2. Find the **Custom Authentication** section
3. Configure your identity provider (OAuth/OIDC)

[SCREENSHOT: Custom auth configuration]

With this configured:
- Your customers log in through your login page
- They see only the machines you've given them access to
- Your branding, your domain, your experience

> **Note:** Full OAuth configuration is beyond the scope of this tutorial. See the [Authentication documentation](../reference/authentication.md) for detailed setup instructions.

**Create customer accounts:**

You can also create customer accounts directly:

1. Go to **Organization Settings** → **Members**
2. Invite your customer with limited permissions
3. They see only their machines, not your entire fleet

This lets you ship a product where each customer sees only their own inspection stations.

#### 7.3 (Optional) Configure Billing

If you're selling inspection-as-a-service, you need to bill customers. Viam can meter usage and integrate with your billing system.

**Usage metering:**

Viam tracks:
- Number of machines
- Data captured and stored
- API calls
- ML inference operations

You can query this data to build usage-based billing:

```typescript
// Example: Get machine usage for billing
const usage = await dataClient.getUsageByOrganization({
    organizationId: 'YOUR_ORG_ID',
    startTime: billingPeriodStart,
    endTime: billingPeriodEnd
});

// Calculate charges based on your pricing model
const machineCharges = usage.machineCount * PRICE_PER_MACHINE;
const dataCharges = usage.dataGB * PRICE_PER_GB;
```

**Billing integration:**

For production billing, you'd integrate Viam's usage data with your billing system (Stripe, your own invoicing, etc.). The data is available through APIs, so you have full flexibility in how you present and charge for usage.

> **Business model flexibility:** Charge per machine, per inspection, per GB of data, or a flat subscription. Viam provides the metering data; you decide the pricing.

**Checkpoint:** You have a customer-ready product. You've gone from prototype to shippable product in one tutorial.

---

## What's Next

### You Can Now Build

With the skills from this tutorial, you could build:

- **Inventory monitoring** — Camera watches shelves, alerts when stock is low
- **Security system** — Detect people or vehicles, log events, send alerts
- **Wildlife camera** — Classify animals, sync photos to cloud, monitor remotely
- **Equipment monitoring** — Watch gauges or indicator lights, alert on anomalies

These all use the same patterns: configure components, add services, write logic, deploy, scale with fragments.

### Continue Learning

**Try another tutorial:**
- [Mobile Base](./mobile-base.md) — Add navigation and movement
- [Arm + Vision](./arm-vision.md) — Add manipulation

**Go deeper with blocks:**
- [Track Objects Across Frames](../build/perception/track-objects.md) — Add persistence to detections
- [Capture and Sync Data](../build/foundation/capture-sync.md) — Build datasets from your cameras
- [Monitor Over Time](../build/stationary-vision/monitor-over-time.md) — Detect anomalies and trends

**Build your own project:**
- You have all the foundational skills
- Pick hardware (or stay in simulation)
- Use the blocks as reference when you get stuck

---

## Simulation Requirements

### Work Cell Elements

| Element | Description |
|---------|-------------|
| Conveyor/staging area | Surface where parts appear |
| Camera | Overhead RGB camera (640x480, 30fps) |
| Sample parts | Mix of "good" and "defective" items |
| Lighting | Consistent industrial lighting |

### Viam Components

| Component | Type | Notes |
|-----------|------|-------|
| `inspection-cam` | camera | Gazebo RGB camera |
| `part-detector` | vision | ML model service |
| `fail-detector-cam` | camera (filtered) | Captures only FAIL detections |
| `fail-alert` | trigger | Email notification on failures |

### Simulated Events

| Event | Trigger | Purpose |
|-------|---------|---------|
| Part appears | Timer or user action | New item to inspect |
| Camera degradation | Part 5 trigger | Create debugging scenario |

---

## Blocks Used

From [block-definitions.md](../planning/block-definitions.md):

**Foundation:**
- Connect to Cloud
- Add a Camera
- Capture and Sync Data
- Start Writing Code

**Perception:**
- Add Computer Vision
- Detect Objects (2D)

**Stationary Vision:**
- Trigger on Detection
- Inspect for Defects

**Fleet/Deployment:**
- Configure Multiple Machines
- Monitor a Fleet
- Push Updates

**Productize:**
- Build a Customer Dashboard (TypeScript SDK)
- Set Up White-Label Auth
- Configure Billing

---

## Author Guidance

### UI Rough Edges to Address

Document and provide explicit guidance for:

- [ ] Account creation flow
- [ ] Finding the camera panel in the app
- [ ] Vision service configuration steps
- [ ] Data capture configuration UI
- [ ] Trigger configuration UI
- [ ] Fragment creation UI
- [ ] Fleet view navigation

### Key Teaching Moments

At each step, explicitly connect to transferable skills:

- "This is how you configure *any* component"
- "This pattern works for *any* sensor"
- "You'd do the same thing with a robot arm"

### Anti-Patterns to Avoid

- Don't let users think Viam is "just for cameras"
- Don't let steps feel like magic—explain what's happening
- Don't assume users will read linked docs—include essential context inline

---

## Open Questions

1. **Part appearance:** Timer vs. manual trigger? Timer feels realistic; manual gives control.

2. **ML model:** Pre-trained (provided) vs. walk through training? Pre-trained keeps focus on platform skills.

3. ~~**Alert mechanism:** What works without user setup?~~ **Resolved:** Using filtered camera + trigger with email notification.

4. **Second station:** Identical or slightly different? Identical is simpler; different shows fragment flexibility.

5. **Dashboard complexity:** How much web dev do we include? Keep minimal—point is Viam APIs, not teaching React.

6. **Mobile app control:** Consider introducing mobile SDK / remote control from phone somewhere in the tutorials. Could demonstrate controlling machines from anywhere.
