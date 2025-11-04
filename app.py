import streamlit as st
import cv2
import mediapipe as mp
from ui import apply_custom_css, setup_sidebar_ui, display_welcome_screen, update_counter_ui, display_stop_message
from exercise import process_frame_and_count, mp_pose

# ---------- Configuration and Setup ----------
st.set_page_config(page_title="Bend It Right - Your Personal Trainer", layout="wide", page_icon="💪")
apply_custom_css() # Apply custom aesthetics

# Main Header
st.markdown("<h1><span style='color: #3fb950;'>Bend It Right</span> - Live Exercise Tracker 💪</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------- Session State Initialization (Streamlit Standard) ----------
if "pushup_counter" not in st.session_state:
    st.session_state.pushup_counter = 0
    st.session_state.pushup_stage = None

if "squat_counter" not in st.session_state:
    st.session_state.squat_counter = 0
    st.session_state.squat_stage = None

if "curlup_counter" not in st.session_state:
    st.session_state.curlup_counter = 0
    st.session_state.curlup_stage = None

if "jumpingjack_counter" not in st.session_state:
    st.session_state.jumpingjack_counter = 0
    st.session_state.jumpingjack_stage = None


def main():
    """Orchestrates the application flow."""
    # Setup sidebar UI and get current state
    # This call creates the checkbox with key="webcam_toggle" and saves its state to st.session_state.
    mode, run_button, counter_placeholder = setup_sidebar_ui()
    
    # Placeholder for the main video stream
    frame_placeholder = st.empty()

    # Display welcome/instructions if not running
    if not run_button or mode == "None":
        display_welcome_screen(mode, run_button)
        return

    # --- Main Loop Execution ---
    st.success(f"🔥 **Workout Active**: **{mode}** Mode is counting your reps!")
    
    cap = cv2.VideoCapture(0)
    
    # Initialize MediaPipe Pose detection
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        # The loop must only check if the webcam is open. The termination check 
        # is moved inside the loop using session_state.
        while cap.isOpened():
            
            # Check for termination condition by reading the state of the checkbox 
            # from session state. This prevents the duplicate element error.
            if not st.session_state.webcam_toggle:
                break
                
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame using logic from exercise.py
            processed_image_rgb = process_frame_and_count(frame, mode, pose)

            # Display processed frame
            # FIX: Replaced deprecated use_column_width=True with use_container_width=True
            frame_placeholder.image(processed_image_rgb, channels="RGB", use_container_width=True)

            # Update counter UI in the sidebar
            update_counter_ui(mode, counter_placeholder)
            
            # REMOVED: st.sidebar.checkbox("Start Live Webcam Feed", key="webcam_toggle") 
            # This was the cause of the duplicate key error.

    # Clean up and display stop message
    cap.release()
    display_stop_message()


if __name__ == "__main__":
    main()
