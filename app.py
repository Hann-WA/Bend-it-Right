import time

import av
import streamlit as st
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer

from ui import apply_custom_css, setup_sidebar_ui, display_welcome_screen, update_counter_ui
from exercise import RepCounter, process_frame_and_count, mp_pose

# ---------- Configuration and Setup ----------
st.set_page_config(page_title="Bend It Right - Your Personal Trainer", layout="wide", page_icon="💪")
apply_custom_css() # Apply custom aesthetics

# Main Header
st.markdown("<h1><span style='color: #3fb950;'>Bend It Right</span> - Live Exercise Tracker 💪</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------- Session State Initialization (Streamlit Standard) ----------
# One RepCounter per browser session; it keeps counts across stream stop/start.
if "rep_counter" not in st.session_state:
    st.session_state.rep_counter = RepCounter()


def get_rtc_configuration():
    """ICE servers used to connect the visitor's browser to the server.

    A public STUN server is enough on most networks. If video fails to connect
    once hosted (strict firewalls / mobile networks), add a TURN server in
    .streamlit/secrets.toml (or the host's secrets settings), e.g.:

        [[ice_servers]]
        urls = ["turn:your.turn.server:3478"]
        username = "..."
        credential = "..."
    """
    ice_servers = [{"urls": ["stun:stun.l.google.com:19302"]}]
    try:
        if "ice_servers" in st.secrets:
            ice_servers += [dict(server) for server in st.secrets["ice_servers"]]
    except Exception:
        pass  # No secrets file: STUN only.
    return {"iceServers": ice_servers}


class PoseProcessor(VideoProcessorBase):
    """Runs pose detection on each frame from the browser webcam.

    streamlit-webrtc calls recv() on a background thread, so this class must not
    touch st.* APIs. The active mode is set from the script thread.
    """

    def __init__(self, counter):
        self.counter = counter
        self.mode = "None"
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        image = process_frame_and_count(image, self.mode, self.pose, self.counter)
        return av.VideoFrame.from_ndarray(image, format="bgr24")

    def on_ended(self):
        self.pose.close()


def main():
    """Orchestrates the application flow."""
    mode, counter_placeholder = setup_sidebar_ui()
    counter = st.session_state.rep_counter

    # Display welcome/instructions until an exercise is chosen
    if mode == "None":
        display_welcome_screen(mode)
        return

    update_counter_ui(mode, counter_placeholder, counter.get(mode))

    ctx = webrtc_streamer(
        key="bend-it-right",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=get_rtc_configuration(),
        video_processor_factory=lambda: PoseProcessor(counter),
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if ctx.video_processor:
        ctx.video_processor.mode = mode

    if not ctx.state.playing:
        st.info("📹 Click **START** above and allow camera access to begin your exercise session!")
        return

    st.success(f"🔥 **Workout Active**: **{mode}** Mode is counting your reps!")

    # Keep the sidebar counter in sync while the stream runs. Streamlit stops
    # this loop automatically when the user changes a widget or hits STOP.
    while ctx.state.playing:
        update_counter_ui(mode, counter_placeholder, counter.get(mode))
        time.sleep(0.25)


if __name__ == "__main__":
    main()
