# Stationary Vision Tutorial

**Status:** 🟡 Draft

**Time:** ~1.25 hours
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

## Tutorial Outline

| Part | Time | What You'll Do |
|------|------|----------------|
| [Part 1: Vision Pipeline](#part-1-vision-pipeline-15-min) | ~15 min | Set up camera, ML model, and vision service |
| [Part 2: Data Capture](#part-2-data-capture-15-min) | ~15 min | Configure automatic data sync and alerts |
| [Part 3: Control Logic](#part-3-control-logic-30-min) | ~30 min | Write inspection module, deploy to machine |
| [Part 4: Scale](#part-4-scale-10-min) | ~10 min | Create fragment, add second machine |
| [Part 5: Productize](#part-5-productize-15-min) | ~15 min | Build dashboard, white-label auth |

<details>
<summary><strong>Full Section Outline</strong></summary>

**[Part 1: Vision Pipeline](#part-1-vision-pipeline-15-min)** (~15 min)
- [1.1 Launch the Simulation](#11-launch-the-simulation)
- [1.2 Create a Machine in Viam](#12-create-a-machine-in-viam)
- [1.3 Install viam-server](#13-install-viam-server)
- [1.4 Configure the Camera](#14-configure-the-camera)
- [1.5 Test the Camera](#15-test-the-camera)
- [1.6 Add a Vision Service](#16-add-a-vision-service)

**[Part 2: Data Capture](#part-2-data-capture-15-min)** (~15 min)
- [2.1 Configure Data Capture](#21-configure-data-capture)
- [2.2 Add Machine Health Alert](#22-add-machine-health-alert)
- [2.3 View and Query Data](#23-view-and-query-data)
- [2.4 Summary](#24-summary)

**[Part 3: Control Logic](#part-3-control-logic-30-min)** (~30 min)
- [3.1 Set Up Your Project](#31-set-up-your-project)
- [3.2 Build the Inspector](#32-build-the-inspector)
- [3.3 Write the Development CLI](#33-write-the-development-cli)
- [3.4 Test Your First Command](#34-test-your-first-command)
- [3.5 Configure the Rejector](#35-configure-the-rejector)
- [3.6 Add Rejection Logic](#36-add-rejection-logic)
- [3.7 Test the Complete Loop](#37-test-the-complete-loop)
- [3.8 Deploy as a Module](#38-deploy-as-a-module)
- [3.9 Summary](#39-summary)

**[Part 4: Scale](#part-4-scale-10-min)** (~10 min)
- [4.1 Create a Fragment](#41-create-a-fragment)
- [4.2 Parameterize Machine-Specific Values](#42-parameterize-machine-specific-values)
- [4.3 Add a Second Machine](#43-add-a-second-machine)
- [4.4 Fleet Management Capabilities](#44-fleet-management-capabilities)

**[Part 5: Productize](#part-5-productize-15-min)** (~15 min)
- [5.1 Create a Dashboard](#51-create-a-dashboard)
- [5.2 Set Up White-Label Auth](#52-set-up-white-label-auth)
- [5.3 (Optional) Configure Billing](#53-optional-configure-billing)

</details>

---

## Tutorial Flow

### Part 1: Vision Pipeline (~15 min)

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

**Checkpoint:** You've configured a complete ML inference pipeline—camera, model, and vision service—entirely through the Viam app. The system can detect defects. Next, you'll set up continuous data capture so every detection is recorded and queryable.

---

### Part 2: Data Capture (~15 min)

**Goal:** Enable continuous recording and monitoring so every detection is captured, queryable, and you're alerted to problems.

**Skills:** Data capture configuration, triggers and alerts, querying captured data.

Your vision pipeline is running. Before writing custom code, set up the data infrastructure—continuous capture, cloud sync, and alerting. This runs automatically in the background, recording every detection for compliance, analytics, and model improvement.

Viam's data capture is built-in. Toggle it on, and every detection result and image gets stored locally, synced to the cloud, and made queryable—automatically.

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

1. In the config, find `part-detector` and click **Test** at the bottom of its card
2. You should see a capture indicator showing data is being recorded

The machine is now capturing detection results and images every 2 seconds—whether or not you're connected.

#### 2.2 Add Machine Health Alert

Get notified if your inspection station goes offline. This is a simple trigger—no code required.

**Create the trigger:**

1. In the Viam app, go to your machine's **Configure** tab
2. Click **+** next to your machine in the left sidebar
3. Select **Trigger**
4. Name it `offline-alert`
5. Click **Create**

**Configure the trigger:**

1. For **Type**, select `Part is offline`
2. Toggle **Email all machine owners** to on (or add specific email addresses)
3. Set **Minutes between notifications** to `5` (so you don't get spammed)
4. Click **Save config**

[SCREENSHOT: Offline trigger configuration]

That's it. If your inspection station loses connection for any reason—network issues, power loss, viam-server crash—you'll get an email.

> **Other triggers:** You can also create triggers for "Part is online" (useful for knowing when a machine comes back) or "Data synced" (fires when data reaches the cloud). For detection-based alerts, see Part 5.

#### 2.3 View and Query Data

Viam automatically syncs captured data to the cloud and removes it from the machine to free up storage. No additional configuration required.

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

**Filter the data:**

1. Click **Filter** and select your machine: `inspection-station-1`
2. Set time range to "Last hour"
3. You can also filter by component to see only vision service results or only camera images

[SCREENSHOT: Data tab with filters applied]

**Query with SQL or MQL:**

For more complex queries, use the **Query** page:

1. In the Viam app, click **Data** then **Query**
2. Select **SQL** or **MQL** as your query language
3. Try a simple query to find all failures:

```sql
SELECT time_received, data
FROM readings
WHERE component_name = 'part-detector'
  AND data LIKE '%FAIL%'
ORDER BY time_received DESC
LIMIT 10
```

[SCREENSHOT: Query page with results]

This is powerful for incident investigation: "Show me all FAIL detections from the last hour" or "How many parts failed on Tuesday's shift?"

This data serves multiple purposes:
- **Compliance** — Auditable record of every inspection
- **Quality trends** — "FAIL rate increased 20% this week"
- **Model improvement** — Export images to retrain your ML model
- **Incident review** — "Show me all FAILs from Tuesday's shift"

#### 2.4 Summary

Data capture is now running in the background:
- Captures every detection and camera image
- Syncs to cloud automatically
- Queryable for analytics and compliance
- Alerts you when the machine goes offline

This foundation records everything your vision pipeline sees. In Part 3, you'll write custom control logic to act on detections.

**Checkpoint:** Your system records every detection automatically. Data syncs to the cloud where you can query it and build dashboards.

---

### Part 3: Control Logic (~30 min)

**Goal:** Write inspection logic that detects defects and rejects them, then deploy it as a module.

**Skills:** Module-first development, Viam SDK, adding actuators, module deployment.

Your vision pipeline detects defects and records the results. Now you'll write code to act on those detections—rejecting defective parts automatically.

You'll use the **module-first development pattern**: code that runs on your laptop during development, connecting to remote hardware over the network. When it works, you package it as a module and deploy it to the machine. Same code, different context.

#### 3.1 Set Up Your Project

Create a project with two files: your service logic and a CLI to test it.

{{< tabs >}}
{{% tab name="Go" %}}

```bash
mkdir inspection-module && cd inspection-module
go mod init inspection-module
go get go.viam.com/rdk
go get github.com/erh/vmodutils
mkdir -p cmd/cli cmd/module
```

Create this structure:

```
inspection-module/
├── cmd/
│   ├── cli/main.go        # Development CLI
│   └── module/main.go     # Production entry point (added later)
├── inspector.go           # Your service logic
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

Your service logic lives in one file; the CLI imports it. During development, the CLI runs on your laptop and connects to the remote machine. You iterate locally without deploying anything.

#### 3.2 Build the Inspector

You'll build the inspector iteratively, testing each change against real hardware. Start with the simplest operation—grab an image from the camera.

{{< tabs >}}
{{% tab name="Go" %}}

Create `inspector.go`:

```go
package inspector

import (
	"context"
	"fmt"
	"image/jpeg"
	"os"

	"github.com/mitchellh/mapstructure"
	"go.viam.com/rdk/components/camera"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/generic"
	"go.viam.com/rdk/services/vision"
)

// Config declares which dependencies the inspector needs.
type Config struct {
	Camera        string `json:"camera"`
	VisionService string `json:"vision_service"`
}

// Validate checks the config and returns dependency names.
// Returns (required deps, optional deps, error).
func (cfg *Config) Validate(path string) ([]string, []string, error) {
	if cfg.Camera == "" {
		return nil, nil, fmt.Errorf("camera is required")
	}
	if cfg.VisionService == "" {
		return nil, nil, fmt.Errorf("vision_service is required")
	}
	return []string{cfg.Camera, cfg.VisionService}, nil, nil
}

// Inspector implements resource.Resource.
type Inspector struct {
	resource.AlwaysRebuild

	name   resource.Name
	conf   *Config
	logger logging.Logger

	cam      camera.Camera
	detector vision.Service
}

// NewInspector is the exported constructor called by both CLI and module.
func NewInspector(
	ctx context.Context,
	deps resource.Dependencies,
	name resource.Name,
	conf *Config,
	logger logging.Logger,
) (resource.Resource, error) {
	cam, err := camera.FromDependencies(deps, conf.Camera)
	if err != nil {
		return nil, err
	}
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, err
	}

	return &Inspector{
		name:     name,
		conf:     conf,
		logger:   logger,
		cam:      cam,
		detector: detector,
	}, nil
}

func (i *Inspector) Name() resource.Name {
	return i.name
}

// Command struct for DoCommand parsing.
type inspectorCmd struct {
	Capture bool
}

func (i *Inspector) DoCommand(ctx context.Context, cmdMap map[string]interface{}) (map[string]interface{}, error) {
	var cmd inspectorCmd
	if err := mapstructure.Decode(cmdMap, &cmd); err != nil {
		return nil, err
	}

	if cmd.Capture {
		if err := i.captureImage(ctx); err != nil {
			return nil, err
		}
		return map[string]interface{}{"saved": "snapshot.jpg"}, nil
	}

	return nil, fmt.Errorf("unknown command: %v", cmdMap)
}

func (i *Inspector) Close(ctx context.Context) error {
	return nil
}

func (i *Inspector) captureImage(ctx context.Context) error {
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

{{% /tab %}}
{{% tab name="Python" %}}

Create `inspector.py`:

```python
from dataclasses import dataclass
from typing import Any, Mapping
from viam.components.camera import Camera
from viam.services.vision import VisionClient

@dataclass
class Config:
    camera: str
    vision_service: str

    def validate(self) -> list[str]:
        """Check config and return dependency names."""
        if not self.camera:
            raise ValueError("camera is required")
        if not self.vision_service:
            raise ValueError("vision_service is required")
        return [self.camera, self.vision_service]

class Inspector:
    """Inspector implements the generic service interface."""

    def __init__(self, name: str, conf: Config, cam: Camera, detector: VisionClient):
        self.name = name
        self.conf = conf
        self.cam = cam
        self.detector = detector

    @classmethod
    async def new(cls, deps: dict, cfg: Config) -> "Inspector":
        """Create an inspector by extracting dependencies from the map."""
        cam = next((v for k, v in deps.items() if k.name == cfg.camera), None)
        detector = next((v for k, v in deps.items() if k.name == cfg.vision_service), None)
        return cls("inspector", cfg, cam, detector)

    async def do_command(self, command: Mapping[str, Any]) -> Mapping[str, Any]:
        """Generic service interface. All commands go through here."""
        if command.get("capture"):
            await self._capture_image()
            return {"saved": "snapshot.jpg"}
        raise ValueError(f"unknown command: {command}")

    async def close(self) -> None:
        pass

    async def _capture_image(self) -> None:
        img = await self.cam.get_image()
        img.save("snapshot.jpg")
```

{{% /tab %}}
{{< /tabs >}}

**Fetch dependencies:**

```bash
go mod tidy
```

#### 3.3 Write the Development CLI

Now create the CLI that imports and tests your inspector. The CLI connects to your remote machine and converts its resources to a Dependencies map—the same format the module system uses in production.

{{< tabs >}}
{{% tab name="Go" %}}

Create `cmd/cli/main.go`:

```go
package main

import (
	"context"
	"flag"
	"fmt"

	"github.com/erh/vmodutils"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/services/generic"

	inspector "inspection-module"
)

func main() {
	err := realMain()
	if err != nil {
		panic(err)
	}
}

func realMain() error {
	ctx := context.Background()
	logger := logging.NewLogger("cli")

	host := flag.String("host", "", "Machine address")
	cmd := flag.String("cmd", "", "Command: capture, detect, inspect")
	flag.Parse()

	if *host == "" {
		return fmt.Errorf("need -host flag")
	}
	if *cmd == "" {
		return fmt.Errorf("need -cmd flag")
	}

	// 1. Config with hardcoded dependency names
	cfg := inspector.Config{
		Camera:        "inspection-cam",
		VisionService: "part-detector",
	}

	// 2. Validate the config
	_, _, err := cfg.Validate("")
	if err != nil {
		return err
	}

	// 3. Connect using vmodutils
	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return err
	}
	defer machine.Close(ctx)

	// 4. Get dependencies using vmodutils
	deps, err := vmodutils.MachineToDependencies(machine)
	if err != nil {
		return err
	}

	// 5. Create service using exported constructor
	svc, err := inspector.NewInspector(ctx, deps, generic.Named("inspector"), &cfg, logger)
	if err != nil {
		return err
	}
	defer svc.Close(ctx)

	// 6. Call DoCommand with the command from -cmd flag
	result, err := svc.DoCommand(ctx, map[string]interface{}{*cmd: true})
	if err != nil {
		return err
	}
	logger.Infof("Result: %v", result)
	return nil
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
    if len(sys.argv) < 3:
        print("Usage: python cli.py HOST COMMAND")
        print("Commands: capture, detect, inspect")
        return

    host = sys.argv[1]
    cmd = sys.argv[2]

    # 1. Config with hardcoded dependency names
    cfg = Config(
        camera="inspection-cam",
        vision_service="part-detector"
    )

    # 2. Validate the config
    cfg.validate()

    # 3. Connect to the remote machine
    robot = await RobotClient.at_address(host)

    # 4. Get dependencies
    deps = {}
    for name in robot.resource_names:
        try:
            deps[name] = robot.get_component(name)
        except:
            try:
                deps[name] = robot.get_service(name)
            except:
                pass

    # 5. Create service using exported constructor
    inspector = await Inspector.new(deps, cfg)

    # 6. Call do_command with the command from CLI args
    result = await inspector.do_command({cmd: True})
    print(f"Result: {result}")

    await inspector.close()
    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
```

{{% /tab %}}
{{< /tabs >}}

The CLI uses `{*cmd: true}` to pass whatever command you specify via `-cmd` flag. This means the same CLI works for `capture`, `detect`, and `inspect`—you don't need to modify it as you add commands to the inspector.

**Authenticate the CLI:**

The Go CLI uses your Viam CLI token for authentication. Make sure you're logged in:

```bash
viam login
```

This stores a token that `vmodutils.ConnectToHostFromCLIToken` uses automatically.

**Get your machine address:**

1. In the Viam app, go to your machine's page
2. Click the **Code sample** tab
3. Copy the machine address (looks like `your-machine-main.abc123.viam.cloud`)

[SCREENSHOT: Code sample tab showing machine address]

#### 3.4 Test Your First Command

**Test it:**

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd capture
# or: python cli.py your-machine-main.abc123.viam.cloud capture
```

```
Result: map[saved:snapshot.jpg]
```

Open `snapshot.jpg`—you should see the current view from your inspection camera. This image was captured on the remote machine and transferred to your laptop.

##### Iteration 2: Run detection

Add the detect command. You need to:
1. Add `Detect bool` to the command struct
2. Add a handler for `cmd.Detect` in `DoCommand`
3. Add the new `detect()` method

{{< tabs >}}
{{% tab name="Go" %}}

Update `inspector.go`—replace the command struct and `DoCommand`, then add the `detect()` method:

```go
// Command struct for DoCommand parsing.
type inspectorCmd struct {
	Capture bool
	Detect  bool
}

func (i *Inspector) DoCommand(ctx context.Context, cmdMap map[string]interface{}) (map[string]interface{}, error) {
	var cmd inspectorCmd
	if err := mapstructure.Decode(cmdMap, &cmd); err != nil {
		return nil, err
	}

	if cmd.Capture {
		if err := i.captureImage(ctx); err != nil {
			return nil, err
		}
		return map[string]interface{}{"saved": "snapshot.jpg"}, nil
	}

	if cmd.Detect {
		label, confidence, err := i.detect(ctx)
		if err != nil {
			return nil, err
		}
		return map[string]interface{}{"label": label, "confidence": confidence}, nil
	}

	return nil, fmt.Errorf("unknown command: %v", cmdMap)
}

func (i *Inspector) detect(ctx context.Context) (string, float64, error) {
	detections, err := i.detector.DetectionsFromCamera(ctx, i.conf.Camera, nil)
	if err != nil {
		return "", 0, err
	}

	if len(detections) == 0 {
		return "NO_DETECTION", 0, nil
	}

	best := detections[0]
	for _, d := range detections[1:] {
		if d.Score() > best.Score() {
			best = d
		}
	}

	return best.Label(), best.Score(), nil
}
```

{{% /tab %}}
{{% tab name="Python" %}}

Update `inspector.py`—replace `do_command` and add the `_detect` method:

```python
async def do_command(self, command: Mapping[str, Any]) -> Mapping[str, Any]:
    if command.get("capture"):
        await self._capture_image()
        return {"saved": "snapshot.jpg"}

    if command.get("detect"):
        label, confidence = await self._detect()
        return {"label": label, "confidence": confidence}

    raise ValueError(f"unknown command: {command}")

async def _detect(self) -> tuple[str, float]:
    detections = await self.detector.get_detections_from_camera(self.conf.camera)

    if not detections:
        return "NO_DETECTION", 0.0

    best = max(detections, key=lambda d: d.confidence)
    return best.class_name, best.confidence
```

{{% /tab %}}
{{< /tabs >}}

**Test it:**

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd detect
# or: python cli.py your-machine-main.abc123.viam.cloud detect
```

```
Result: map[confidence:0.942 label:PASS]
```

You're now running ML inference on the remote machine from your laptop.

#### 3.5 Configure the Rejector

Your inspector can detect defects. Now add hardware to act on them.

**Add the reject mechanism to your work cell:**

Click the button below to add a part rejector to your simulation:

[BUTTON: Add Reject Mechanism]

The simulation now shows a pneumatic pusher mounted beside the conveyor. When activated, it pushes parts into a reject bin.

[SCREENSHOT: Work cell with reject mechanism visible]

**Configure it in Viam:**

1. In the Viam app, go to your machine's **Configure** tab
2. Click **+** next to your machine in the left sidebar
3. Select **Component**, then **motor**
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

**Test it:**

1. Find the `rejector` motor in your config
2. Click **Test** at the bottom of its configuration card
3. Click **Run** to activate it briefly
4. Watch the simulation—the pusher should extend and retract

[SCREENSHOT: Motor test panel with Run button]

**Update your code to use the rejector:**

Now add the rejector as a dependency. Same pattern: add to Config, update Validate, add to struct, extract in constructor.

{{< tabs >}}
{{% tab name="Go" %}}

Update `inspector.go`:

```go
import (
	// ... existing imports ...
	"go.viam.com/rdk/components/motor"
)

type Config struct {
	Camera        string `json:"camera"`
	VisionService string `json:"vision_service"`
	Rejector      string `json:"rejector"`
}

func (cfg *Config) Validate(path string) ([]string, []string, error) {
	if cfg.Camera == "" {
		return nil, nil, fmt.Errorf("camera is required")
	}
	if cfg.VisionService == "" {
		return nil, nil, fmt.Errorf("vision_service is required")
	}
	if cfg.Rejector == "" {
		return nil, nil, fmt.Errorf("rejector is required")
	}
	return []string{cfg.Camera, cfg.VisionService, cfg.Rejector}, nil, nil
}

type Inspector struct {
	resource.AlwaysRebuild

	name   resource.Name
	conf   *Config
	logger logging.Logger

	cam      camera.Camera
	detector vision.Service
	rejector motor.Motor
}

func NewInspector(
	ctx context.Context,
	deps resource.Dependencies,
	name resource.Name,
	conf *Config,
	logger logging.Logger,
) (resource.Resource, error) {
	cam, err := camera.FromDependencies(deps, conf.Camera)
	if err != nil {
		return nil, err
	}
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, err
	}
	rejector, err := motor.FromDependencies(deps, conf.Rejector)
	if err != nil {
		return nil, err
	}

	return &Inspector{
		name:     name,
		conf:     conf,
		logger:   logger,
		cam:      cam,
		detector: detector,
		rejector: rejector,
	}, nil
}
```

Update the config in `cmd/cli/main.go`:

```go
cfg := inspector.Config{
	Camera:        "inspection-cam",
	VisionService: "part-detector",
	Rejector:      "rejector",
}
```

{{% /tab %}}
{{% tab name="Python" %}}

Update `inspector.py`:

```python
from viam.components.motor import Motor

@dataclass
class Config:
    camera: str
    vision_service: str
    rejector: str

    def validate(self) -> list[str]:
        if not self.camera:
            raise ValueError("camera is required")
        if not self.vision_service:
            raise ValueError("vision_service is required")
        if not self.rejector:
            raise ValueError("rejector is required")
        return [self.camera, self.vision_service, self.rejector]

class Inspector:
    def __init__(self, name: str, conf: Config, cam: Camera, detector: VisionClient, rejector: Motor):
        self.name = name
        self.conf = conf
        self.cam = cam
        self.detector = detector
        self.rejector = rejector

    @classmethod
    async def new(cls, deps: dict, cfg: Config) -> "Inspector":
        cam = next((v for k, v in deps.items() if k.name == cfg.camera), None)
        detector = next((v for k, v in deps.items() if k.name == cfg.vision_service), None)
        rejector = next((v for k, v in deps.items() if k.name == cfg.rejector), None)
        return cls("inspector", cfg, cam, detector, rejector)
```

Update the config in `cli.py`:

```python
cfg = Config(
    camera="inspection-cam",
    vision_service="part-detector",
    rejector="rejector"
)
```

{{% /tab %}}
{{< /tabs >}}

Run your code to verify it still works—it should connect successfully even though you're not using the rejector yet.

#### 3.6 Add Rejection Logic

Now add the `inspect` command. Update the command struct and add the internal methods.

{{< tabs >}}
{{% tab name="Go" %}}

Update `inspector.go`:

```go
type inspectorCmd struct {
	Capture bool
	Detect  bool
	Inspect bool
}

func (i *Inspector) DoCommand(ctx context.Context, cmdMap map[string]interface{}) (map[string]interface{}, error) {
	var cmd inspectorCmd
	if err := mapstructure.Decode(cmdMap, &cmd); err != nil {
		return nil, err
	}

	if cmd.Capture {
		if err := i.captureImage(ctx); err != nil {
			return nil, err
		}
		return map[string]interface{}{"saved": "snapshot.jpg"}, nil
	}

	if cmd.Detect {
		label, confidence, err := i.detect(ctx)
		if err != nil {
			return nil, err
		}
		return map[string]interface{}{"label": label, "confidence": confidence}, nil
	}

	if cmd.Inspect {
		label, confidence, rejected, err := i.inspect(ctx)
		if err != nil {
			return nil, err
		}
		return map[string]interface{}{
			"label":      label,
			"confidence": confidence,
			"rejected":   rejected,
		}, nil
	}

	return nil, fmt.Errorf("unknown command: %v", cmdMap)
}

func (i *Inspector) inspect(ctx context.Context) (string, float64, bool, error) {
	label, confidence, err := i.detect(ctx)
	if err != nil {
		return "", 0, false, err
	}

	shouldReject := label == "FAIL" && confidence > 0.7

	if shouldReject {
		if err := i.reject(ctx); err != nil {
			i.logger.Errorw("Failed to reject part", "error", err)
		}
	}

	return label, confidence, shouldReject, nil
}

func (i *Inspector) reject(ctx context.Context) error {
	if err := i.rejector.GoFor(ctx, 100, 1, nil); err != nil {
		return err
	}
	i.logger.Info("Part rejected")
	return nil
}
```

{{% /tab %}}
{{% tab name="Python" %}}

Update `inspector.py`:

```python
async def do_command(self, command: Mapping[str, Any]) -> Mapping[str, Any]:
    if command.get("capture"):
        await self._capture_image()
        return {"saved": "snapshot.jpg"}

    if command.get("detect"):
        label, confidence = await self._detect()
        return {"label": label, "confidence": confidence}

    if command.get("inspect"):
        label, confidence, rejected = await self._inspect()
        return {"label": label, "confidence": confidence, "rejected": rejected}

    raise ValueError(f"unknown command: {command}")

async def _inspect(self) -> tuple[str, float, bool]:
    label, confidence = await self._detect()
    should_reject = label == "FAIL" and confidence > 0.7

    if should_reject:
        try:
            await self._reject()
        except Exception as e:
            print(f"Failed to reject part: {e}")

    return label, confidence, should_reject

async def _reject(self) -> None:
    await self.rejector.go_for(rpm=100, revolutions=1)
    print("Part rejected")
```

{{% /tab %}}
{{< /tabs >}}

#### 3.7 Test the Complete Loop

Run your code and watch the simulation:

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd inspect
# or: python cli.py your-machine-main.abc123.viam.cloud inspect
```

With a passing part:
```
Result: map[confidence:0.942 label:PASS rejected:false]
```

With a failing part:
```
Result: map[confidence:0.873 label:FAIL rejected:true]
```

Watch the simulation—when a FAIL is detected, the rejector activates and pushes the part into the reject bin.

[SCREENSHOT: Simulation showing part being rejected]

**You've closed the control loop:**
1. **Sees** — Camera captures the part
2. **Thinks** — Vision service classifies it
3. **Acts** — Rejector removes defective parts

This is the complete sense-think-act cycle that defines robotic systems.

#### 3.8 Deploy as a Module

Your code works. Now package it as a module so it runs on the machine itself, not your laptop.

**Why deploy as a module?**

During development, your laptop runs the logic and talks to the machine over the network. This is great for iteration—edit, run, see results. But for production:
- The machine should run autonomously
- Network latency adds delay to the control loop
- Your laptop shouldn't need to be connected

Modules run directly on the machine as part of viam-server.

**Create the module entry point:**

{{< tabs >}}
{{% tab name="Go" %}}

Create `cmd/module/main.go`:

```go
package main

import (
	"go.viam.com/rdk/module"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/generic"

	inspector "inspection-module"
)

func main() {
	module.ModularMain(
		resource.APIModel{generic.API, inspector.Model},
	)
}
```

Add registration to `inspector.go` (at the top, before Config):

```go
var Model = resource.NewModel("your-org", "inspection", "inspector")

func init() {
	resource.RegisterService(generic.API, Model,
		resource.Registration[resource.Resource, *Config]{
			Constructor: newInspector,
		},
	)
}

// newInspector is the module constructor - extracts config and calls NewInspector.
func newInspector(
	ctx context.Context,
	deps resource.Dependencies,
	rawConf resource.Config,
	logger logging.Logger,
) (resource.Resource, error) {
	conf, err := resource.NativeConfig[*Config](rawConf)
	if err != nil {
		return nil, err
	}
	return NewInspector(ctx, deps, rawConf.ResourceName(), conf, logger)
}

// NewInspector is the exported constructor - called by both CLI and module.
func NewInspector(...) (resource.Resource, error) {
	// ... same as before ...
}
```

This matches the viam-chess pattern exactly:
- `init()` registers with a module constructor
- Module constructor (`newInspector`) extracts the config and calls the exported constructor
- Exported constructor (`NewInspector`) is used by both CLI and module

{{% /tab %}}
{{% tab name="Python" %}}

Create `main.py`:

```python
import asyncio
from viam.module.module import Module
from viam.services.generic import Generic

from inspector import Inspector

async def main():
    module = Module.from_args()
    module.add_model_from_registry(Generic.SUBTYPE, Inspector.MODEL)
    await module.start()

if __name__ == "__main__":
    asyncio.run(main())
```

Add registration to `inspector.py`:

```python
from viam.services.generic import Generic
from viam.resource.types import Model, ModelFamily

class Inspector(Generic):
    MODEL = Model(ModelFamily("your-org", "inspection"), "inspector")

    @classmethod
    async def new(cls, deps: dict, cfg: Config) -> "Inspector":
        """Called by both CLI and module system."""
        # ... same as before ...
```

{{% /tab %}}
{{< /tabs >}}

**Create `meta.json`:**

```json
{
  "module_id": "your-org:inspection-module",
  "visibility": "private",
  "url": "",
  "description": "Part inspection with automatic rejection",
  "models": [
    {
      "api": "rdk:service:generic",
      "model": "your-org:inspection:inspector"
    }
  ],
  "entrypoint": "bin/inspection-module"
}
```

**Build and package the module:**

```bash
# Build the binary
mkdir -p bin
go build -o bin/inspection-module cmd/module/main.go

# Create the upload tarball
tar czf module.tar.gz meta.json bin/
```

**Upload to the registry:**

```bash
viam module upload --version 1.0.0 --platform linux/amd64 module.tar.gz
```

> **Note:** Replace `your-org` in meta.json with your actual Viam organization namespace. You can find this in the Viam app under **Organization settings**.

**Add the module to your machine:**

1. In the Viam app, go to your machine's **Configure** tab
2. Click **+** next to your machine
3. Select **Service** and search for `inspection-module`
4. Select your module from the results (it will show as `your-org:inspection-module`)
5. Click **Add module**

This adds both the module and creates a service configuration card.

**Configure the inspector service:**

In the service card that was created:

1. Name it `inspector`
2. Expand the **Attributes** section and add the dependencies:

```json
{
  "camera": "inspection-cam",
  "vision_service": "part-detector",
  "rejector": "rejector"
}
```

3. Click **Save** in the top right

**Verify it's running:**

1. Check the **Logs** tab for your machine
2. You should see the inspector module starting up
3. Go to the simulation and trigger a defective part—watch the rejector activate

The machine now runs your inspection logic autonomously. The same code that ran on your laptop now runs on the machine as part of viam-server.

#### 3.9 Summary

In three iterations, you went from nothing to a working inspection system:

1. **Capture image** — Proved you can access remote hardware
2. **Run detection** — Added ML inference
3. **Inspect and reject** — Made a decision and acted on it

Each iteration was: edit → rebuild → run → see results. No deployment, no waiting. Your code ran on your laptop while the hardware ran on the machine.

Then you packaged and deployed the same code as a module. **Same constructor, same `DoCommand`, different context.** That's module-first development.

**The module-first pattern:**
- **Config** — One field per dependency (declares what you need)
- **Constructor** — Extract dependencies using `FromDependencies`, return `resource.Resource`
- **DoCommand** — The generic service interface; all operations go through here
- **CLI** — Creates your service locally, calls `DoCommand`, just like the module system does

When you need to add another sensor or actuator, it's the same pattern: add to config, extract in constructor, add a command to `DoCommand`.

**Checkpoint:** Your inspection system runs autonomously on the machine. It sees, thinks, and acts—the complete control loop.

---

### Part 4: Scale (~10 min)

**Goal:** Add a second inspection station.

**Skills:** Configuration reuse with fragments, fleet basics.

#### 4.1 Create a Fragment

You have one working inspection station. Now imagine you need 10 more—or 100. Manually copying configuration to each machine would be tedious and error-prone.

Viam solves this with *fragments*: reusable configuration blocks that can be applied to any machine. Think of a fragment as a template. Define your camera, vision service, data capture, and triggers once, then apply that template to as many machines as you need.

**Export your machine configuration:**

1. Go to your `inspection-station-1` machine
2. Click the **Configure** tab, then click **JSON** (top right) to see the raw configuration
3. Copy the entire JSON configuration to your clipboard

[SCREENSHOT: JSON config view with copy button]

**Create the fragment:**

1. In the Viam app, click **Fragments** in the left sidebar
2. Click **+ Create fragment**
3. Name it `inspection-station`
4. Paste your configuration into the fragment editor
5. Click **Save**

[SCREENSHOT: Fragment editor with pasted configuration]

#### 4.2 Parameterize Machine-Specific Values

Your fragment now contains everything—but some values are specific to each machine. The camera's `video_path` might be `/dev/video0` on one machine and `/dev/video1` on another. Hardcoding these values would break the fragment's reusability.

Viam fragments support *variables* for exactly this purpose.

**Find the camera configuration in your fragment:**

Look for the camera component in the JSON. It will look something like:

```json
{
  "name": "inspection-cam",
  "type": "camera",
  "model": "webcam",
  "attributes": {
    "video_path": "/dev/video0"
  }
}
```

**Replace the hardcoded value with a variable:**

Change `video_path` to use the `$variable` syntax:

```json
{
  "name": "inspection-cam",
  "type": "camera",
  "model": "webcam",
  "attributes": {
    "video_path": {
      "$variable": {
        "name": "camera_path"
      }
    }
  }
}
```

Click **Save** to update the fragment.

Now when you apply this fragment to a machine, you'll provide the actual `camera_path` value for that specific machine.

> **What to parameterize:** Device paths (`/dev/video0`, `/dev/ttyUSB0`), IP addresses, serial numbers—anything that varies between physical machines. Configuration like detection thresholds, capture frequency, and module versions should stay in the fragment so they're consistent across your fleet.

**Apply the fragment to your first machine:**

Now that the fragment exists, update `inspection-station-1` to use it instead of inline configuration:

1. Go to `inspection-station-1`'s **Configure** tab
2. Switch to **JSON** view
3. Delete all the component and service configurations (keep only the machine metadata)
4. Switch back to **Builder** view
5. Click **+** and select **Insert fragment**
6. Select `inspection-station` and click **Add**
7. Set the variable: `{"camera_path": "/dev/video0"}`
8. Click **Save**

The machine reloads with the same configuration, but now it's sourced from the fragment. Any future changes to the fragment will automatically apply to this machine.

#### 4.3 Add a Second Machine

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

**Apply the fragment with variable values:**

1. On `inspection-station-2`, go to the **Configure** tab
2. Click **+** and select **Insert fragment**
3. Search for and select `inspection-station`
4. Click **Add**

The fragment appears in your configuration. Notice the **Variables** section—this is where you provide machine-specific values.

**Set the camera path for this machine:**

1. In the fragment's **Variables** section, add:

```json
{
  "camera_path": "/dev/video0"
}
```

2. Click **Save** in the top right

[SCREENSHOT: Fragment with variables configured]

Within seconds, the machine reloads its configuration. It now has the camera (with the correct device path), vision service, inspector module, data capture, and alerting—all from the fragment, customized for this specific machine.

**Verify it works:**

1. Go to the **Control** tab
2. Check the camera feed
3. Run a detection

Both stations are now running identical inspection logic.

[SCREENSHOT: Fleet view showing both machines online]

#### 4.4 Fleet Management Capabilities

With fragments in place, you have the foundation for managing fleets at any scale. Here's what's possible:

**Push updates across your fleet:**
- **Configuration changes** — Edit the fragment, and all machines using it receive the update automatically within seconds
- **ML model updates** — Change which model the vision service uses; all machines switch to the new version
- **Module updates** — Deploy new versions of your inspection logic across the fleet
- **Capture settings** — Adjust data capture frequency, enable/disable components fleet-wide

**Monitor and maintain remotely:**
- **Fleet dashboard** — View all machines' status, last seen, and health from one screen
- **Aggregated data** — Query inspection results across all stations ("How many FAILs across all machines this week?")
- **Remote diagnostics** — View live camera feeds, check logs, and test components without physical access
- **Alerts** — Get notified when any machine goes offline or exhibits anomalies

**Handle machine-specific variations:**
- **Fragment variables** — Parameterize device paths, IP addresses, serial numbers—anything that differs between physical machines
- **Per-machine overrides** — Add machine-specific configuration on top of fragments when needed
- **Hardware flexibility** — Same inspection logic works whether a station uses USB cameras, CSI cameras, or IP cameras

This same pattern scales from 2 machines to 2,000. The fragment is your single source of truth; Viam handles the distribution.

**Checkpoint:** Two stations running identical inspection logic from a shared fragment. Update the fragment once, and all machines receive the change automatically.

---

### Part 5: Productize (~15 min)

<!-- TODO: Add a section on alerting - query data for FAIL detections and send notifications programmatically -->

**Goal:** Build a customer-facing product.

**Skills:** Building apps with Viam SDKs, white-label deployment.

#### 5.1 Create a Dashboard

You've built a working system—but right now, only you can see it through the Viam app. Your customers need their own interface showing inspection results.

Viam offers two approaches:
1. **Built-in Teleop Dashboard** — No code, drag-and-drop widgets
2. **Custom Web App** — Full control with TypeScript SDK

##### Option A: Built-in Teleop Dashboard (No Code)

Viam's Teleop dashboard lets you create custom views without writing code.

**Create a dashboard workspace:**

1. In the Viam app, go to **Fleet** → **Teleop** tab
2. Click **+ Create workspace**
3. Name it `Inspection Overview`
4. Select the location containing your inspection stations

**Add widgets:**

Click **+ Add widget** and configure:

1. **Camera Stream** — Select `inspection-cam` from any station to show live video
2. **Time Series Graph** — Plot detection confidence over time from `part-detector`
3. **Table Widget** — Display recent detection results with labels and timestamps
4. **Stat Widget** — Show current pass/fail counts

Drag widgets to arrange your layout. The dashboard updates in real-time.

[SCREENSHOT: Teleop dashboard with inspection widgets]

> **Quick wins:** The Teleop dashboard is great for internal monitoring and demos. For customer-facing products with your branding, use Option B.

##### Option B: Custom Web App (TypeScript SDK)

For full control over branding and features, build a custom dashboard with Viam's TypeScript SDK.

**Set up a TypeScript project:**

```bash
mkdir inspection-dashboard && cd inspection-dashboard
npm init -y
npm install @viamrobotics/sdk vite
```

**Create `src/main.ts`:**

```typescript
import * as VIAM from "@viamrobotics/sdk";

// Replace with your credentials (from Viam app → Organization → API Keys)
const API_KEY_ID = "YOUR_API_KEY_ID";
const API_KEY = "YOUR_API_KEY";
const ORG_ID = "YOUR_ORG_ID";

async function createClient(): Promise<VIAM.ViamClient> {
  return await VIAM.createViamClient({
    serviceHost: "https://app.viam.com:443",
    credentials: {
      type: "api-key",
      authEntity: API_KEY_ID,
      payload: API_KEY,
    },
  });
}

async function updateDashboard() {
  const client = await createClient();
  const dataClient = client.dataClient;

  // Query detection results from the last 24 hours
  const results = await dataClient.tabularDataBySQL(
    ORG_ID,
    `SELECT * FROM readings
     WHERE component_name = 'part-detector'
     AND time_received > datetime('now', '-1 day')
     ORDER BY time_received DESC
     LIMIT 100`
  );

  // Calculate stats
  const total = results.length;
  const fails = results.filter((r: any) =>
    JSON.stringify(r).includes("FAIL")
  ).length;
  const passRate = total > 0 ? ((total - fails) / total * 100).toFixed(1) : 0;

  // Update UI
  document.getElementById("total-count")!.textContent = String(total);
  document.getElementById("fail-count")!.textContent = String(fails);
  document.getElementById("pass-rate")!.textContent = `${passRate}%`;
}

// Update on load and every 30 seconds
updateDashboard();
setInterval(updateDashboard, 30000);
```

**Create `index.html`:**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Inspection Dashboard</title>
  <style>
    body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; }
    .stats { display: flex; gap: 20px; margin: 20px 0; }
    .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; flex: 1; }
    .stat-value { font-size: 48px; font-weight: bold; }
    .pass { color: #22c55e; }
    .fail { color: #ef4444; }
  </style>
</head>
<body>
  <h1>Quality Inspection Dashboard</h1>
  <div class="stats">
    <div class="stat-card">
      <div>Recent Inspections</div>
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
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

**Run it:**

```bash
npx vite
```

Open `http://localhost:5173` to see your dashboard.

[SCREENSHOT: Custom dashboard showing inspection stats]

> **This is your product.** No Viam branding—your interface, your design. The same APIs can power a React app, mobile app, or enterprise dashboard.

#### 5.2 Set Up White-Label Auth

Your customers shouldn't log into Viam—they should log into *your* product. Viam supports white-label authentication so your branding appears throughout the experience.

**Add your logo:**

Your logo appears on login screens and emails sent to your users:

```bash
# Get your organization ID from Viam app → Organization Settings
viam organization logo set --org-id <YOUR_ORG_ID> --logo-path logo.png
```

The logo must be PNG format, under 200KB.

**Enable custom authentication:**

```bash
viam organization auth-service enable --org-id <YOUR_ORG_ID>
```

This enables OAuth/OIDC integration so users authenticate through your identity provider.

**Set support email:**

```bash
viam organization support-email set --org-id <YOUR_ORG_ID> --email support@yourcompany.com
```

Now password recovery and verification emails come from your support address, not Viam's.

[SCREENSHOT: Branded login screen with custom logo]

With this configured:
- Users see your logo on login
- Emails come from your support address
- Your branding, your experience

> **Going further:** For full SSO integration with your identity provider (Okta, Auth0, etc.), see the [Authentication documentation](https://docs.viam.com/manage/manage/authentication/).

**Create customer organizations:**

For multi-tenant deployments, create separate organizations for each customer:

1. Each customer gets their own organization
2. They see only their machines
3. You maintain access to all organizations as the provider

This lets you ship a product where each customer has isolated access to their own inspection stations.

#### 5.3 (Optional) Configure Billing

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
| `part-classifier` | mlmodel | TFLite model for PASS/FAIL classification |
| `part-detector` | vision | ML model service connected to camera |
| `rejector` | motor | Pneumatic pusher for rejecting parts |
| `inspector` | generic (module) | Control logic service |
| `offline-alert` | trigger | Email notification when machine goes offline |

### Simulated Events

| Event | Trigger | Purpose |
|-------|---------|---------|
| Part appears | Timer or user action | New item to inspect |

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

3. ~~**Alert mechanism:** What works without user setup?~~ **Resolved:** Using machine health trigger (offline alert) with email notification. Detection-based alerts deferred to Part 5.

4. **Second station:** Identical or slightly different? Identical is simpler; different shows fragment flexibility.

5. **Dashboard complexity:** How much web dev do we include? Keep minimal—point is Viam APIs, not teaching React.

6. **Mobile app control:** Consider introducing mobile SDK / remote control from phone somewhere in the tutorials. Could demonstrate controlling machines from anywhere.
