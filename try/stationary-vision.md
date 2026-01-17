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

##### Step 1: Scaffold a module project

Create a project structure that supports both local development and production deployment:

{{< tabs >}}
{{% tab name="Go" %}}

```bash
mkdir inspection-module && cd inspection-module
go mod init inspection-module
```

Create this directory structure:

```
inspection-module/
├── cmd/
│   ├── module/main.go     # Production entry point (runs on machine)
│   └── cli/main.go        # Development CLI (runs on your laptop)
├── inspector.go           # Your service logic (used by both)
├── go.mod
└── meta.json              # Module metadata for registry
```

{{% /tab %}}
{{% tab name="Python" %}}

```bash
mkdir inspection-module && cd inspection-module
python3 -m venv venv && source venv/bin/activate
pip install viam-sdk
```

Create this directory structure:

```
inspection-module/
├── src/
│   ├── __init__.py
│   ├── inspector.py       # Your service logic
│   └── __main__.py        # Module entry point
├── cli.py                 # Development CLI
├── meta.json
└── requirements.txt
```

{{% /tab %}}
{{< /tabs >}}

The key insight: **your service logic lives in one place** (`inspector.go` or `inspector.py`) and is used by both the development CLI and the production module. You write the code once.

##### Step 2: Write the service logic

This is the code that runs inspections. It declares its dependencies (camera, vision service) in config and receives them through dependency injection:

{{< tabs >}}
{{% tab name="Go" %}}

Create `inspector.go`:

```go
package inspector

import (
    "context"
    "errors"

    "go.viam.com/rdk/components/camera"
    "go.viam.com/rdk/logging"
    "go.viam.com/rdk/resource"
    "go.viam.com/rdk/services/generic"
    "go.viam.com/rdk/services/vision"
)

// Model identifies this service in the Viam registry
var Model = resource.NewModel("your-org", "inspection", "inspector")

// Config declares dependencies - these names match your machine config
type Config struct {
    Camera        string `json:"camera"`
    VisionService string `json:"vision_service"`
}

// Validate ensures required fields are present
func (c *Config) Validate(path string) ([]string, error) {
    deps := []string{}
    if c.Camera != "" {
        deps = append(deps, c.Camera)
    }
    if c.VisionService != "" {
        deps = append(deps, c.VisionService)
    }
    return deps, nil
}

// Inspector implements your inspection logic
type Inspector struct {
    resource.AlwaysRebuild
    name     resource.Name
    conf     *Config
    cam      camera.Camera
    detector vision.Service
    logger   logging.Logger
}

// NewInspector creates the service - used by both CLI and module
func NewInspector(
    ctx context.Context,
    deps resource.Dependencies,
    name resource.Name,
    conf *Config,
    logger logging.Logger,
) (*Inspector, error) {
    // Get dependencies by name - these come from the machine
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
        cam:      cam,
        detector: detector,
        logger:   logger,
    }, nil
}

// RunInspection captures an image and runs detection
func (i *Inspector) RunInspection(ctx context.Context) (string, float64, error) {
    detections, err := i.detector.DetectionsFromCamera(ctx, i.conf.Camera, nil)
    if err != nil {
        return "", 0, err
    }

    if len(detections) == 0 {
        return "NO_DETECTION", 0.0, nil
    }

    // Find highest confidence detection
    best := detections[0]
    for _, d := range detections[1:] {
        if d.Score() > best.Score() {
            best = d
        }
    }

    return best.Label(), best.Score(), nil
}

// DoCommand exposes inspection through the generic service API
func (i *Inspector) DoCommand(
    ctx context.Context,
    cmd map[string]interface{},
) (map[string]interface{}, error) {
    if _, ok := cmd["inspect"]; ok {
        result, confidence, err := i.RunInspection(ctx)
        if err != nil {
            return nil, err
        }
        return map[string]interface{}{
            "result":     result,
            "confidence": confidence,
        }, nil
    }
    return nil, errors.New("unknown command: use {\"inspect\": true}")
}

// Required interface methods
func (i *Inspector) Name() resource.Name { return i.name }
func (i *Inspector) Close(ctx context.Context) error { return nil }
```

{{% /tab %}}
{{% tab name="Python" %}}

Create `src/inspector.py`:

```python
from typing import ClassVar, Mapping, Any, Optional
from viam.module.types import Reconfigurable
from viam.resource.types import Model, ModelFamily
from viam.services.generic import Generic
from viam.components.camera import Camera
from viam.services.vision import VisionClient
from viam.resource.base import ResourceBase
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.utils import struct_to_dict
from viam.logging import getLogger

LOGGER = getLogger(__name__)

class Inspector(Generic, Reconfigurable):
    """Inspection service - runs on both your laptop (dev) and machine (prod)."""

    MODEL: ClassVar[Model] = Model(
        ModelFamily("your-org", "inspection"), "inspector"
    )

    def __init__(self, name: str):
        super().__init__(name)
        self.camera: Optional[Camera] = None
        self.detector: Optional[VisionClient] = None
        self.camera_name: str = ""

    @classmethod
    def new(
        cls,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase],
    ) -> "Inspector":
        """Create the service - used by both CLI and module."""
        service = cls(config.name)
        service.reconfigure(config, dependencies)
        return service

    def reconfigure(
        self,
        config: ComponentConfig,
        dependencies: Mapping[ResourceName, ResourceBase],
    ):
        """Configure dependencies from the machine."""
        attrs = struct_to_dict(config.attributes)

        self.camera_name = attrs.get("camera", "")
        vision_name = attrs.get("vision_service", "")

        # Get dependencies by name - these come from the machine
        for name, resource in dependencies.items():
            if name.name == self.camera_name:
                self.camera = resource
            elif name.name == vision_name:
                self.detector = resource

    async def run_inspection(self) -> tuple[str, float]:
        """Capture an image and run detection."""
        if not self.detector or not self.camera_name:
            raise ValueError("Inspector not configured")

        detections = await self.detector.get_detections_from_camera(
            self.camera_name
        )

        if not detections:
            return "NO_DETECTION", 0.0

        # Find highest confidence detection
        best = max(detections, key=lambda d: d.confidence)
        return best.class_name, best.confidence

    async def do_command(
        self, command: Mapping[str, Any], **kwargs
    ) -> Mapping[str, Any]:
        """Expose inspection through the generic service API."""
        if "inspect" in command:
            result, confidence = await self.run_inspection()
            return {"result": result, "confidence": confidence}
        raise ValueError("Unknown command: use {'inspect': True}")
```

{{% /tab %}}
{{< /tabs >}}

Notice what this code does **not** do: it doesn't connect to the machine or manage credentials. It receives its dependencies (camera, vision service) already connected. This is what makes the same code work in both development and production.

##### Step 3: Write the development CLI

This is where the module-first pattern shines. The CLI connects to your remote machine, gets the dependencies, and creates your service locally:

{{< tabs >}}
{{% tab name="Go" %}}

Create `cmd/cli/main.go`:

```go
package main

import (
    "context"
    "flag"
    "fmt"

    "go.viam.com/rdk/logging"
    "go.viam.com/rdk/services/generic"
    vmodutils "go.viam.com/rdk/module/modmanager/vmodutils"

    "inspection-module"  // Your service package
)

func main() {
    host := flag.String("host", "", "Machine address (e.g., your-machine.viam.cloud)")
    cameraName := flag.String("camera", "inspection-cam", "Camera name")
    visionName := flag.String("vision", "part-detector", "Vision service name")
    flag.Parse()

    if *host == "" {
        fmt.Println("Usage: inspector-cli -host YOUR_MACHINE_ADDRESS")
        return
    }

    ctx := context.Background()
    logger := logging.NewLogger("inspector-cli")

    // 1. Connect to the REMOTE machine using CLI token auth
    machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
    if err != nil {
        logger.Fatal(err)
    }
    defer machine.Close(ctx)
    logger.Info("Connected to machine")

    // 2. Get dependencies from the remote machine
    deps, err := vmodutils.MachineToDependencies(machine)
    if err != nil {
        logger.Fatal(err)
    }

    // 3. Create YOUR service LOCALLY using remote dependencies
    cfg := &inspector.Config{
        Camera:        *cameraName,
        VisionService: *visionName,
    }
    svc, err := inspector.NewInspector(
        ctx, deps, generic.Named("inspector"), cfg, logger,
    )
    if err != nil {
        logger.Fatal(err)
    }
    defer svc.Close(ctx)
    logger.Info("Inspector service created")

    // 4. Run inspection - your code runs locally, talks to remote hardware
    result, err := svc.DoCommand(ctx, map[string]interface{}{"inspect": true})
    if err != nil {
        logger.Fatal(err)
    }

    fmt.Printf("Result: %s (%.1f%% confidence)\n",
        result["result"], result["confidence"].(float64)*100)
}
```

{{% /tab %}}
{{% tab name="Python" %}}

Create `cli.py`:

```python
import asyncio
import sys
from viam.robot.client import RobotClient
from viam.rpc.dial import DialOptions
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from google.protobuf.struct_pb2 import Struct

from src.inspector import Inspector

async def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python cli.py MACHINE_ADDRESS [--camera NAME] [--vision NAME]")
        return

    host = sys.argv[1]
    camera_name = "inspection-cam"
    vision_name = "part-detector"

    # Parse optional args
    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg == "--camera" and i + 1 < len(args):
            camera_name = args[i + 1]
        elif arg == "--vision" and i + 1 < len(args):
            vision_name = args[i + 1]

    # 1. Connect to the REMOTE machine
    # Use API key auth - get credentials from Viam app
    robot = await RobotClient.at_address(
        host,
        RobotClient.Options.with_api_key(
            api_key="YOUR_API_KEY",      # From Viam app
            api_key_id="YOUR_API_KEY_ID"
        )
    )
    print(f"Connected to {host}")

    # 2. Build dependencies dict from remote machine resources
    deps = {}
    for name in await robot.resource_names:
        resource = await robot.get_component(name) if "component" in str(name) \
            else await robot.get_service(name)
        deps[name] = resource

    # 3. Create YOUR service LOCALLY using remote dependencies
    attrs = Struct()
    attrs.update({"camera": camera_name, "vision_service": vision_name})
    config = ComponentConfig(name="inspector", attributes=attrs)

    svc = Inspector.new(config, deps)
    print("Inspector service created")

    # 4. Run inspection - your code runs locally, talks to remote hardware
    result = await svc.do_command({"inspect": True})
    print(f"Result: {result['result']} ({result['confidence']*100:.1f}% confidence)")

    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
```

{{% /tab %}}
{{< /tabs >}}

**The magic here**: Your service code runs on your laptop, but when it calls `detector.DetectionsFromCamera()`, that call goes over the network to the camera and vision service running on the remote machine. The image capture and ML inference happen on the machine; only results come back.

##### Step 4: Set up CLI authentication

Before running the CLI, authenticate with Viam:

{{< tabs >}}
{{% tab name="Go" %}}

The Go CLI uses `vmodutils.ConnectToHostFromCLIToken()`, which reads credentials from the Viam CLI config. Run this once:

```bash
viam login
```

This stores your credentials in `~/.viam/`. The CLI will automatically use them.

{{% /tab %}}
{{% tab name="Python" %}}

Get API credentials from the Viam app:

1. Go to your organization's **Settings** page
2. Click **API Keys** → **Create API Key**
3. Copy the key and key ID into your `cli.py`

{{% /tab %}}
{{< /tabs >}}

##### Step 5: Iterate on your logic

Now you can rapidly develop and test:

{{< tabs >}}
{{% tab name="Go" %}}

```bash
# Build the CLI
go build -o inspector-cli ./cmd/cli

# Run against your machine
./inspector-cli -host your-machine.viam.cloud
```

{{% /tab %}}
{{% tab name="Python" %}}

```bash
python cli.py your-machine.viam.cloud
```

{{% /tab %}}
{{< /tabs >}}

```
Connected to machine
Inspector service created
Result: PASS (94.2% confidence)
```

Edit `inspector.go` (or `inspector.py`), rebuild, run again. No deployment, no waiting. Your code runs locally but uses real hardware.

##### Step 6: Add the module entry point

When your logic is working, add the production entry point:

{{< tabs >}}
{{% tab name="Go" %}}

First, add registration code to `inspector.go`:

```go
func init() {
    resource.RegisterService(generic.API, Model,
        resource.Registration[resource.Service, *Config]{
            Constructor: func(
                ctx context.Context,
                deps resource.Dependencies,
                conf resource.Config,
                logger logging.Logger,
            ) (resource.Service, error) {
                cfg, err := resource.NativeConfig[*Config](conf)
                if err != nil {
                    return nil, err
                }
                return NewInspector(ctx, deps, conf.ResourceName(), cfg, logger)
            },
        })
}
```

Create `cmd/module/main.go`:

```go
package main

import (
    "go.viam.com/rdk/module"
    "go.viam.com/rdk/resource"
    "go.viam.com/rdk/services/generic"

    "inspection-module"  // Imports trigger init() registration
)

func main() {
    module.ModularMain(
        resource.APIModel{API: generic.API, Model: inspector.Model},
    )
}
```

{{% /tab %}}
{{% tab name="Python" %}}

Create `src/__main__.py`:

```python
import asyncio
from viam.module.module import Module
from viam.services.generic import Generic

from .inspector import Inspector

async def main():
    module = Module.from_args()
    module.add_model_from_registry(Generic.SUBTYPE, Inspector.MODEL)
    await module.start()

if __name__ == "__main__":
    asyncio.run(main())
```

{{% /tab %}}
{{< /tabs >}}

##### Step 7: Deploy to the registry

Create `meta.json`:

```json
{
  "module_id": "your-org:inspection-module",
  "visibility": "private",
  "url": "",
  "description": "Part inspection service",
  "models": [
    {
      "api": "rdk:service:generic",
      "model": "your-org:inspection:inspector"
    }
  ],
  "entrypoint": "run.sh"
}
```

Build and upload:

{{< tabs >}}
{{% tab name="Go" %}}

```bash
# Build the module binary
go build -o inspector ./cmd/module

# Create the tarball
tar -czvf module.tar.gz inspector meta.json

# Upload to registry
viam module upload --version 1.0.0 --platform linux/amd64 module.tar.gz
```

{{% /tab %}}
{{% tab name="Python" %}}

```bash
# Create run script
echo '#!/bin/bash
exec python3 -m src "$@"' > run.sh
chmod +x run.sh

# Create tarball
tar -czvf module.tar.gz src run.sh meta.json requirements.txt

# Upload
viam module upload --version 1.0.0 --platform linux/amd64 module.tar.gz
```

{{% /tab %}}
{{< /tabs >}}

##### Step 8: Add the module to your machine

In the Viam app:

1. Go to your machine's **Config** tab
2. Click **+ Create service** → **generic**
3. Select your module from the registry
4. Configure it with your camera and vision service names:

```json
{
  "camera": "inspection-cam",
  "vision_service": "part-detector"
}
```

5. Save the config

The machine pulls your module and runs it. The exact same `inspector.go` or `inspector.py` code that worked on your laptop now runs on the machine itself.

##### What you've built

- **Same code, two entry points**: `inspector.go` is used by both the CLI (development) and the module (production)
- **Remote dependencies, local execution**: During development, your code runs locally but uses remote hardware over the network
- **Fast iteration**: Edit, rebuild CLI, test—no deployment needed until you're ready
- **Zero changes for production**: Package and upload; the machine runs your code unmodified

> **This is module-first development.** You prototype against real hardware without deploying, then ship the exact same logic as a production module. The pattern works for any Viam service—inspection, navigation, custom sensors, integrations with external systems.

**Checkpoint:** You've built a modular inspection service, tested it locally against remote hardware, and deployed it to the registry. This is the development workflow for production Viam applications.

---

### Part 2: Automate (~15 min)

**Goal:** Configure continuous data capture and alerting so inspections run automatically.

**Skills:** Data capture configuration, cloud sync, filtered cameras, triggers and notifications.

#### 2.1 Configure Data Capture

In Part 1, you ran inspection sessions manually from your laptop. That's great for testing and debugging, but for production you want inspections running continuously—without anyone connected.

Viam handles this through *data capture*: you configure which components and services should capture data, how often, and Viam does the rest. No scripts to deploy, no processes to manage.

**Enable data capture on the vision service:**

1. In the Viam app, go to your machine's **Config** tab
2. Find the `part-detector` vision service
3. Click the **Data capture** section to expand it
4. Toggle **Enable data capture** to on
5. Set the capture frequency (e.g., every 2 seconds)
6. Select the method to capture: `GetClassificationsFromCamera` or `GetDetectionsFromCamera`
7. Click **Save config**

[SCREENSHOT: Vision service data capture configuration]

**Also capture camera images:**

For quality inspection, you often want the raw images alongside detection results—so you can review what the model saw.

1. Find the `inspection-cam` camera in your config
2. Expand **Data capture**
3. Toggle **Enable data capture** to on
4. Set frequency to match your vision service (e.g., every 2 seconds)
5. Click **Save config**

[SCREENSHOT: Camera data capture configuration]

When you save, viam-server immediately starts capturing. Every 2 seconds, it runs detection on the camera and saves the results to local storage.

#### 2.2 Sync Data to the Cloud

Data captured on the machine is automatically synced to Viam's cloud. This happens in the background—you don't need to configure anything beyond enabling capture.

**Watch the sync happen:**

1. Go to the **Data** tab in your organization (not the machine)
2. You should see data appearing within a minute or two

[SCREENSHOT: Data tab showing captured detections]

The data includes:
- **Detection results** — Every classification with label and confidence
- **Camera images** — The raw frames, viewable inline
- **Timestamps** — When each capture occurred
- **Machine ID** — Which machine captured it

**Query the data:**

You can filter and search captured data:

1. Filter by machine: `inspection-station-1`
2. Filter by time range: last hour, today, custom range
3. Filter by component: `part-detector`

[SCREENSHOT: Data tab with filters applied]

> **What's happening:** The machine runs continuously, capturing inspection results and syncing them to the cloud. You don't need a laptop connected. You don't need a script running. The data flows automatically based on your configuration.

#### 2.3 Alert on Failures

Capturing data is useful, but you need to know immediately when defects are detected. Viam's trigger system lets you send notifications when specific conditions occur—no custom code required.

**Add a filtered camera:**

A filtered camera wraps your existing camera and vision service, only outputting images when detections match your criteria. We'll configure one that captures only FAIL detections.

1. In the Viam app, go to **Config** tab
2. Click **+ Add component**
3. For **Type**, select `camera`
4. For **Model**, search for and select `filtered-camera`
5. Name it `fail-detector-cam`
6. Click **Create**

**Configure the filter:**

1. In the `fail-detector-cam` configuration panel, set:
   - **camera**: `inspection-cam` (your source camera)
   - **vision_service**: `part-detector` (your ML service)
   - **classifications** or **objects**: Add `FAIL` as the label to match
   - **confidence_threshold**: `0.7` (only capture high-confidence failures)

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

2. Click **Save config**

[SCREENSHOT: Filtered camera configuration]

**Enable data capture on the filtered camera:**

1. Expand **Data capture** on `fail-detector-cam`
2. Toggle **Enable data capture** to on
3. Set frequency (e.g., every 1 second)
4. Click **Save config**

Now only FAIL detections (with confidence ≥70%) are captured and synced.

**Configure a trigger for notifications:**

1. In the Viam app, go to **Config** tab
2. Scroll to the **Triggers** section (or find it in the left sidebar)
3. Click **+ Add trigger**
4. Configure:
   - **Name**: `fail-alert`
   - **Event type**: `Data has been synced to the cloud`
   - **Data type**: Select the filtered camera's data

**Add email notification:**

1. Under **Notifications**, click **Add notification**
2. Select **Email**
3. Enter your email address (or select **Email all machine owners**)
4. Set **Seconds between notifications**: `3600` (max one alert per hour)
5. Click **Save config**

[SCREENSHOT: Trigger configuration with email notification]

**Test the alert:**

Wait for a FAIL detection to occur (or trigger one in the simulation). Within a few minutes, you should receive an email notification.

> **Going further:** You can also configure webhook notifications to integrate with Slack, PagerDuty, or any other service. The webhook receives the detection data, and your cloud function can format and route the alert however you need.

#### 2.4 Understand the Pattern

Compare what you've done in Part 1 vs. Part 2:

| Part 1: SDK Tool | Part 2: Data Capture |
|------------------|---------------------|
| Runs on your laptop | Runs on the machine |
| You trigger it manually | Runs continuously, automatically |
| Results saved locally (CSV, images) | Results synced to cloud |
| Good for testing, debugging, one-off analysis | Good for production, ongoing monitoring |

**Both are useful.** The SDK tool from Part 1 remains valuable:
- Run it when testing a new ML model
- Use it to debug when something seems wrong
- Generate local reports for specific analysis

Data capture in Part 2 provides the production foundation:
- Continuous operation without intervention
- Cloud storage and sync
- Data available for dashboards, alerting, analysis

> **The clean pattern:** The machine runs viam-server with configured components and services. Data capture handles automation. Triggers handle alerting. Your code runs remotely (laptop, server, cloud functions) and connects via SDK to query data or build applications. You don't deploy scripts to run on the machine—you configure the platform.

**Checkpoint:** Inspection data flows continuously from machine to cloud. You get notified when failures occur. No scripts deployed, no processes to manage—just configuration.

---

### Part 3: Scale (~10 min)

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

### Part 4: Fleet (~10 min)

**Goal:** Manage both stations as a fleet.

**Skills:** Fleet monitoring, pushing updates.

#### 4.1 View Your Fleet

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

#### 4.2 Push a Configuration Update

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

### Part 5: Maintain (~10 min)

**Goal:** Debug and fix an issue.

**Skills:** Remote diagnostics, log analysis, incident response.

#### 5.1 Simulate a Problem

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

#### 5.2 Diagnose Remotely

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

#### 5.3 Fix and Verify

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

### Part 6: Productize (~15 min)

**Goal:** Build a customer-facing product.

**Skills:** Building apps with Viam SDKs, white-label deployment.

#### 6.1 Create a Customer Dashboard

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

#### 6.2 Set Up White-Label Auth

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

#### 6.3 (Optional) Configure Billing

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
