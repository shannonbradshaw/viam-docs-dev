# Part 3: Build the Inspector (~15 min)

[← Back to Overview](./index.md) | [← Part 2: Data Capture](./part2.md)

---

**Goal:** Write inspection logic that detects dented cans and rejects them, testing from your laptop.

**Skills:** Viam module generator, SDK usage, module-first development.

## What You'll Build

Your vision pipeline detects dented cans and records the results. Now you'll write code that **acts** on those detections—rejecting defective cans automatically.

This completes the **sense-think-act** cycle that defines robotic systems:

1. **Sense** — Camera captures images
2. **Think** — Vision service classifies cans as PASS/FAIL
3. **Act** — Rejector pushes defective cans off the belt

You'll use the **module-first development pattern**: write code on your laptop, test it against remote hardware over the network. This workflow lets you iterate quickly—edit code, run it, see results—without redeploying after every change.

---

## Prerequisites

Before starting, verify you have the required tools installed.

**Check Go version:**

```bash
go version
```

You need Go 1.21 or later. If Go isn't installed or is outdated, download it from [go.dev/dl](https://go.dev/dl/).

**Install the Viam CLI:**

The Viam CLI is used for authentication, module generation, and deployment. Install it:

```bash
# macOS (Homebrew)
brew tap viamrobotics/brews
brew install viam

# Linux (binary)
sudo curl -o /usr/local/bin/viam https://storage.googleapis.com/packages.viam.com/apps/viam-cli/viam-cli-stable-linux-amd64
sudo chmod +x /usr/local/bin/viam
```

Verify it's installed:

```bash
viam version
```

**Log in to Viam:**

```bash
viam login
```

This stores credentials that your code will use to connect to remote machines.

> **Note:** The Viam CLI (`viam`) is different from `viam-server`. The CLI runs on your development machine; `viam-server` runs on your robot/machine.

---

## 3.1 Generate the Module Scaffold

The Viam CLI can generate module boilerplate for you. This gives you the correct project structure, registration code, and a CLI for testing.

**Create and generate the module:**

```bash
mkdir inspection-module && cd inspection-module
viam module generate
```

When prompted, enter:
- **Language:** `go`
- **Module name:** `inspection-module`
- **Model name:** `inspector`
- **Resource subtype:** `generic-service`
- **Namespace:** Your organization namespace (find it in Viam app under **Organization → Settings**)
- **Visibility:** `private`
- **Enable cloud build:** `no` (for simplicity during development)

The generator creates this structure:

```
inspection-module/
├── cmd/
│   ├── cli/
│   │   └── main.go        # CLI for testing (we'll modify this)
│   └── module/
│       └── main.go        # Module entry point (ready to use)
├── inspector.go           # Your service logic (we'll modify this)
├── meta.json              # Registry metadata (ready to use)
├── Makefile               # Build commands (ready to use)
└── go.mod
```

> **What the generator provides:** Model registration, module entry point, config parsing, and resource lifecycle methods. You just need to add your business logic and remote testing capability.

---

## 3.2 Add Remote Machine Connection

The generated CLI is a stub for local testing. We'll modify it to connect to your remote machine, enabling the fast iteration pattern: edit code locally, test against real hardware instantly.

**Add the vmodutils dependency:**

```bash
go get github.com/erh/vmodutils
```

The `vmodutils` package provides helpers for connecting to remote machines using your Viam CLI credentials.

**Get your machine address:**

1. In the Viam app, go to your machine's page
2. Click **Code sample** in the top right
3. Copy the machine address (looks like `your-machine-main.abc123.viam.cloud`)

[SCREENSHOT: Code sample tab showing machine address]

**Modify the generated CLI:**

Open `cmd/cli/main.go`. The generator created something like this:

```go
func realMain() error {
	ctx := context.Background()
	logger := logging.NewLogger("cli")

	deps := resource.Dependencies{}
	// can load these from a remote machine if you need

	cfg := inspector.Config{}

	thing, err := inspector.NewInspector(ctx, deps, generic.Named("foo"), &cfg, logger)
	// ...
}
```

Replace the entire file with:

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
	if err := realMain(); err != nil {
		panic(err)
	}
}

func realMain() error {
	ctx := context.Background()
	logger := logging.NewLogger("cli")

	// Parse command-line flags
	host := flag.String("host", "", "Machine address (required)")
	cmd := flag.String("cmd", "detect", "Command: detect or inspect")
	flag.Parse()

	if *host == "" {
		return fmt.Errorf("need -host flag (get address from Viam app → Code sample)")
	}

	// Configuration specifying which resources to use.
	// These names must match what you configured in the Viam app.
	conf := &inspector.Config{
		Camera:        "inspection-cam",
		VisionService: "can-detector",
	}

	if _, _, err := conf.Validate(""); err != nil {
		return err
	}

	// Connect to the remote machine using credentials from `viam login`
	logger.Infof("Connecting to %s...", *host)
	machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
	if err != nil {
		return fmt.Errorf("failed to connect: %w", err)
	}
	defer machine.Close(ctx)

	// Convert machine resources to a Dependencies map.
	// This gives us the same format the module system uses.
	deps, err := vmodutils.MachineToDependencies(machine)
	if err != nil {
		return fmt.Errorf("failed to get dependencies: %w", err)
	}

	// Create the inspector using the same constructor the module will use
	insp, err := inspector.NewInspector(ctx, deps, generic.Named("inspector"), conf, logger)
	if err != nil {
		return err
	}
	defer insp.Close(ctx)

	// Run the requested command
	switch *cmd {
	case "detect":
		label, confidence, err := insp.Detect(ctx)
		if err != nil {
			return err
		}
		logger.Infof("Detection: %s (%.1f%% confidence)", label, confidence*100)

	default:
		return fmt.Errorf("unknown command: %s (use 'detect')", *cmd)
	}

	return nil
}
```

**Key changes from the generated stub:**
- Added `flag` package for `-host` and `-cmd` arguments
- Added `vmodutils` import for remote connection
- Replaced empty `deps := resource.Dependencies{}` with actual remote connection
- Added command dispatch (we'll add more commands later)

---

## 3.3 Add Detection Logic

Now modify the generated service to implement detection. The generator created `inspector.go` with stub methods. We'll fill them in.

**Update the Config struct:**

Find the `Config` struct in `inspector.go` and update it:

```go
// Config declares which dependencies the inspector needs.
type Config struct {
	Camera        string `json:"camera"`
	VisionService string `json:"vision_service"`
}

// Validate checks that required fields are present and returns dependency names.
func (cfg *Config) Validate(path string) ([]string, []string, error) {
	if cfg.Camera == "" {
		return nil, nil, fmt.Errorf("camera is required")
	}
	if cfg.VisionService == "" {
		return nil, nil, fmt.Errorf("vision_service is required")
	}
	// Return dependency names so Viam's dependency injection provides them
	return []string{cfg.Camera, cfg.VisionService}, nil, nil
}
```

**Update the imports:**

Make sure your imports include:

```go
import (
	"context"
	"fmt"

	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/generic"
	"go.viam.com/rdk/services/vision"
)
```

**Update the Inspector struct:**

Find the struct (the generator may have named it differently) and ensure it has:

```go
type Inspector struct {
	resource.AlwaysRebuild

	name     resource.Name
	conf     *Config
	logger   logging.Logger
	detector vision.Service
}
```

**Update the constructor:**

The generator created two constructors—one for the module (`newInspector`) and one public (`NewInspector`). Update `NewInspector`:

```go
func NewInspector(
	ctx context.Context,
	deps resource.Dependencies,
	name resource.Name,
	conf *Config,
	logger logging.Logger,
) (*Inspector, error) {
	// Extract the vision service from dependencies by name
	detector, err := vision.FromDependencies(deps, conf.VisionService)
	if err != nil {
		return nil, fmt.Errorf("failed to get vision service %q: %w", conf.VisionService, err)
	}

	return &Inspector{
		name:     name,
		conf:     conf,
		logger:   logger,
		detector: detector,
	}, nil
}
```

Also update the module's internal constructor to call it:

```go
func newInspector(ctx context.Context, deps resource.Dependencies, rawConf resource.Config, logger logging.Logger) (resource.Resource, error) {
	conf, err := resource.NativeConfig[*Config](rawConf)
	if err != nil {
		return nil, err
	}
	return NewInspector(ctx, deps, rawConf.ResourceName(), conf, logger)
}
```

**Add the Detect method:**

```go
// Detect runs the vision service and returns the best detection.
func (i *Inspector) Detect(ctx context.Context) (string, float64, error) {
	// Call vision service, passing camera name
	detections, err := i.detector.DetectionsFromCamera(ctx, i.conf.Camera, nil)
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

**Test the connection and detection:**

```bash
go mod tidy
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud
```

You should see:

```
Connecting to your-machine-main.abc123.viam.cloud...
Detection: PASS (94.2% confidence)
```

Run it several times—results change as different cans pass under the camera.

> **What just happened:** Your laptop connected to the remote machine, called the vision service, and got ML inference results. The code runs locally but uses remote hardware.

<details>
<summary><strong>Troubleshooting: Connection or detection failures</strong></summary>

**"failed to connect" or timeout errors:**
- Verify your machine is online in the Viam app (green dot)
- Check that you've run `viam login` successfully
- Confirm the host address is correct (copy fresh from Code sample tab)

**"failed to get vision service" error:**
- Verify `can-detector` exists in your machine config (Part 1)
- Check the exact name matches—it's case-sensitive

**"NO_DETECTION" result:**
- Normal if no can is in view—wait for one to appear
- Check the camera is working in the Viam app's Test panel

</details>

---

### Milestone 1: Detection Working

You can now detect cans from your laptop. Run the CLI a few times and watch results change as cans pass under the camera.

---

## 3.4 Configure the Rejector

Before writing rejection code, add the rejector hardware to your machine.

**Add the motor component:**

1. In the Viam app, go to your machine's **Configure** tab
2. Click **+** next to your machine in the left sidebar
3. Select **Component**, then **motor**
4. For **Model**, select `fake` (simulated motor for testing)
5. Name it `rejector`
6. Click **Create**
7. Click **Save**

> **Note:** In production, you'd use an actual motor model (like `gpio`) with pin configuration. The `fake` model lets us test control logic without physical hardware.

**Test it in the Viam app:**

1. Find the `rejector` motor in your config
2. Click **Test** at the bottom of its card
3. Try the **Run** controls to verify it responds

[SCREENSHOT: Motor test panel showing rejector controls]

---

## 3.5 Add Rejection Logic

Now extend the inspector to trigger the rejector when a defective can is detected.

**Update the imports in `inspector.go`:**

```go
import (
	"context"
	"fmt"

	"go.viam.com/rdk/components/motor"  // Add this
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/resource"
	"go.viam.com/rdk/services/generic"
	"go.viam.com/rdk/services/vision"
)
```

**Add Rejector to Config:**

```go
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
```

**Add rejector to Inspector struct:**

```go
type Inspector struct {
	resource.AlwaysRebuild

	name     resource.Name
	conf     *Config
	logger   logging.Logger
	detector vision.Service
	rejector motor.Motor  // Add this
}
```

**Update the constructor:**

```go
func NewInspector(
	ctx context.Context,
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

**Add the reject and Inspect methods:**

```go
// reject activates the rejector motor
func (i *Inspector) reject(ctx context.Context) error {
	if err := i.rejector.GoFor(ctx, 100, 1, nil); err != nil {
		return err
	}
	i.logger.Info("Defective can rejected")
	return nil
}

// Inspect runs detection and rejects defective cans
func (i *Inspector) Inspect(ctx context.Context) (string, float64, bool, error) {
	label, confidence, err := i.Detect(ctx)
	if err != nil {
		return "", 0, false, err
	}

	// Reject if FAIL with sufficient confidence
	shouldReject := label == "FAIL" && confidence > 0.7

	if shouldReject {
		if err := i.reject(ctx); err != nil {
			i.logger.Errorw("Failed to reject", "error", err)
		}
	}

	return label, confidence, shouldReject, nil
}
```

**Update the CLI config and add the inspect command:**

In `cmd/cli/main.go`, update the config:

```go
conf := &inspector.Config{
	Camera:        "inspection-cam",
	VisionService: "can-detector",
	Rejector:      "rejector",
}
```

Update the command switch:

```go
switch *cmd {
case "detect":
	label, confidence, err := insp.Detect(ctx)
	if err != nil {
		return err
	}
	logger.Infof("Detection: %s (%.1f%% confidence)", label, confidence*100)

case "inspect":
	label, confidence, rejected, err := insp.Inspect(ctx)
	if err != nil {
		return err
	}
	logger.Infof("Inspection: %s (%.1f%%), rejected=%v", label, confidence*100, rejected)

default:
	return fmt.Errorf("unknown command: %s (use 'detect' or 'inspect')", *cmd)
}
```

**Test both commands:**

```bash
# Detection only
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd detect

# Full inspection with rejection
go run ./cmd/cli -host your-machine-main.abc123.viam.cloud -cmd inspect
```

With a dented can:
```
Inspection: FAIL (87.3%), rejected=true
Defective can rejected
```

---

### Milestone 2: Full Inspection Loop Working

You now have a complete inspect-and-reject system running from your laptop against remote hardware.

---

## 3.6 Summary

You built inspection logic using the module-first development pattern:

1. **Generated** the module scaffold with `viam module generate`
2. **Modified** the CLI to connect to remote machines with vmodutils
3. **Added detection** — called vision service, processed results
4. **Added rejection** — triggered motor based on detection confidence

**The key insight:** Edit code locally, run the CLI, see results on real hardware instantly. No deploy cycle during development.

**Your code is ready.** In Part 4, you'll add the DoCommand interface and deploy it to run on the machine autonomously.

---

**[Continue to Part 4: Deploy as a Module →](./part4.md)**
