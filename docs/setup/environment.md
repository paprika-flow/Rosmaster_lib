# Development Environment

Here are some ways I would recommend writing and running code on the robot. Feel free to use these or any way you want.

## SSH + Terminal Editor (Simplest)

Connect via SSH and use a terminal-based editor like `nano` or `vim`:

```bash
ssh jetson@<robot-ip>
# Edit files directly on the robot
nano my_script.py
python3 my_script.py
```

**Pros:** No setup, works over any connection, minimal resource usage.  
**Cons:** No graphical editor, no file browser.

## SSHFS + SSH (Recommended)

Mount the robot's filesystem on your laptop so you can use your local editor:

```bash
# On your laptop
mkdir -p ~/rosmaster #local folder (keep empty)
# sshfs jetson@<robot-ip>:[robot dir] [local dir]
sshfs jetson@<robot-ip>:/home/jetson ~/rosmaster

# Now files in ~/rosmaster will sync with the robot folder you chose. Saved files are updated in real time.
# Run them over SSH
```
**Pros:** No setup on robot, use any IDE, real-time sync   
**Cons:** Hard to setup `sshfs` command on Mac. 

### SSHFS on Mac
Here is how I got the `SSHFS` command to work on my Mac:
- Using [Homebrew](https://brew.sh/) (highly recommended)
- `brew install sshfs` or `gromgit/fuse/sshfs-mac` are not recommended, they are outdate and could break.
- Use Fuse-T instead.

```bash
brew install macos-fuse-t/homebrew-cask/fuse-t
brew tap macos-fuse-t/homebrew-cask
brew install macos-fuse-t/homebrew-cask/fuse-t-sshfs
```
### SSHFS on linux or Windows
Straight forward. search on Google.


## VS Code Remote

VS Code remote server extension to edit files on the robot.
  
-   ⚠️ In my testing, the Yahboom Ubuntu image (Ubuntu 18.04) does not support remote VS code server. You will need to upgrade to 20.04 for this to work or figure out a way to get it to work on 18.04. 

1. Install the "Remote - SSH" extension in VS Code
2. `Ctrl+Shift+P` → "Remote-SSH: Connect to Host"
3. Enter `jetson@<robot-ip>`
4. VS Code opens a full remote workspace 

**Pros:** Full IDE experience.  
**Cons:** Only works on Ubuntu 20.04 (VS Code Server doesn't support 18.04 arm64 well). Pretty much the same as SSHFS + SSH but with extra steps and overhead.

## RealVNC (Desktop)

The Yahboom image includes RealVNC. This gives you a full Ubuntu desktop:

1. Connect via RealVNC Viewer to the robot's IP
2. Open a terminal, browser, VS Code (if installed), etc.

**Pros:** Full desktop environment. Good for quick, visual testing  
**Cons:** Extremely laggy, almost unusable for regular use. 

## Monitor + Keyboard + Mouse

Plug a monitor into the HDMI port, and a USB keyboard + mouse into the Jetson's USB ports. Use like a regular computer.

**Pros:** Fastest local development, no network dependency.  
**Cons:** not practical for a mobile robot.



