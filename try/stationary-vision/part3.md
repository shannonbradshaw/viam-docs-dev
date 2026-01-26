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

// main wraps realMain so we can use error returns instead of log.Fatal.
// This pattern makes deferred cleanup (like machine.Close) work properly on errors.
func main() {
	if err := realMain(); err != nil {
		panic(err)
	}
}

func realMain() error {
	// Context carries cancellation signals and deadlines through the call chain
	ctx := context.Background()
	// Logger provides structured logging with levels (Info, Error, Debug)
	logger := logging.NewLogger("cli")

	// Parse command-line flags
	host := flag.String("host", "", "Machine address")
	flag.Parse()

	if *host == "" {
		return fmt.Errorf("need -host flag")
	}

	// Connect to the remote machine using credentials from `viam login`
	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer machine.Close(ctx) // Always close the connection when done

	// List available resources to verify connection works
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

## 3.3 Build the Inspector

Now write code that calls the vision service to detect cans.

We'll call this `Inspector` from the start—even though it only does detection for now. By the end of Part 3, it will also reject defective cans. Naming it `Inspector` now avoids renaming later and reflects what we're building toward.

**Create the config:**

Create `inspector.go` and start with a configuration struct:

```go
package inspector

import (
	"context"
	"fmt"

	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/vision"
)

// Config declares which dependencies the inspector needs.
// Each field names a resource that must exist on the machine.
// When deployed as a module, these come from the JSON config.
// When testing via CLI, we set them directly in code.
type Config struct {
	Camera        string `json:"camera"`         // Name of the camera component
	VisionService string `json:"vision_service"` // Name of the vision service
}

// Validate checks that required fields are present and returns dependency names.
// Viam calls this during configuration to:
// 1. Catch config errors early (before trying to start the service)
// 2. Know which resources to inject into the constructor
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

**Add the Inspector struct and constructor:**

```go
// Inspector handles detection and (eventually) rejection of defective cans.
// For now it only does detection; we'll add rejection in section 3.5.
type Inspector struct {
	conf     *Config
	logger   logging.Logger
	detector vision.Service
}

// NewInspector creates an inspector from a dependencies map.
// This same constructor works whether called from CLI or module.
func NewInspector(deps resource.Dependencies, conf *Config, logger logging.Logger) (*Inspector, error) {
	// Extract the vision service from dependencies by name.
	// FromDependencies looks up the resource and returns it as the correct type.
	// If the resource doesn't exist or isn't a vision service, it returns an error.
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, fmt.Errorf("failed to get vision service %q: %w", conf.VisionService, err)
	}

	return &Inspector{
		conf:     conf,
		logger:   logger,
		detector: detector,
	}, nil
}
```

**Add the Detect method:**

```go
// Detect runs the vision service and returns the best detection.
// Returns: label (e.g., "PASS" or "FAIL"), confidence (0.0-1.0), error
func (i *Inspector) Detect(ctx context.Context) (string, float64, error) {
	// Call vision service, passing camera name so it knows which camera to use.
	// One vision service can work with multiple cameras.
	// The third argument (nil) is for extra parameters we don't need.
	detections, err := i.detector.DetectionsFromCamera(ctx, i.conf.Camera, nil)
	if err != nil {
		return "", 0, err
	}

	// Handle case where nothing was detected
	if len(detections) == 0 {
		return "NO_DETECTION", 0, nil
	}

	// Find the detection with highest confidence score.
	// When multiple objects are detected, we care about the most confident one.
	best := detections[0]
	for _, det := range detections[1:] {
		if det.Score() > best.Score() {
			best = det
		}
	}

	return best.Label(), best.Score(), nil
}
```

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

	inspector "inspection-module"
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

	// Configuration specifying which resources to use.
	// These names must match what you configured in the Viam app.
	conf := &inspector.Config{
		Camera:        "inspection-cam",
		VisionService: "can-detector",
	}

	if _, err := conf.Validate(""); err != nil {
		return err
	}

	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer machine.Close(ctx)

	// Convert machine resources to a Dependencies map.
	// This gives us the same format the module system uses,
	// so our constructor works identically in both contexts.
	deps, err := vmodutils.MachineToDependencies(machine)
	if err != nil {
		return fmt.Errorf("failed to get dependencies: %w", err)
	}

	// Create the inspector using the same constructor the module will use
	insp, err := inspector.NewInspector(deps, conf, logger)
	if err != nil {
		return err
	}

	// Run detection
	label, confidence, err := insp.Detect(ctx)
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

Now extend the inspector to trigger the rejector when a defective can is detected.

**Update the imports in `inspector.go`:**

Add the motor import:

```go
import (
	"context"
	"fmt"

	"go.viam.com/rdk/components/motor" // Add this
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/vision"
)
```

**Add the Rejector field to Config:**

```go
type Config struct {
	Camera        string `json:"camera"`
	VisionService string `json:"vision_service"`
	Rejector      string `json:"rejector"` // Add this
}
```

**Update Validate to include the rejector:**

Add the rejector validation check and include `cfg.Rejector` in the returned dependencies:

```go
func (cfg *Config) Validate(path string) ([]string, error) {
	if cfg.Camera == "" {
		return nil, fmt.Errorf("camera is required")
	}
	if cfg.VisionService == "" {
		return nil, fmt.Errorf("vision_service is required")
	}
	if cfg.Rejector == "" {                                          // NEW
		return nil, fmt.Errorf("rejector is required")               // NEW
	}                                                                // NEW
	return []string{cfg.Camera, cfg.VisionService, cfg.Rejector}, nil  // CHANGED: added cfg.Rejector
}
```

**Add the rejector field to Inspector:**

```go
type Inspector struct {
	conf     *Config
	logger   logging.Logger
	detector vision.Service
	rejector motor.Motor // Add this
}
```

**Update NewInspector to get the rejector:**

Add the rejector lookup after getting the detector, and include it in the returned struct:

```go
func NewInspector(deps resource.Dependencies, conf *Config, logger logging.Logger) (*Inspector, error) {
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, fmt.Errorf("failed to get vision service %q: %w", conf.VisionService, err)
	}

	rejector, err := motor.FromDependencies(deps, conf.Rejector)  // NEW
	if err != nil {                                                // NEW
		return nil, fmt.Errorf("failed to get rejector %q: %w", conf.Rejector, err)  // NEW
	}                                                              // NEW

	return &Inspector{
		conf:     conf,
		logger:   logger,
		detector: detector,
		rejector: rejector,  // NEW
	}, nil
}
```

**Add the reject and Inspect methods:**

```go
// reject activates the rejector motor to push a defective can off the belt.
func (i *Inspector) reject(ctx context.Context) error {
	// GoFor runs the motor at a given speed for a given number of revolutions.
	// Arguments: rpm (speed), revolutions (distance), extra (nil = no extra params)
	// Tune these values based on your actuator - a pneumatic pusher might use
	// different parameters than a servo arm.
	if err := i.rejector.GoFor(ctx, 100, 1, nil); err != nil {
		return err
	}
	i.logger.Info("Defective can rejected")
	return nil
}

// Inspect runs detection and rejects defective cans.
// Returns: label, confidence, whether the can was rejected, error
func (i *Inspector) Inspect(ctx context.Context) (string, float64, bool, error) {
	label, confidence, err := i.Detect(ctx)
	if err != nil {
		return "", 0, false, err
	}

	// Decide whether to reject based on label and confidence.
	// The 0.7 threshold avoids rejecting on uncertain detections.
	// Lower values: catch more defects, risk more false positives
	// Higher values: fewer false positives, might miss some defects
	// Tune based on cost of each error type in your application.
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

**Update the CLI to support both commands:**

Add the `-cmd` flag and update the config and command handling. In `cmd/cli/main.go`:

Add the flag after the `host` flag:

```go
host := flag.String("host", "", "Machine address")
cmd := flag.String("cmd", "detect", "Command: detect or inspect") // Add this
flag.Parse()
```

Add `Rejector` to the config:

```go
conf := &inspector.Config{
	Camera:        "inspection-cam",
	VisionService: "can-detector",
	Rejector:      "rejector", // Add this
}
```

Replace the detection code at the end of `realMain()` (the four lines from `label, confidence, err := insp.Detect(ctx)` through `logger.Infof(...)`) with this switch:

```go
// Handle the requested command
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

**Add the mapstructure import:**

```go
import (
	// ... existing imports ...
	"github.com/mitchellh/mapstructure"
)
```

Run `go get github.com/mitchellh/mapstructure` if needed.

**Add the Command struct and DoCommand method to `inspector.go`:**

```go
// Command represents the commands the inspector accepts via DoCommand.
// Using a struct with mapstructure tags lets us safely decode the
// map[string]interface{} that DoCommand receives.
type Command struct {
	Detect  bool `mapstructure:"detect"`
	Inspect bool `mapstructure:"inspect"`
}

// DoCommand handles incoming commands from clients.
// This is the generic service interface - all operations go through here.
// Using a single entry point with command maps is more flexible than
// defining separate RPC methods for each operation.
func (i *Inspector) DoCommand(ctx context.Context, req map[string]interface{}) (map[string]interface{}, error) {
	// Decode the request map into our typed Command struct.
	// mapstructure handles type coercion (e.g., JSON numbers to bools).
	var cmd Command
	if err := mapstructure.Decode(req, &cmd); err != nil {
		return nil, fmt.Errorf("failed to decode command: %w", err)
	}

	// Dispatch based on which command flag is set.
	// We use a switch on bools rather than a string command name
	// because it's more flexible - could support multiple flags at once.
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

**Update the CLI to use DoCommand:**

This verifies the interface works the same way it will when called remotely. Replace the switch statement you added in section 3.5 with this version that calls through `DoCommand`:

```go
switch *cmd {
case "detect":
	// Call through DoCommand to verify the interface works
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

Add the embedded `AlwaysRebuild` struct and a `name` field:

```go
// Inspector implements resource.Resource for the generic service API.
type Inspector struct {
	// AlwaysRebuild is an embedded struct that tells Viam to destroy and
	// recreate this service when config changes, rather than trying to
	// update it in place. This is simpler than implementing Reconfigure().
	resource.AlwaysRebuild  // NEW

	name     resource.Name  // NEW
	conf     *Config
	logger   logging.Logger
	detector vision.Service
	rejector motor.Motor
}
```

**Update the constructor to accept a resource name:**

Add a `name` parameter and include it in the returned struct:

```go
// NewInspector creates an inspector. This constructor is used by both CLI and module.
func NewInspector(
	deps resource.Dependencies,
	name resource.Name,  // NEW parameter
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
		name:     name,  // NEW
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
// Our inspector doesn't hold any resources that need cleanup -
// the vision service and motor are managed by Viam.
func (i *Inspector) Close(ctx context.Context) error {
	return nil
}
```

**Update the CLI for the new constructor signature:**

Add the import:

```go
import (
	// ... existing imports ...
	"go.viam.com/rdk/services/generic"
)
```

Update the `NewInspector` call to pass a resource name as the second argument:

```go
// generic.Named creates a resource name for the generic service API.
// The string "inspector" is just a local name for logging/debugging.
insp, err := inspector.NewInspector(deps, generic.Named("inspector"), conf, logger)
//                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^ NEW argument
```

**Test it:**

```bash
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd inspect
```

Still works. You've restructured the code without changing behavior.

---

## 3.8 Add Module Registration

Now add the code that lets viam-server discover and instantiate your inspector.

**Add the generic import to `inspector.go`:**

```go
import (
	// ... existing imports ...
	"go.viam.com/rdk/services/generic"
)
```

**Add the Model variable and init function:**

```go
// Model is the full model triplet that identifies this service type.
// Format: namespace:family:model
// - "acme" is your organization namespace (replace with yours from Viam app)
// - "inspection" is the model family (groups related models)
// - "inspector" is the specific model name
var Model = resource.NewModel("acme", "inspection", "inspector")

func init() {
	// Register this model with Viam's resource registry.
	// This runs automatically when the module binary starts (due to Go's init semantics).
	// The registration tells viam-server how to create instances of this service.
	resource.RegisterService(generic.API, Model,
		// Registration is a generic type parameterized by:
		// - resource.Resource: the interface our service implements
		// - *Config: the config type for type-safe config parsing
		resource.Registration[resource.Resource, *Config]{
			Constructor: createInspector,
		},
	)
}

// createInspector is the constructor that viam-server calls.
// It receives raw config (from JSON) and must extract our typed Config.
func createInspector(
	ctx context.Context,
	deps resource.Dependencies,
	rawConf resource.Config,
	logger logging.Logger,
) (resource.Resource, error) {
	// NativeConfig extracts our typed *Config from the raw config.
	// This uses the JSON tags we defined on Config fields.
	conf, err := resource.NativeConfig[*Config](rawConf)
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}
	// Delegate to our shared constructor
	return NewInspector(deps, rawConf.ResourceName(), conf, logger)
}
```

**Create the module entry point:**

Create the directory and file:

```bash
mkdir -p cmd/module
```

Create `cmd/module/main.go`:

```go
package main

import (
	"go.viam.com/rdk/module"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/generic"

	// This blank import runs the inspector package's init() function,
	// which registers our model with Viam's resource registry.
	// Without this import, viam-server wouldn't know our model exists.
	inspector "inspection-module"
)

func main() {
	// ModularMain starts the module and handles communication with viam-server.
	// We pass our API and Model so the module knows what it provides.
	module.ModularMain(
		resource.APIModel{API: generic.API, Model: inspector.Model},
	)
}
```

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
