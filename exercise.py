import cv2
import mediapipe as mp
import numpy as np
import streamlit as st # Necessary to access st.session_state
import time # <-- NEW IMPORT

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
    Processes a single video frame, calculates angles, updates the counter/timer, 
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
        shoulder_l = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow_l = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist_l = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x, lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        hip_l = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x, lm[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee_l = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x, lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle_l = [lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        
        # Right side landmarks
        shoulder_r = [lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow_r = [lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, lm[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        hip_r = [lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x, lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee_r = [lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        ankle_r = [lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, lm[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]


        # 3. Exercise-Specific Logic 
        if mode == "Push Up":
            angle = calculate_angle(shoulder_l, elbow_l, wrist_l)
            if angle > 165:
                st.session_state.pushup_stage = "up"
            elif angle < 90 and st.session_state.pushup_stage == "up":
                st.session_state.pushup_stage = "down"
                st.session_state.pushup_counter += 1
            cv2.putText(image, f'Push-up Count: {st.session_state.pushup_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        elif mode == "Squat":
            angle = calculate_angle(hip_l, knee_l, ankle_l)
            if angle > 160:
                st.session_state.squat_stage = "up"
            elif angle < 95 and st.session_state.squat_stage == "up":
                st.session_state.squat_stage = "down"
                st.session_state.squat_counter += 1
            cv2.putText(image, f'Squat Count: {st.session_state.squat_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        elif mode == "Curl Up":
            angle = calculate_angle(shoulder_l, hip_l, knee_l)
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
            arm_angle = calculate_angle(hip_l, shoulder_l, elbow_l)
            leg_angle = calculate_angle(hip_r, hip_l, knee_l)

            if arm_angle > 120 and leg_angle > 97:
                st.session_state.jumpingjack_stage = "up"
            elif arm_angle < 100 and leg_angle < 94 and st.session_state.jumpingjack_stage == "up":
                st.session_state.jumpingjack_stage = "down"
                st.session_state.jumpingjack_counter += 1

            cv2.putText(image, f'Jumping Jack Count: {st.session_state.jumpingjack_counter}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # Tree Pose Timer Logic (Uses stopwatch timer)
        elif mode == "Tree Pose":
            
            # 1. Arm Angle (overhead, straight elbows, arms up)
            arm_angle_l = calculate_angle(hip_l, shoulder_l, elbow_l)
            arm_angle_r = calculate_angle(hip_r, shoulder_r, elbow_r)

            arms_up = arm_angle_l > 160 and arm_angle_r > 160

            # 2. Lifted Leg Angle (Left hip-knee-ankle should be bent for foot placement)
            lifted_leg_angle = calculate_angle(hip_l, knee_l, ankle_l)
          
            
            # Check if the posture is correct (All three criteria must be met)
            posture_correct = arms_up and lifted_leg_angle > 70

            if posture_correct:
                
                # START/CONTINUE TIMER
                if st.session_state.tree_pose_start_time is None:
                    # Start the timer if it was paused or just started
                    st.session_state.tree_pose_start_time = time.time()
                
                # Calculate the elapsed duration
                current_time = time.time()
                st.session_state.tree_pose_hold_duration = current_time - st.session_state.tree_pose_start_time
                
                status_text = "Holding Pose"
                status_color = (0, 255, 0) # Green
            else:
                # PAUSE TIMER: Posture is incorrect, reset the start time
                st.session_state.tree_pose_start_time = None
                
                status_text = "Adjust Pose"
                status_color = (0, 0, 255) # Red
                
            # Display status and duration on screen
            cv2.putText(image, f'Status: {status_text}', (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            cv2.putText(image, f'Time: {st.session_state.tree_pose_hold_duration:.1f}s', (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            cv2.putText(image, f'Leg Angle L: {int(lifted_leg_angle)}', (10, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
    
    # Convert back to RGB for Streamlit display
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
