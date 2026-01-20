# Development Workflow

[← Back to Overview](./index.md) | [← Configuration](./configuration.md)

---

This page explains the CLI development pattern—how to iterate quickly on module code without constant redeployment.

## The Problem

Traditional robotics development:

1. Write code
2. Build module
3. Upload to registry (or copy to machine)
4. Restart viam-server
5. Test
6. Find bug → repeat

Each cycle can cost several minutes. When you're debugging gripper timing or motion paths, that friction kills productivity.

## The Solution: CLI Development

viam-chess has two entry points:

```
cmd/module/main.go  →  Runs on the robot (production)
cmd/cli/main.go     →  Runs on your laptop (development)
```

The CLI connects to your remote machine and uses its hardware, but runs **your local code**:

```
┌─────────────────────┐         ┌─────────────────────┐
│    Your Laptop      │         │    Robot Machine    │
│                     │         │                     │
│  ┌───────────────┐  │         │  ┌───────────────┐  │
│  │  chess logic  │  │ ──────► │  │     arm       │  │
│  │  (your code)  │  │         │  │   gripper     │  │
│  └───────────────┘  │ ◄────── │  │   camera      │  │
│                     │         │  └───────────────┘  │
└─────────────────────┘         └─────────────────────┘
        LOCAL                         REMOTE
```

Your code runs locally. When it calls `arm.MoveToPosition()`, that call goes to the remote arm. You get instant iteration with real hardware.

## How It Works

### Step 1: Connect to Remote Machine

```go
machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
```

`ConnectToHostFromCLIToken` uses your Viam CLI credentials to connect to a machine. You get a `robot.Robot` client that can access all components and services on that machine.

### Step 2: Extract Dependencies

```go
deps, err := vmodutils.MachineToDependencies(machine)
```

`MachineToDependencies` converts the robot client into a `resource.Dependencies` map—the same format your module constructor expects.

### Step 3: Create Your Service Locally

```go
cfg := viamchess.ChessConfig{
    PieceFinder: "piece-finder",
    Arm:         "arm",
    Gripper:     "gripper",
    PoseStart:   "hack-pose-look-straight-down",
}

thing, err := viamchess.NewChess(ctx, deps, generic.Named("foo"), &cfg, logger)
```

Your constructor receives dependencies that point to remote hardware. When your code calls `s.arm.MoveToPosition()`, the call goes over the network to the actual arm.

### Step 4: Run Commands

```go
res, err := thing.DoCommand(ctx, map[string]interface{}{"go": 1})
```

Your local `DoCommand` implementation runs. It calls `piece-finder` (remote), moves the arm (remote), grabs with the gripper (remote)—all from your laptop.

## The Full CLI (cmd/cli/main.go)

```go
func realMain() error {
    ctx := context.Background()
    logger := logging.NewLogger("cli")

    host := flag.String("host", "", "host")
    cmd := flag.String("cmd", "", "command")
    from := flag.String("from", "", "")
    to := flag.String("to", "", "")
    n := flag.Int("n", 1, "")
    flag.Parse()

    // Connect to remote machine
    machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, *host, logger)
    if err != nil {
        return err
    }
    defer machine.Close(ctx)

    // Get dependencies from remote machine
    deps, err := vmodutils.MachineToDependencies(machine)
    if err != nil {
        return err
    }

    // Create YOUR service locally, using remote dependencies
    cfg := viamchess.ChessConfig{
        PieceFinder: "piece-finder",
        Arm:         "arm",
        Gripper:     "gripper",
        PoseStart:   "hack-pose-look-straight-down",
    }
    thing, err := viamchess.NewChess(ctx, deps, generic.Named("foo"), &cfg, logger)
    if err != nil {
        return err
    }
    defer thing.Close(ctx)

    // Execute command
    switch *cmd {
    case "go":
        res, err := thing.DoCommand(ctx, map[string]interface{}{"go": *n})
        logger.Infof("res: %v", res)
        return err
    case "move":
        res, err := thing.DoCommand(ctx, map[string]interface{}{
            "move": map[string]interface{}{"from": *from, "to": *to, "n": *n},
        })
        logger.Infof("res: %v", res)
        return err
    case "reset":
        res, err := thing.DoCommand(ctx, map[string]interface{}{"reset": true})
        return err
    default:
        return fmt.Errorf("unknown command [%s]", *cmd)
    }
}
```

## Development Cycle

### 1. Set Up Authentication

First, authenticate with Viam:

```bash
viam login
```

This stores credentials that `ConnectToHostFromCLIToken` uses.

### 2. Get Your Machine Address

From the Viam app, find your machine's address. It looks like:
```
chess-robot-main.abc123xyz.viam.cloud
```

### 3. Build the CLI

```bash
cd viam-chess
make cli
```

This builds `./chesscli`.

### 4. Run Commands

```bash
# Make one move
./chesscli -host chess-robot-main.abc123xyz.viam.cloud -cmd go -n 1

# Move a specific piece
./chesscli -host chess-robot-main.abc123xyz.viam.cloud -cmd move -from e2 -to e4

# Reset the board
./chesscli -host chess-robot-main.abc123xyz.viam.cloud -cmd reset
```

### 5. Edit and Repeat

Change `chess.go` → `make cli` → run again. No upload, no restart.

## Why This Works

The key insight: **Viam's dependency injection doesn't care where dependencies come from.**

Your constructor expects:
```go
func NewChess(ctx context.Context, deps resource.Dependencies, ...)
```

Whether those dependencies are:
- Local (in-process, production module)
- Remote (over network, CLI development)
- Mock (in tests)

...your code is the same.

## Production Deployment

When your code works, deploy it:

### 1. Build the Module

```bash
make module.tar.gz
```

### 2. Upload to Registry

```bash
viam module upload --version 1.0.0 --platform linux/arm64
```

### 3. Update Machine Config

The machine already has:
```json
{
  "type": "registry",
  "module_id": "erh:viam-chess",
  "version": "latest"
}
```

It will automatically pull your new version.

## Hot Reload (Faster Still)

For even faster iteration, use hot reload:

```json
{
  "type": "registry",
  "module_id": "erh:viam-chess",
  "version": "latest",
  "reload_enabled": true,
  "reload_path": "~/.viam/packages-local/erh_viam-chess_from_reload-module.tar.gz"
}
```

Then:
```bash
make module.tar.gz
scp module.tar.gz robot:~/.viam/packages-local/erh_viam-chess_from_reload-module.tar.gz
```

viam-server detects the file change and hot-reloads the module without restart.

## Testing Strategy

| Phase | Method | Speed |
|-------|--------|-------|
| **Unit tests** | Mock dependencies | Instant |
| **Integration** | CLI against real hardware | Fast |
| **Production** | Deploy module | Slow (but necessary) |

The CLI pattern fills the gap between unit tests and production deployment.

## The vmodutils Package

The `github.com/erh/vmodutils` package provides the CLI development utilities:

```go
// Connect using CLI token (from `viam login`)
machine, err := vmodutils.ConnectToHostFromCLIToken(ctx, host, logger)

// Convert robot client to dependency map
deps, err := vmodutils.MachineToDependencies(machine)
```

You can use this pattern in any Go module you develop.

## Summary

| Traditional | CLI Development |
|-------------|-----------------|
| Change code | Change code |
| Build module | Build CLI |
| Upload to registry | — |
| SSH to machine | — |
| Restart viam-server | — |
| Test | Test |

The CLI pattern removes the upload/deploy/restart cycle entirely. Your laptop becomes an extension of the robot—running your logic while using its hardware.

---

**[← Back to Overview](./index.md)**
