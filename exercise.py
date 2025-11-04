import cv2
import mediapipe as mp
import numpy as np
import streamlit as st # Necessary to access st.session_state

# ---------- Setup ----------
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Helper: Calculate Angle (Unchanged)
def calculate_angle(a, b, c):
    """Calculates the angle between three 2D points."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ab, bc = a - b, c - b
    # Ensure vectors are not zero before calculating dot product
    norm_ab = np.linalg.norm(ab)
    norm_bc = np.linalg.norm(bc)
    if norm_ab == 0 or norm_bc == 0:
        return 0
        
    cos_angle = np.dot(ab, bc) / (norm_ab * norm_bc)
    return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

def process_frame_and_count(frame, mode, pose):
    """
    Processes a single video frame, calculates angles, updates the counter, 
    and draws landmarks and text overlays.
    
    Args:
        frame: The current frame (BGR image) from the webcam.
        mode: The active exercise mode string.
        pose: The initialized mediapipe pose object.

    Returns:
        The processed frame (RGB image) with overlays.
    """
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Set writeable to false for performance
    image_rgb.flags.writeable = False
    results = pose.process(image_rgb)
    image_rgb.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR) # Convert back to BGR for CV drawing

    if results.pose_landmarks:
        # 1. Draw Landmarks
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            # Custom drawing specs for aesthetic dark mode look
            mp_drawing.DrawingSpec(color=(60, 200, 255), thickness=2, circle_radius=3), 
            mp_drawing.DrawingSpec(color=(255, 60, 200), thickness=2, circle_radius=2)) 

        # 2. Extract Landmarks
        lm = results.pose_landmarks.landmark
        
        # Left side landmarks
        shoulder = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x, lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        hip = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x, lm[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x, lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        
        # Right hip for Jumping Jack symmetry
        hip_r= [lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x, lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

        # 3. Exercise-Specific Logic (UNCHANGED LOGIC)
        if mode == "Push Up":
            angle = calculate_angle(shoulder, elbow, wrist)
            if angle > 165:
                st.session_state.pushup_stage = "up"
            elif angle < 90 and st.session_state.pushup_stage == "up":
                st.session_state.pushup_stage = "down"
                st.session_state.pushup_counter += 1
            cv2.putText(image, f'Push-up Count: {st.session_state.pushup_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        elif mode == "Squat":
            angle = calculate_angle(hip, knee, ankle)
            if angle > 160:
                st.session_state.squat_stage = "up"
            elif angle < 95 and st.session_state.squat_stage == "up":
                st.session_state.squat_stage = "down"
                st.session_state.squat_counter += 1
            cv2.putText(image, f'Squat Count: {st.session_state.squat_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        elif mode == "Curl Up":
            angle = calculate_angle(shoulder, hip, knee)
            if angle > 90:
                st.session_state.curlup_stage = "down"
            elif angle < 50 and st.session_state.curlup_stage == "down":
                st.session_state.curlup_stage = "up"
                st.session_state.curlup_counter += 1
            cv2.putText(image, f'Hip Angle: {int(angle)}', (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            cv2.putText(image, f'Curl-Up Count: {st.session_state.curlup_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        elif mode == "Jumping Jack":
            arm_angle = calculate_angle(hip, shoulder, elbow)
            leg_angle = calculate_angle(hip_r, hip, knee)

            if arm_angle > 120 and leg_angle > 97:
                st.session_state.jumpingjack_stage = "up"
            elif arm_angle < 100 and leg_angle < 94 and st.session_state.jumpingjack_stage == "up":
                st.session_state.jumpingjack_stage = "down"
                st.session_state.jumpingjack_counter += 1

            cv2.putText(image, f'Jumping Jack Count: {st.session_state.jumpingjack_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    # Convert back to RGB for Streamlit display
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
