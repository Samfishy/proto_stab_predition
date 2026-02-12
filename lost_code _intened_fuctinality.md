# STM32 Dual-Task Camera System  
**Stabilization + Face Detection and Tracking**

## Overview
This project implements a **dual-task embedded vision system** on an STM32 microcontroller.  
The firmware runs two parallel tasks:

1. **Camera Stabilization** using IMU data and servo control.
2. **Face Detection and Tracking** using camera zone analysis and ToF data.

The objective is to keep a detected face centered in the frame while maintaining mechanical stabilization of the camera.

---

## System Functions

### 1. Stabilization Task
- Uses **IMU sensor data** (gyro/accelerometer).
- Controls **4 servos** to keep the camera frame upright.
- Runs inside a **timer interrupt** for deterministic response.
- Continuously adjusts orientation to stabilize the center of the frame.

**Goal:**  
Maintain a stable and level camera orientation regardless of motion.

---

### 2. Face Detection and Tracking Task
- Camera frame is divided into **64 zones (8×8 grid)**.
- The center of the frame is treated as a **reference dot**.
- System tracks in which zone the dot lies relative to the detected face.

#### Tracking Process
1. Camera captures frame.
2. Face detection identifies the face region.
3. Frame is mapped into **64 zones**.
4. ToF sensor provides **64-zone depth values**.
5. Depth and face position data are combined across **2–3 frames**.
6. A **2D prediction vector** is generated.
7. The zone where the dot lies becomes the new target center.
8. Servo corrections are applied to keep the face centered while stabilization runs.

**Goal:**  
Continuously adjust camera orientation to keep the detected face at the center.

---

## System Architecture
