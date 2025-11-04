import streamlit as st

def apply_custom_css():
    """Applies custom CSS for a dark, aesthetic theme."""
    st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0d1117; /* Dark background */
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #58a6ff; /* Primary Blue for Headings */
        font-weight: 700;
    }
    
    /* Sidebar Styling */
    .stSidebar {
        background-color: #161b22 !important; /* Slightly lighter dark shade for contrast */
        border-right: 2px solid #30363d;
        color: #c9d1d9;
    }
    .stSidebar .css-1d391kg, .stSidebar .css-pksc6u {
        color: #c9d1d9;
    }

    /* Info Boxes (used for instructions/welcome screen) */
    .info-box {
        background-color: #1f242c;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        border-left: 5px solid #58a6ff;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .info-box:hover {
        transform: translateY(-5px);
    }
    
    /* Metric Counter Style (used in the sidebar) */
    .metric-container {
        background-color: #232832;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-top: 15px;
        border: 2px solid #58a6ff;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.3);
    }
    .metric-container h3 {
        color: #c9d1d9;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    .metric-container h1 {
        color: #3fb950; /* Green for success metric */
        font-size: 3.5rem !important;
        margin: 0;
        line-height: 1;
    }
    
    /* Warning Box for Stop Stream */
    .warning-box {
        background-color: #2c211d;
        color: #ffb86c;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #ffb86c;
        margin-top: 20px;
    }
    
    /* Success Box for Active Mode */
    .stSuccess {
        background-color: #0e4429 !important;
        color: #3fb950 !important;
        border-color: #3fb950 !important;
        border-radius: 8px;
    }
    
</style>
""", unsafe_allow_html=True)

def setup_sidebar_ui():
    """Sets up the sidebar controls and returns the selected mode and run state."""
    st.sidebar.markdown("## ⚙️ Control Panel")
    st.sidebar.markdown("### Choose Your Workout")
    mode = st.sidebar.selectbox("Select Exercise Mode:", ["None", "Push Up", "Squat", "Curl Up", "Jumping Jack", "Tree Pose"], key="mode_select")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎥 Stream Control")
    run_button = st.sidebar.checkbox("Start Live Webcam Feed", key="webcam_toggle")
    st.sidebar.markdown("---")

    st.sidebar.markdown("### 📊 Live Repetition Count / Timer")
    counter_placeholder = st.sidebar.empty()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Guidance & Tips")
    st.sidebar.markdown("""
1. Select an exercise mode above.
2. Hit **'Start Live Webcam Feed'**.
3. Ensure your whole body is visible in the frame.
4. Let's get moving!
""")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛑 Shutdown")
    st.sidebar.markdown("- **Stop stream**: Uncheck the webcam box.")
    
    return mode, run_button, counter_placeholder

def display_welcome_screen(mode, run_button):
    """Displays the welcome screen with instructions when the app is not running."""
    if not run_button or mode == "None":
        if mode == "None":
            st.info("🎯 Please select an exercise mode in the **Control Panel** to begin your workout!")
        else:
            st.info("📹 Click the **'Start Live Webcam Feed'** checkbox to begin your exercise session!")
            
        st.markdown("## Get Ready to Train! Choose an Exercise on the Sidebar to Begin.")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 🏋️‍♂️ Exercise Form Guidelines")
            st.markdown("""
            <p style='color: #c9d1d9;'>
            **Push Ups**: 
            - Keep your core tight and body straight.
            - Lower until your elbows reach a 90° angle.
            </p>
            <p style='color: #c9d1d9;'>
            **Squats**:
            - Feet shoulder-width apart, chest up.
            - Lower your hips as if sitting in a chair (thighs parallel to floor).
            </p>
            <p style='color: #c9d1d9;'>
            **Tree Pose**:
            - Stand straight, bring one foot to the inner thigh of the opposite leg.
            - Raise your arms overhead, palms together.
            - Timer stops if arms or legs drop out of position.
            </p>
            <p style='color: #c9d1d9;'>
            **Jumping Jacks**:
            - Start standing tall with arms at sides.
            - Jump out, spreading arms and legs wide (arms above head).
            </p>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 📝 Camera Setup Tips")
            st.markdown("""
            <p style='color: #c9d1d9;'>
            1. **Good Lighting:** Ensure you are well-lit and not backlit.
            2. **Full Body View:** Position your camera to capture your entire body for accurate tracking.
            3. **Side View (recommended):** For exercises like Squats and Push Ups, a side profile is best.
            4. **Stable Camera:** Keep your device steady throughout the workout.
            </p>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

def update_counter_ui(mode, counter_placeholder):
    """Updates the live counter/timer in the sidebar."""
    
    counter_map = {
        "Push Up": ("Push Up Reps", st.session_state.pushup_counter),
        "Squat": ("Squat Reps", st.session_state.squat_counter),
        "Curl Up": ("Curl Up Reps", st.session_state.curlup_counter),
        "Jumping Jack": ("Jumping Jack Reps", st.session_state.jumpingjack_counter),
    }

    if mode in counter_map:
        title, count = counter_map[mode]
        counter_placeholder.markdown(
            f'<div class="metric-container">'
            f'<h3>{title}</h3>'
            f'<h1 style="font-size: 3.5rem; margin: 0; line-height: 1;">{count}</h1>'
            f'</div>', unsafe_allow_html=True
        )
    
    elif mode == "Tree Pose":
        # UPDATED: Use the duration directly from session state
        duration = st.session_state.get('tree_pose_hold_duration', 0.0)
        
        # Convert total seconds (duration is now a float) into MM:SS format
        seconds_total = int(duration)
        minutes = seconds_total // 60
        seconds_display = seconds_total % 60
        timer_display = f"{minutes:02}:{seconds_display:02}"
        
        counter_placeholder.markdown(
            f'<div class="metric-container">'
            f'<h3>Tree Pose Hold Time</h3>'
            f'<h1 style="font-size: 3.5rem; margin: 0; line-height: 1; color: #ffb86c;">{timer_display}</h1>'
            f'</div>', unsafe_allow_html=True
        )


def display_stop_message():
    """Displays the message when the webcam is stopped."""
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.warning("Webcam stopped. Great job! Select 'Start Live Webcam Feed' to resume your workout.")
    st.markdown('</div>', unsafe_allow_html=True)
