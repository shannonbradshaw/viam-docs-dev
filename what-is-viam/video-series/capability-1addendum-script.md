# Capability #1 Addendum: Fragments for Hardware Configuration
## 75-Second Video Script

**Learning Outcome:** "Common hardware combinations are shared as fragments — I pulled in a fragment, provided an IP and a serial number, and had a fully configured arm with calibrated point clouds in under a minute."

**Demo Setup:** xArm 6 with gripper and Intel RealSense D435 (bench arm, `bench1-main`). Start with the machine's hardware config removed (fragment not applied). Apply the fragment live during the demo. Viam app open in browser.

---

## Script

### [00:00-00:15] Hook (15 seconds)

*Visual:*
- Presenter on camera, bench arm visible in background

*Presenter:*
"You can configure every component individually — arm, camera, gripper, each with its own config block. But common hardware combinations are universal. Everyone using an xArm with a wrist-mounted RealSense camera and a gripper needs the same setup including the frame system that puts point clouds for detected objects in the right place in 3D space. Fragments let you capture the entire hardware stack, callibration, and frame system details once and share it."

*Presenter guidance:*
- "Configure every component individually" — this is what capability 1 showed. Each component gets a config block with its model, attributes, and frame. It works, but it's manual.
- "Common hardware combinations are universal" — an xArm 6 + RealSense D435 + xArm gripper is a combination many people use. The camera resolution (1280x720), the gripper's 150mm offset, the hand-eye calibration offsets (where the camera sits relative to the arm) — these are the same for every instance of this hardware combination.
- "Fragments let you capture that entire hardware stack once and share it" — a fragment is a reusable configuration block. Anyone on Viam can pull it into their machine config. Update the fragment, every machine using it gets the change.

---

### [00:15-00:35] Demo: Apply the Fragment (20 seconds)

*Visual:*
- Viam app CONFIGURE tab — machine has no hardware components configured (or minimal config)
- Click **+**, select **Insert fragment**
- Select the xArm6+RealSense+gripper fragment
- Set the variables:
  ```json
  {
    "arm-ip-address": "192.168.1.220",
    "arm-name": "arm",
    "cam-serial-number": "346222073240"
  }
  ```
- Click **Save**

*Presenter (voiceover):*
"Empty machine. I pull in the fragment — this ensures that my robot has all the necessary hardware drivers and is configured properly to work in this 3D space. Fragments can be parameterized so that you can provide the necessary component-specific settings that vary from one robot to another. I provide three values: the arm's IP address, the camera's serial number, and a name for the arm. Save."

*Presenter guidance:*
- "Empty machine" — the machine has viam-server running but no hardware components configured. This is the starting point for any new machine.
- "Three values" — `arm-ip-address: "192.168.1.220"` is the xArm's static IP on this network. `cam-serial-number: "346222073240"` is the RealSense's USB serial number. `arm-name: "arm"` is used by the gripper and camera to reference the arm in the frame tree. Everything else — the arm model (`viam:ufactory:xArm6`), camera model (`viam:camera:realsense`), gripper model (`viam:ufactory:gripper`), modules, frame offsets — comes from the fragment.

---

### [00:35-00:55] Demo: It's Live (20 seconds)

*Visual:*
- Viam app CONTROL tab — arm is online, camera is streaming
- Switch to 3D view — point cloud appearing in the scene, spatially aligned with the arm model
- Rotate the 3D view to show the point cloud is in the correct position relative to the arm and workspace

*Presenter (voiceover):*
"Arm is online. Camera is streaming. And look at the 3D view — the point cloud from the wrist camera is in the right place in 3D space, aligned with the arm and the workspace. That spatial alignment comes from frame offsets in the fragment — the hand-eye calibration result, the gripper geometry, all captured as part of a reusable configuration fragment.

*Presenter guidance:*
- "Point cloud is in the right place" — the RealSense produces points in its own coordinate frame. For those points to appear correctly in the 3D scene, Viam needs to know exactly where the camera is relative to the arm's end effector. The fragment includes these frame transforms: the camera is offset 83mm in X, -30mm in Y, 18mm in Z from the arm, rotated ~98 degrees. The gripper extends 150mm from the flange.
- "Hand-eye calibration result, captured as configuration" — in traditional setups, these offsets end up hardcoded in URDF files or application code. Here they're part of the component config in the fragment. Anyone using this camera mount gets the same calibrated transforms.
- "Three values and a fragment got us here" — the speed is the point. From no hardware config to a fully operational arm with calibrated point clouds. No driver installation, no frame transform code, no manual calibration.

---

### [00:55-01:15] Payoff (20 seconds)

*Visual:*
- Back to presenter on camera
- 3D view with point cloud still visible on laptop screen behind them

*Presenter:*
"Common hardware combinations shouldn't require starting from scratch. The hardware drivers and other software modules you need, the camera settings, the calibrated frame relationships — all in one fragment. Anyone using this hardware combination pulls it in, provides their IP and camera serial number, and gets a fully configured robot with accurate 3D perception."

"Fragments are also composable. I can build on top of this fragment with control logic that implements a specific robotic solution such as a pick and place application. I can then reuse that fragment across any number of robots in a fleet. Viam agent running on my robot compute machine communicates with the Viam registry to automatically download, install and maintain the software, ML models, and everything else configured in the fragment"

*Presenter guidance:*
- "Shouldn't require starting from scratch" — every person who sets up an xArm 6 + RealSense + gripper faces the same configuration work. Fragments eliminate the repetition.
- "Anyone using this hardware combination" — this isn't a personal template. It's shared infrastructure. The fragment is available to anyone in your organization — or, if published to the Viam Registry, anyone on Viam.
- "Accurate 3D perception" — the frame offsets in the fragment are what make the point cloud spatially correct. Without them, the point cloud floats in the wrong place and motion planning reaches the wrong positions. With them, it just works — from configuration.
- "Shared configuration" — echoes the capability 1 theme. Hardware is configured, not coded. Fragments make that configuration shareable and maintainable.

---

## Production Notes

**Total time:** 75 seconds

**Pacing:**
- Hook sets up the problem quickly — individual config works but common combinations deserve a better pattern.
- Fragment application should feel fast — click, fill in three values, save. Don't linger on keystrokes.
- The 3D view reveal is the centerpiece. Let the viewer see the point cloud aligned in 3D space. Rotate the view. The spatial accuracy from configuration is the proof.
- Payoff ties it together: shared hardware configurations with calibrated frame relationships.

**The narrative arc:**
Common hardware combinations are universal, fragments capture them (hook) → Pull in fragment, provide IP and serial number, save (apply) → Arm online, camera streaming, point cloud aligned in 3D view (live) → Shared configuration with calibrated perception for anyone using this hardware (payoff)

**Key messages:**
1. Common hardware combinations shouldn't require configuring each component from scratch every time
2. Fragments capture the entire hardware stack — components, modules, and calibrated frame relationships
3. Each machine provides only its specific values — IP address, serial number
4. The frame system is configuration — spatial relationships that make point clouds accurate and motion planning work, shared through fragments

**Tone:**
- The hook is practical — "everyone using this combination needs the same setup."
- The demo should feel fast and effortless — the speed is the point.
- The 3D view should feel like the payoff of the speed — you didn't just get hardware online, you got calibrated 3D perception.
- No marketing language. The fragment and the point cloud speak for themselves.

**Connection to Capability 1:**
Extends the hardware configuration story. Capability 1 showed that hardware is configured, not coded. This addendum shows that common configurations are shared, not repeated — and that the frame system makes spatial relationships part of that shared config.

---

## B-Roll Needed

- Bench arm with RealSense and gripper on workbench
- Presenter with arm visible in background
- Close-up of arm with camera mounted on wrist (showing the physical mounting that the frame offsets describe)

## Screen Recordings Needed

- Viam app: CONFIGURE tab with empty/minimal machine config
- Viam app: inserting fragment, filling in three variable values, saving
- Viam app: CONTROL tab showing arm online and camera streaming
- Viam app: 3D view with point cloud appearing, spatially aligned with arm model
- Viam app: rotating 3D view to show alignment from multiple angles
- Clean, readable variable values — large font

## Graphics/Overlays

- Optional: annotate the physical camera mount with the frame offset values (83mm X, -30mm Y, 18mm Z)
- Optional: brief label on 3D view indicating "point cloud from wrist camera"
- Minimal aesthetic — the speed of setup and the 3D view are the story
