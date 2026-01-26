# Part 3: Control Logic (~40 min)

[← Back to Overview](./index.md) | [← Part 2: Data Capture](./part2.md)

---

**Goal:** Write inspection logic that detects dented cans and rejects them, then deploy it as a module.

**Skills:** Viam SDK, module development, CLI-based testing, module deployment.

## What You'll Build

Your vision pipeline detects dented cans and records the results. Now you'll write code that **acts** on those detections—rejecting defective cans automatically.

This completes the **sense-think-act** cycle that defines robotic systems:

1. **Sense** — Camera captures images
2. **Think** — Vision service classifies cans as PASS/FAIL
3. **Act** — Rejector pushes defective cans off the belt

You'll use the **module-first development pattern**: write code on your laptop, test it against remote hardware over the network, then package and deploy it as a module. This workflow lets you iterate quickly—edit code, run it, see results—without redeploying after every change.

---

## 3.1 Set Up Your Project

Create a Go project with a CLI for testing.

```bash
mkdir inspection-module && cd inspection-module
go mod init inspection-module
go get go.viam.com/rdk
go get github.com/erh/vmodutils
mkdir -p cmd/cli
```

You'll end up with this structure:

```
inspection-module/
├── cmd/
│   └── cli/main.go        # CLI for testing against remote machine
├── inspector.go           # Your service logic
└── go.mod
```

The `vmodutils` package provides helpers for connecting to remote machines using your Viam CLI credentials. This lets your local code talk to hardware running elsewhere.

---

## 3.2 Connect to Your Machine

Before writing inspection logic, verify you can connect to your machine from Go code.

**Get your machine address:**

1. In the Viam app, go to your machine's page
2. Click **Code sample** in the top right
3. Copy the machine address (looks like `your-machine-main.abc123.viam.cloud`)

**Authenticate the CLI:**

The CLI uses your Viam CLI token for authentication. Make sure you're logged in:

```bash
viam login
```

This stores a token that `vmodutils` uses automatically.

**Create the CLI:**

Create `cmd/cli/main.go`:

```go
package main

import (
	"context"
	"flag"
	"fmt"

	"github.com/erh/vmodutils"
	"go.viam.com/rdk/logging"
)

func main() {
	if err := realMain(); err != nil {
		panic(err)
	}
}

func realMain() error {
	ctx := context.Background()
	logger := logging.NewLogger("cli")

	host := flag.String("host", "", "Machine address")
	flag.Parse()

	if *host == "" {
		return fmt.Errorf("need -host flag")
	}

	// Connect to the remote machine using CLI credentials
	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer machine.Close(ctx)

	// List available resources
	logger.Info("Connected! Available resources:")
	for _, name := range machine.ResourceNames() {
		logger.Infof("  %s", name)
	}

	return nil
}
```

**Test the connection:**

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud
```

You should see output listing your machine's resources:

```
Connected! Available resources:
  rdk:component:camera/inspection-cam
  rdk:service:vision/can-detector
  ...
```

> **What just happened:** Your laptop connected to the machine running in Docker (or on physical hardware) over the network. The `vmodutils.ConnectToHostFromCLIToken` function reads your Viam CLI credentials and establishes a secure connection. You now have a `machine` object that can access any component or service on that machine.

**Checkpoint:** If you see your resources listed, you're ready to write inspection logic. If not, verify your machine is online in the Viam app and that you've run `viam login`.

---

## 3.3 Build the Detector

Now write code that calls the vision service to detect cans.

**Create the config:**

Create `inspector.go` and start with a configuration struct:

```go
package inspector

import (
	"context"
	"fmt"

	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/vision"
)

// Config declares which dependencies the inspector needs.
// Each field names a resource that must exist on the machine.
type Config struct {
	Camera        string `json:"camera"`
	VisionService string `json:"vision_service"`
}

// Validate checks the config and returns the names of dependencies.
// Viam calls this during configuration to know what resources to provide.
func (cfg *Config) Validate(path string) ([]string, error) {
	if cfg.Camera == "" {
		return nil, fmt.Errorf("camera is required")
	}
	if cfg.VisionService == "" {
		return nil, fmt.Errorf("vision_service is required")
	}
	// Return dependency names so Viam's dependency injection provides them
	return []string{cfg.Camera, cfg.VisionService}, nil
}
```

The `Validate` function serves two purposes:
1. **Validation** — Ensures required fields are present
2. **Dependency declaration** — Returns resource names so Viam knows what to inject

When you later configure this service in the Viam app, Viam will read these dependency names and pass the corresponding resources to your constructor.

**Add the detector struct and constructor:**

```go
// Detector holds the dependencies needed for detection.
type Detector struct {
	conf     *Config
	detector vision.Service
}

// NewDetector creates a detector from a dependencies map.
// This same function works whether called from CLI or module.
func NewDetector(deps resource.Dependencies, conf *Config) (*Detector, error) {
	// Extract the vision service from dependencies by name
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, fmt.Errorf("failed to get vision service %q: %w", conf.VisionService, err)
	}

	return &Detector{
		conf:     conf,
		detector: detector,
	}, nil
}
```

`vision.FromDependencies` looks up a resource by name in the dependencies map and returns it as the correct type. If the resource doesn't exist or isn't a vision service, it returns an error.

**Add the detect method:**

```go
// Detect runs the vision service and returns the best detection.
func (d *Detector) Detect(ctx context.Context) (string, float64, error) {
	// Call vision service with camera name
	// The vision service captures an image and runs ML inference
	detections, err := d.detector.DetectionsFromCamera(ctx, d.conf.Camera, nil)
	if err != nil {
		return "", 0, err
	}

	if len(detections) == 0 {
		return "NO_DETECTION", 0, nil
	}

	// Find the detection with highest confidence
	best := detections[0]
	for _, det := range detections[1:] {
		if det.Score() > best.Score() {
			best = det
		}
	}

	return best.Label(), best.Score(), nil
}
```

`DetectionsFromCamera` takes a camera name because one vision service can work with multiple cameras. It returns a slice of detections, each with a label (like "PASS" or "FAIL") and a confidence score (0.0 to 1.0).

**Update the CLI to test detection:**

Replace the contents of `cmd/cli/main.go`:

```go
package main

import (
	"context"
	"flag"
	"fmt"

	"github.com/erh/vmodutils"
	"go.viam.com/rdk/logging"

	"inspection-module"
)

func main() {
	if err := realMain(); err != nil {
		panic(err)
	}
}

func realMain() error {
	ctx := context.Background()
	logger := logging.NewLogger("cli")

	host := flag.String("host", "", "Machine address")
	flag.Parse()

	if *host == "" {
		return fmt.Errorf("need -host flag")
	}

	// Configuration - names must match your Viam config
	conf := &inspector.Config{
		Camera:        "inspection-cam",
		VisionService: "can-detector",
	}

	// Validate config
	if _, err := conf.Validate(""); err != nil {
		return err
	}

	// Connect to the remote machine
	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer machine.Close(ctx)

	// Convert machine resources to a Dependencies map
	// This is the same format the module system uses
	deps, err := vmodutils.MachineToDependencies(machine)
	if err != nil {
		return fmt.Errorf("failed to get dependencies: %w", err)
	}

	// Create the detector
	det, err := inspector.NewDetector(deps, conf)
	if err != nil {
		return err
	}

	// Run detection
	label, confidence, err := det.Detect(ctx)
	if err != nil {
		return fmt.Errorf("detection failed: %w", err)
	}

	logger.Infof("Detection: %s (%.1f%% confidence)", label, confidence*100)
	return nil
}
```

**Fetch dependencies and test:**

```bash
go mod tidy
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud
```

You should see output like:

```
Detection: PASS (94.2% confidence)
```

or

```
Detection: FAIL (87.3% confidence)
```

Run it several times—you'll see different results as different cans pass under the camera.

> **What just happened:** Your laptop called the vision service running on the remote machine. The vision service grabbed an image from the camera, ran it through the ML model, and returned detection results. You're running ML inference on remote hardware from local code.

**Checkpoint:** You have working detection. Next, you'll add the ability to reject defective cans.

---

## 3.4 Configure the Rejector

Before writing rejection code, add the rejector hardware to your machine.

**Add the motor component:**

1. In the Viam app, go to your machine's **Configure** tab
2. Click **+** next to your machine in the left sidebar
3. Select **Component**, then **motor**
4. For **Model**, select `fake` (this creates a simulated motor for testing)
5. Name it `rejector`
6. Click **Create**
7. Click **Save** in the top right

> **Note:** In a real deployment, you'd use an actual motor model (like `gpio`) with pin configuration. The `fake` model lets us test the control logic without physical hardware.

**Test it in the Viam app:**

1. Find the `rejector` motor in your config
2. Click **Test** at the bottom of its card
3. Try the **Run** controls to verify it responds

---

## 3.5 Add Rejection Logic

Now extend your code to trigger the rejector when a defective can is detected.

**Update the config:**

In `inspector.go`, add the rejector to the config:

```go
import (
	"context"
	"fmt"

	"go.viam.com/rdk/components/motor"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/vision"
)

type Config struct {
	Camera        string `json:"camera"`
	VisionService string `json:"vision_service"`
	Rejector      string `json:"rejector"`
}

func (cfg *Config) Validate(path string) ([]string, error) {
	if cfg.Camera == "" {
		return nil, fmt.Errorf("camera is required")
	}
	if cfg.VisionService == "" {
		return nil, fmt.Errorf("vision_service is required")
	}
	if cfg.Rejector == "" {
		return nil, fmt.Errorf("rejector is required")
	}
	return []string{cfg.Camera, cfg.VisionService, cfg.Rejector}, nil
}
```

**Create the full Inspector:**

Replace the `Detector` struct with a full `Inspector` that includes the rejector:

```go
// Inspector handles detection and rejection of defective cans.
type Inspector struct {
	conf     *Config
	logger   logging.Logger
	detector vision.Service
	rejector motor.Motor
}

// NewInspector creates an inspector from a dependencies map.
func NewInspector(deps resource.Dependencies, conf *Config, logger logging.Logger) (*Inspector, error) {
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, fmt.Errorf("failed to get vision service %q: %w", conf.VisionService, err)
	}

	rejector, err := motor.FromDependencies(deps, conf.Rejector)
	if err != nil {
		return nil, fmt.Errorf("failed to get rejector %q: %w", conf.Rejector, err)
	}

	return &Inspector{
		conf:     conf,
		logger:   logger,
		detector: detector,
		rejector: rejector,
	}, nil
}
```

**Add the detect method** (same as before, now on Inspector):

```go
func (i *Inspector) Detect(ctx context.Context) (string, float64, error) {
	detections, err := i.detector.DetectionsFromCamera(ctx, i.conf.Camera, nil)
	if err != nil {
		return "", 0, err
	}

	if len(detections) == 0 {
		return "NO_DETECTION", 0, nil
	}

	best := detections[0]
	for _, det := range detections[1:] {
		if det.Score() > best.Score() {
			best = det
		}
	}

	return best.Label(), best.Score(), nil
}
```

**Add the rejection method:**

```go
func (i *Inspector) reject(ctx context.Context) error {
	// GoFor(rpm, revolutions, extra)
	// - 100 RPM: motor speed
	// - 1 revolution: how far to move (pushes the can off)
	// - nil: no extra parameters
	if err := i.rejector.GoFor(ctx, 100, 1, nil); err != nil {
		return err
	}
	i.logger.Info("Defective can rejected")
	return nil
}
```

`GoFor` is the motor API for "run at this speed for this many revolutions." In a real system, you'd tune these values based on your actuator—a pneumatic pusher might use different parameters than a servo arm.

**Add the inspect method that combines detection and rejection:**

```go
// Inspect runs detection and rejects defective cans.
// Returns the label, confidence, and whether the can was rejected.
func (i *Inspector) Inspect(ctx context.Context) (string, float64, bool, error) {
	label, confidence, err := i.Detect(ctx)
	if err != nil {
		return "", 0, false, err
	}

	// Reject if FAIL with high confidence
	// The 0.7 threshold avoids rejecting on uncertain detections
	// Tune this based on your tolerance for false positives vs. missed defects
	shouldReject := label == "FAIL" && confidence > 0.7

	if shouldReject {
		if err := i.reject(ctx); err != nil {
			// Log but don't fail - we still want to return the detection result
			i.logger.Errorw("Failed to reject", "error", err)
		}
	}

	return label, confidence, shouldReject, nil
}
```

The 0.7 confidence threshold is a policy decision. Lower values catch more defects but risk false positives (rejecting good cans). Higher values are more conservative but might miss some defects. In production, you'd tune this based on the cost of each error type.

**Update the CLI:**

```go
package main

import (
	"context"
	"flag"
	"fmt"

	"github.com/erh/vmodutils"
	"go.viam.com/rdk/logging"

	"inspection-module"
)

func main() {
	if err := realMain(); err != nil {
		panic(err)
	}
}

func realMain() error {
	ctx := context.Background()
	logger := logging.NewLogger("cli")

	host := flag.String("host", "", "Machine address")
	cmd := flag.String("cmd", "detect", "Command: detect or inspect")
	flag.Parse()

	if *host == "" {
		return fmt.Errorf("need -host flag")
	}

	conf := &inspector.Config{
		Camera:        "inspection-cam",
		VisionService: "can-detector",
		Rejector:      "rejector",
	}

	if _, err := conf.Validate(""); err != nil {
		return err
	}

	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer machine.Close(ctx)

	deps, err := vmodutils.MachineToDependencies(machine)
	if err != nil {
		return fmt.Errorf("failed to get dependencies: %w", err)
	}

	insp, err := inspector.NewInspector(deps, conf, logger)
	if err != nil {
		return err
	}

	switch *cmd {
	case "detect":
		label, confidence, err := insp.Detect(ctx)
		if err != nil {
			return err
		}
		logger.Infof("Detection: %s (%.1f%%)", label, confidence*100)

	case "inspect":
		label, confidence, rejected, err := insp.Inspect(ctx)
		if err != nil {
			return err
		}
		logger.Infof("Inspection: %s (%.1f%%), rejected=%v", label, confidence*100, rejected)

	default:
		return fmt.Errorf("unknown command: %s (use 'detect' or 'inspect')", *cmd)
	}

	return nil
}
```

**Test both commands:**

```bash
# Detection only
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd detect

# Full inspection with rejection
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd inspect
```

With a good can:
```
Inspection: PASS (94.2%), rejected=false
```

With a dented can:
```
Inspection: FAIL (87.3%), rejected=true
Defective can rejected
```

> **What just happened:** You closed the control loop. Your code detects a defect, decides to reject based on confidence threshold, and actuates the motor. This is the sense-think-act cycle running from your laptop against remote hardware.

**Checkpoint:** Detection and rejection work from the CLI. The logic is complete—now you need to package it so it runs on the machine itself.

---

## 3.6 Add the DoCommand Interface

Before turning this into a module, you need to expose your methods through Viam's **generic service** interface. Generic services use a single `DoCommand` method that accepts arbitrary commands as a map.

**Why DoCommand?** It provides flexibility without defining a custom API. Any client can send commands like `{"detect": true}` or `{"inspect": true}` without needing generated client code. This is ideal for application-specific logic like our inspector.

**Add the DoCommand method to `inspector.go`:**

```go
import (
	// ... existing imports ...
	"github.com/mitchellh/mapstructure"
)

// Command represents the commands the inspector accepts.
type Command struct {
	Detect  bool `mapstructure:"detect"`
	Inspect bool `mapstructure:"inspect"`
}

// DoCommand handles incoming commands.
// This is the generic service interface - all operations go through here.
func (i *Inspector) DoCommand(ctx context.Context, req map[string]interface{}) (map[string]interface{}, error) {
	var cmd Command
	if err := mapstructure.Decode(req, &cmd); err != nil {
		return nil, fmt.Errorf("failed to decode command: %w", err)
	}

	switch {
	case cmd.Detect:
		label, confidence, err := i.Detect(ctx)
		if err != nil {
			return nil, err
		}
		return map[string]interface{}{
			"label":      label,
			"confidence": confidence,
		}, nil

	case cmd.Inspect:
		label, confidence, rejected, err := i.Inspect(ctx)
		if err != nil {
			return nil, err
		}
		return map[string]interface{}{
			"label":      label,
			"confidence": confidence,
			"rejected":   rejected,
		}, nil

	default:
		return nil, fmt.Errorf("unknown command: %v", req)
	}
}
```

The `mapstructure` library decodes `map[string]interface{}` into typed structs. This is safer than manual type assertions and handles type coercion gracefully.

**Update the CLI to use DoCommand:**

This verifies the interface works the same way it will when called remotely:

```go
switch *cmd {
case "detect":
	result, err := insp.DoCommand(ctx, map[string]interface{}{"detect": true})
	if err != nil {
		return err
	}
	logger.Infof("Detection: %s (%.1f%%)",
		result["label"], result["confidence"].(float64)*100)

case "inspect":
	result, err := insp.DoCommand(ctx, map[string]interface{}{"inspect": true})
	if err != nil {
		return err
	}
	logger.Infof("Inspection: %s (%.1f%%), rejected=%v",
		result["label"], result["confidence"].(float64)*100, result["rejected"])

default:
	return fmt.Errorf("unknown command: %s", *cmd)
}
```

**Test it:**

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd inspect
```

Output should be identical to before. The behavior hasn't changed—you've just formalized the interface.

---

## 3.7 Structure as a Viam Resource

To run as a module, your inspector must implement Viam's `resource.Resource` interface. This requires a few additions.

**Update the Inspector struct:**

```go
// Inspector implements resource.Resource for the generic service API.
type Inspector struct {
	// AlwaysRebuild tells Viam to recreate this service when config changes,
	// rather than trying to reconfigure it in place.
	resource.AlwaysRebuild

	name     resource.Name
	conf     *Config
	logger   logging.Logger
	detector vision.Service
	rejector motor.Motor
}
```

`resource.AlwaysRebuild` is an embedded struct that implements the `Reconfigure` method by returning an error, telling Viam to destroy and recreate the resource when configuration changes. This is simpler than implementing incremental reconfiguration.

**Update the constructor signature:**

```go
// NewInspector creates an inspector. This constructor is used by both CLI and module.
func NewInspector(
	deps resource.Dependencies,
	name resource.Name,
	conf *Config,
	logger logging.Logger,
) (*Inspector, error) {
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, fmt.Errorf("failed to get vision service %q: %w", conf.VisionService, err)
	}

	rejector, err := motor.FromDependencies(deps, conf.Rejector)
	if err != nil {
		return nil, fmt.Errorf("failed to get rejector %q: %w", conf.Rejector, err)
	}

	return &Inspector{
		name:     name,
		conf:     conf,
		logger:   logger,
		detector: detector,
		rejector: rejector,
	}, nil
}
```

**Add required interface methods:**

```go
// Name returns the resource name. Required by resource.Resource.
func (i *Inspector) Name() resource.Name {
	return i.name
}

// Close cleans up the resource. Required by resource.Resource.
func (i *Inspector) Close(ctx context.Context) error {
	// No cleanup needed - dependencies are managed by Viam
	return nil
}
```

**Update the CLI for the new constructor:**

```go
import (
	// ... existing imports ...
	"go.viam.com/rdk/services/generic"
)

// In realMain():
insp, err := inspector.NewInspector(deps, generic.Named("inspector"), conf, logger)
```

`generic.Named("inspector")` creates a resource name for the generic service API with the name "inspector".

**Test it:**

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd inspect
```

Still works. You've restructured the code without changing behavior.

---

## 3.8 Add Module Registration

Now add the code that lets viam-server discover and instantiate your inspector.

**Add the Model variable and init function to `inspector.go`:**

```go
// Model is the full model triplet: namespace:family:model
// - "acme" is your organization namespace (replace with yours)
// - "inspection" is the model family (grouping related models)
// - "inspector" is the specific model name
var Model = resource.NewModel("acme", "inspection", "inspector")

func init() {
	// Register this model so viam-server can instantiate it from config.
	// This runs automatically when the module binary starts.
	resource.RegisterService(generic.API, Model,
		resource.Registration[resource.Resource, *Config]{
			Constructor: createInspector,
		},
	)
}

// createInspector is called by viam-server when this service is configured.
// It receives raw config and must extract the typed Config.
func createInspector(
	ctx context.Context,
	deps resource.Dependencies,
	rawConf resource.Config,
	logger logging.Logger,
) (resource.Resource, error) {
	conf, err := resource.NativeConfig[*Config](rawConf)
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}
	return NewInspector(deps, rawConf.ResourceName(), conf, logger)
}
```

The registration has two parts:
- **`init()`** — Runs when the module loads, registering the model with Viam's registry
- **`createInspector`** — Constructor that viam-server calls; extracts typed config and delegates to `NewInspector`

This two-constructor pattern keeps `NewInspector` usable from both CLI (where you have typed config) and module (where config comes as raw JSON).

**Add the import for generic:**

```go
import (
	// ... other imports ...
	"go.viam.com/rdk/services/generic"
)
```

**Create the module entry point:**

Create `cmd/module/main.go`:

```go
package main

import (
	"go.viam.com/rdk/module"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/generic"

	// Import inspector package to trigger init() registration
	inspector "inspection-module"
)

func main() {
	module.ModularMain(
		resource.APIModel{API: generic.API, Model: inspector.Model},
	)
}
```

`module.ModularMain` starts the module process and handles communication with viam-server. The `resource.APIModel` tells it which model this module provides.

**Build the module:**

```bash
mkdir -p bin
go build -o bin/inspection-module ./cmd/module
```

---

## 3.9 Deploy to the Machine

Package your module and upload it to the Viam registry.

**Create `meta.json`:**

```json
{
  "module_id": "acme:inspection-module",
  "visibility": "private",
  "url": "",
  "description": "Can inspection with automatic rejection of defects",
  "models": [
    {
      "api": "rdk:service:generic",
      "model": "acme:inspection:inspector"
    }
  ],
  "entrypoint": "bin/inspection-module"
}
```

Replace `acme` with your Viam organization namespace (find it in the Viam app under **Organization → Settings**).

**Package the module:**

```bash
tar czf module.tar.gz meta.json bin/
```

**Upload to the registry:**

```bash
viam module upload --version 1.0.0 --platform linux/amd64 module.tar.gz
```

> **Note:** Use `linux/arm64` if your machine runs on ARM (like Raspberry Pi).

**Add the module to your machine:**

1. In the Viam app, go to your machine's **Configure** tab
2. Click **+** next to your machine
3. Select **Local module**, then **Local module**
4. Search for your module name (e.g., `acme:inspection-module`)
5. Click **Add module**

**Add the inspector service:**

1. Click **+** next to your machine
2. Select **Service**, then **generic**
3. For **Model**, select your model (e.g., `acme:inspection:inspector`)
4. Name it `inspector`
5. Click **Create**

**Configure the service:**

In the inspector's configuration panel, set the attributes:

```json
{
  "camera": "inspection-cam",
  "vision_service": "can-detector",
  "rejector": "rejector"
}
```

Click **Save**.

**Verify it's running:**

1. Go to the **Logs** tab for your machine
2. Look for log messages from the inspector module
3. You should see it starting up and connecting to its dependencies

The inspector now runs on the machine itself, not your laptop. It will continuously inspect cans and reject defective ones—even when you're not connected.

---

## 3.10 Summary

You built a complete inspection system using the module-first development pattern:

1. **Connected** to the remote machine from local code
2. **Built detection** — called vision service, processed results
3. **Added rejection** — triggered motor based on detection confidence
4. **Formalized the interface** — exposed operations via DoCommand
5. **Structured as a resource** — implemented Viam's resource interface
6. **Registered as a module** — made it discoverable by viam-server
7. **Deployed** — packaged and uploaded to the registry

**The key pattern:** One constructor (`NewInspector`) used by both CLI and module. During development, the CLI connects to remote hardware and calls your constructor directly. In production, viam-server loads your module and calls the same constructor. Same code, different context.

**When to use this pattern:** Any time you're building custom logic that needs to run on a machine. The CLI-first workflow lets you iterate quickly—edit, run, see results—without redeploying after every change.

**Checkpoint:** Your inspection system runs autonomously on the machine. It sees, thinks, and acts—the complete control loop.

---

**[Continue to Part 4: Scale →](./part4.md)**
