# viam-chess: A Chess-Playing Robot

A robot arm that plays chess—picking up pieces, making moves calculated by Stockfish, and resetting the board when the game ends.

**[Watch the demo →](TODO_VIDEO_LINK)** | **Source code:** [github.com/erh/viam-chess](https://github.com/erh/viam-chess)

This guide explains how it works and what Viam features make it possible.

---

## What Makes This Possible

### Your Code Doesn't Know What Hardware It's Using

The chess service calls `arm.MoveToPosition()` — not `xArm6.MoveToPosition()`. It works with *any* 6-DOF arm that implements Viam's Arm API. Swap the xArm for a different brand? Change one line of config. Your application code stays the same.

**Viam pattern:** Hardware abstraction through typed interfaces

### Configuration, Not Code, for Hardware Setup

The arm's IP address, camera serial number, gripper offsets, joint limits — none of this is in the application code. It's in the hardware controllers Viam makes available and simple configuration JSON (and it's reusable via fragments). Deploy to a new machine by providing new variable values, not by editing source files.

**Viam pattern:** Fragments and variables for machine-specific values

### You Say Where, Viam Figures Out How

Moving a gripper to a 3D point requires inverse kinematics, path planning, and collision avoidance. The chess code just says "move here" — Viam's motion service figures out the joint angles and trajectory. The camera is mounted on the arm? The frame system automatically transforms coordinates as the arm moves.

**Viam pattern:** Motion service + frame system for spatial reasoning

### One Config Line Installs a Module

The chess module is published to Viam's registry. Any machine can use it by adding:
```json
{"module_id": "erh:viam-chess", "version": "latest"}
```
No apt-get, no pip, no dependency hell. Viam handles download, installation, and lifecycle.

**Viam pattern:** Module registry for packaging and distribution

---

## How It Works (30-Second Version)

1. **Depth camera** mounted on arm captures the board
2. **piece-finder** vision service analyzes the point cloud to find each square and detect piece colors
3. **chess** service uses Stockfish to pick a move, then commands the arm/gripper to execute it
4. **Motion service** plans collision-free paths through 3D space
5. Game state persists in FEN notation; the robot can resume or reset

---

## Guide Sections

| Section | What You'll Learn |
|---------|-------------------|
| [Architecture](./architecture.md) | How fragments, modules, and services compose into a working system |
| [Code Walkthrough](./code.md) | Inside the Go module: chess logic, piece detection, arm control |
| [Configuration](./configuration.md) | Every config block explained—what it does and why |

---

## Quick Reference

**Hardware:**
- xArm6 robot arm with gripper
- Intel RealSense D435 depth camera (mounted on arm)
- Elgato Stream Deck (optional, for button control)

**Software:**
- `erh:viam-chess` module (chess service + piece-finder vision service)
- `erh:vmodutils` module (arm position saver)
- `viam:ufactory` module (xArm driver)
- `viam:realsense` module (camera driver)
- Stockfish chess engine (installed on the machine)

**Module models:**
- `erh:viam-chess:chess` — Generic service that orchestrates the game
- `erh:viam-chess:piece-finder` — Vision service that locates pieces
- `erh:viam-chess:board-finder-cam` — Camera that crops to just the board

---

## Start Reading

**[Architecture →](./architecture.md)**
