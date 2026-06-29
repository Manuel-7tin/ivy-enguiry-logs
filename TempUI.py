import streamlit as st
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Form / Voice Toggle", layout="centered")

# Initialize session state
if "mode" not in st.session_state:
    st.session_state.mode = "Form"


# Toggle button
col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🔄 Toggle"):
        if st.session_state.mode == "Form":
            st.session_state.mode = "Voice"
        else:
            st.session_state.mode = "Form"

st.title("Input Interface")

st.write(f"### Current Mode: {st.session_state.mode}")

# -----------------------
# FORM INTERFACE
# -----------------------
if st.session_state.mode == "Form":

    with st.form("user_form"):

        name = st.text_input("Name")
        email = st.text_input("Email")
        message = st.text_area("Message")

        submitted = st.form_submit_button("Submit")

        if submitted:
            st.success("Form Submitted!")
            st.write({
                "Name": name,
                "Email": email,
                "Message": message
            })


# -----------------------
# VOICE INTERFACE
# -----------------------
else:

    st.subheader("Voice Recorder")

    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop Recording",
        key="voice_recorder",
        use_container_width=True,
    )

    if audio:

        st.success("Recording Captured!")

        st.audio(audio["bytes"], format="audio/wav")

        st.download_button(
            "Download Recording",
            data=audio["bytes"],
            file_name="recording.wav",
            mime="audio/wav",
        )