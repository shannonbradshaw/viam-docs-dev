# Code Walkthrough

[← Back to Overview](./index.md) | [← Architecture](./architecture.md) | [Next: Configuration →](./configuration.md)

---

This page walks through the Go code that makes viam-chess work.

## Project Structure

```
viam-chess/
├── cmd/
│   ├── module/main.go     # Production entry point (deployed)
│   └── cli/main.go        # Development CLI (runs on your laptop)
├── chess.go               # Main chess service
├── piece_finder.go        # Vision service for detecting pieces
├── reset.go               # Board reset logic
├── common.go              # Shared model definitions
├── meta.json              # Module manifest
└── Makefile
```

Two entry points, one codebase:
- `cmd/module/main.go` — Runs on the robot as a Viam module
- `cmd/cli/main.go` — Runs on your laptop for development, connects to remote hardware

## Module Registration

### common.go — Model Namespace

```go
var family = resource.ModelNamespace("erh").WithFamily("viam-chess")
```

This establishes the namespace `erh:viam-chess` for all models in this module.

### chess.go — Registering the Chess Service

```go
var ChessModel = family.WithModel("chess")  // erh:viam-chess:chess

func init() {
    resource.RegisterService(generic.API, ChessModel,
        resource.Registration[resource.Resource, *ChessConfig]{
            Constructor: newViamChessChess,
        },
    )
}
```

Key points:
- `generic.API` — This is a generic service (uses DoCommand for operations)
- `ChessModel` — Full model name: `erh:viam-chess:chess`
- `*ChessConfig` — The config struct Viam will parse from JSON

### piece_finder.go — Registering the Vision Service

```go
var PieceFinderModel = family.WithModel("piece-finder")  // erh:viam-chess:piece-finder

func init() {
    resource.RegisterService(vision.API, PieceFinderModel,
        resource.Registration[vision.Service, *PieceFinderConfig]{
            Constructor: newPieceFinder,
        },
    )
}
```

Same pattern, but implements `vision.API` instead of `generic.API`.

### cmd/module/main.go — Module Entry Point

```go
func main() {
    module.ModularMain(
        resource.APIModel{vision.API, viamchess.PieceFinderModel},
        resource.APIModel{generic.API, viamchess.ChessModel},
    )
}
```

`ModularMain` handles:
- Socket communication with viam-server
- Config parsing and validation
- Service lifecycle (construct, reconfigure, close)

## Config and Validation

### ChessConfig

```go
type ChessConfig struct {
    PieceFinder string `json:"piece-finder"`
    Arm         string
    Gripper     string
    PoseStart   string `json:"pose-start"`
    Engine      string
    EngineMillis int `json:"engine-millis"`
}
```

Maps directly to JSON:

```json
{
  "piece-finder": "piece-finder",
  "arm": "arm",
  "gripper": "gripper",
  "pose-start": "hack-pose-look-straight-down",
  "engine": "/usr/games/stockfish"
}
```

### Validate — Declaring Dependencies

```go
func (cfg *ChessConfig) Validate(path string) ([]string, []string, error) {
    if cfg.PieceFinder == "" {
        return nil, nil, fmt.Errorf("need a piece-finder")
    }
    if cfg.Arm == "" {
        return nil, nil, fmt.Errorf("need an arm")
    }
    // ... more validation ...

    // Return required dependencies (Viam ensures these exist before constructing)
    return []string{
        cfg.PieceFinder,
        cfg.Arm,
        cfg.Gripper,
        cfg.PoseStart,
        motion.Named("builtin").String(),
    }, nil, nil
}
```

The return value `([]string, []string, error)` is:
1. **Required dependencies** — Must exist, or service won't start
2. **Optional dependencies** — Nice to have, but not required
3. **Error** — Validation failed

Viam uses this to:
- Build the dependency graph
- Ensure services start in the right order
- Pass the correct dependencies to your constructor

## Constructor Pattern

### Two Constructors

```go
// Private: called by Viam with raw config
func newViamChessChess(ctx context.Context, deps resource.Dependencies,
    rawConf resource.Config, logger logging.Logger) (resource.Resource, error) {

    conf, err := resource.NativeConfig[*ChessConfig](rawConf)
    if err != nil {
        return nil, err
    }
    return NewChess(ctx, deps, rawConf.ResourceName(), conf, logger)
}

// Public: called by CLI with typed config
func NewChess(ctx context.Context, deps resource.Dependencies,
    name resource.Name, conf *ChessConfig, logger logging.Logger) (resource.Resource, error) {
    // ... actual construction ...
}
```

Why two constructors?
- `newViamChessChess` — Viam calls this; handles raw JSON → typed config
- `NewChess` — CLI calls this directly with pre-built config

This enables the **CLI development pattern** (covered in [Development Workflow](./development.md)).

### Extracting Dependencies

```go
func NewChess(ctx context.Context, deps resource.Dependencies,
    name resource.Name, conf *ChessConfig, logger logging.Logger) (resource.Resource, error) {

    s := &viamChessChess{
        name:   name,
        logger: logger,
        conf:   conf,
        // ...
    }

    // Get typed dependencies from the dependency map
    s.pieceFinder, err = vision.FromProvider(deps, conf.PieceFinder)
    s.arm, err = arm.FromProvider(deps, conf.Arm)
    s.gripper, err = gripper.FromProvider(deps, conf.Gripper)
    s.poseStart, err = toggleswitch.FromProvider(deps, conf.PoseStart)
    s.motion, err = motion.FromDependencies(deps, "builtin")
    s.rfs, err = framesystem.FromDependencies(deps)

    // Initialize chess engine
    s.engine, err = uci.New(conf.engine())
    err = s.engine.Run(uci.CmdUCI, uci.CmdIsReady, uci.CmdUCINewGame)

    return s, nil
}
```

`FromProvider` and `FromDependencies` give you typed interfaces:
- `s.arm` is type `arm.Arm` — you can call `MoveToPosition`, etc.
- `s.gripper` is type `gripper.Gripper` — you can call `Grab`, `Open`

You don't know or care what specific hardware is behind these interfaces.

## DoCommand — The Service Interface

```go
func (s *viamChessChess) DoCommand(ctx context.Context,
    cmdMap map[string]interface{}) (map[string]interface{}, error) {

    s.doCommandLock.Lock()
    defer s.doCommandLock.Unlock()

    defer func() {
        s.goToStart(ctx)  // Always return to home position
    }()

    var cmd cmdStruct
    mapstructure.Decode(cmdMap, &cmd)

    if cmd.Move.To != "" && cmd.Move.From != "" {
        // Manual move: pick up piece at From, place at To
        return nil, s.movePiece(ctx, cmd.Move.From, cmd.Move.To)
    }

    if cmd.Go > 0 {
        // Make N moves (Stockfish plays both sides)
        for n := range cmd.Go {
            _, err = s.makeAMove(ctx, n == 0)
        }
        return map[string]interface{}{"move": m.String()}, nil
    }

    if cmd.Reset {
        return nil, s.resetBoard(ctx)
    }

    if cmd.Wipe {
        return nil, s.wipe(ctx)  // Clear saved game state
    }

    return nil, fmt.Errorf("unknown command")
}
```

Commands supported:
- `{"go": 5}` — Make 5 moves
- `{"move": {"from": "e2", "to": "e4"}}` — Move specific piece
- `{"reset": true}` — Reset board to starting position
- `{"wipe": true}` — Clear game state file
- `{"skill": 75}` — Adjust engine strength

## Piece Detection (piece_finder.go)

The `piece-finder` is a vision service that analyzes depth camera data.

### CaptureAllFromCamera

```go
func (bc *PieceFinder) CaptureAllFromCamera(ctx context.Context,
    cameraName string, opts viscapture.CaptureOptions,
    extra map[string]interface{}) (viscapture.VisCapture, error) {

    // Get color images and point cloud from depth camera
    ni, _, err := bc.input.Images(ctx, nil, extra)
    pc, err := bc.input.NextPointCloud(ctx, extra)

    // Process the board into 64 squares
    dst, squares, err := BoardDebugImageHack(ret.Image, pc, bc.props)

    // Build result with objects for each square
    ret.Objects = []*viz.Object{}
    for _, s := range squares {
        // Transform from camera frame to world frame
        pc, err := bc.rfs.TransformPointCloud(ctx, s.pc, bc.conf.Input, "world")

        // Label: "e4-1" means square e4, white piece (1=white, 2=black, 0=empty)
        label := fmt.Sprintf("%s-%d", s.name, s.color)
        o, err := viz.NewObjectWithLabel(pc, label, nil)
        ret.Objects = append(ret.Objects, o)
    }

    return ret, nil
}
```

### Detecting Piece Color

```go
// Analyze point cloud to determine: empty (0), white (1), or black (2)
func estimatePieceColor(pc pointcloud.PointCloud) int {
    minZ := pc.MetaData().MaxZ - minPieceSize  // Look at top of pieces
    var totalR, totalG, totalB float64
    count := 0

    pc.Iterate(0, 0, func(p r3.Vector, d pointcloud.Data) bool {
        if p.Z < minZ && d != nil && d.HasColor() {
            r, g, b := d.RGB255()
            totalR += float64(r)
            totalG += float64(g)
            totalB += float64(b)
            count++
        }
        return true
    })

    if count <= 10 {
        return 0  // Empty square
    }

    brightness := (totalR + totalG + totalB) / float64(count) / 3.0
    if brightness > 128 {
        return 1  // White piece
    }
    return 2  // Black piece
}
```

Simple but effective: measure average brightness of points above the board surface.

## Moving Pieces (chess.go)

### The Move Sequence

```go
func (s *viamChessChess) movePiece(ctx context.Context, data viscapture.VisCapture,
    theState *state, from, to string, m *chess.Move) error {

    // If destination has a piece, capture it first
    if to != "-" {
        o := s.findObject(data, to)
        if !strings.HasSuffix(o.Geometry.Label(), "-0") {  // Not empty
            err := s.movePiece(ctx, data, theState, to, "-", nil)  // Move to graveyard
        }
    }

    // Get 3D position of source square
    center, err := s.getCenterFor(data, from, theState)

    // Move gripper above piece
    err = s.moveGripper(ctx, r3.Vector{center.X, center.Y, safeZ})

    // Lower and grab (with retry logic)
    for {
        err = s.moveGripper(ctx, r3.Vector{center.X, center.Y, useZ})
        got, err := s.myGrab(ctx)
        if got {
            break
        }
        useZ -= 10  // Try lower
    }

    // Lift
    err = s.moveGripper(ctx, r3.Vector{center.X, center.Y, safeZ})

    // Move to destination
    destCenter, err := s.getCenterFor(data, to, theState)
    err = s.moveGripper(ctx, r3.Vector{destCenter.X, destCenter.Y, safeZ})
    err = s.moveGripper(ctx, r3.Vector{destCenter.X, destCenter.Y, useZ})

    // Release
    err = s.setupGripper(ctx)  // Open gripper

    // Lift away
    err = s.moveGripper(ctx, r3.Vector{destCenter.X, destCenter.Y, safeZ})

    return nil
}
```

### Motion Planning

```go
func (s *viamChessChess) moveGripper(ctx context.Context, p r3.Vector) error {
    // Calculate gripper orientation (pointing down, with adjustments at edges)
    orientation := &spatialmath.OrientationVectorDegrees{
        OZ:    -1,  // Point down
        Theta: s.startPose.Pose().Orientation().OrientationVectorDegrees().Theta,
    }

    // Tilt slightly when reaching to edges of board
    if p.X > 300 {
        orientation.OX = (p.X - 300) / 1000
    }

    myPose := spatialmath.NewPose(p, orientation)

    // Let motion service figure out the joint angles
    _, err := s.motion.Move(ctx, motion.MoveReq{
        ComponentName: s.conf.Gripper,
        Destination:   referenceframe.NewPoseInFrame("world", myPose),
    })
    return err
}
```

The motion service handles:
- Inverse kinematics (pose → joint angles)
- Path planning (avoid collisions)
- Smooth motion execution

Your code just says "move the gripper here."

## Game State Persistence

```go
type savedState struct {
    FEN       string `json:"fen"`       // Chess position in FEN notation
    Graveyard []int  `json:"graveyard"` // Captured pieces
}

func (s *viamChessChess) saveGame(ctx context.Context, theState *state) error {
    ss := savedState{
        FEN:       theState.game.FEN(),
        Graveyard: theState.graveyard,
    }
    b, _ := json.MarshalIndent(&ss, "", "  ")
    return os.WriteFile(s.fenFile, b, 0666)
}
```

State persists in `$VIAM_MODULE_DATA/state.json`. The robot can:
- Resume a game after restart
- Detect if human moved a piece (sanity check)
- Reset to starting position

## Key Patterns Summary

| Pattern | Example | Benefit |
|---------|---------|---------|
| **Interface dependencies** | `arm.Arm` not `xArm6` | Swap hardware without code changes |
| **Validate returns deps** | `return []string{cfg.Arm, ...}` | Viam ensures deps exist before construction |
| **Two constructors** | `newX` (private) + `NewX` (public) | Enable CLI development pattern |
| **DoCommand map** | `cmd["go"]`, `cmd["reset"]` | Flexible service interface |
| **Frame transforms** | `TransformPointCloud(..., "world")` | Automatic coordinate conversion |
| **Motion service** | `motion.Move(destination)` | Path planning handled for you |

---

**[Next: Configuration →](./configuration.md)**
