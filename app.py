"""
==========================================================
IVY LEAGUE ASSOCIATES
Customer Enquiry Application

Author:
Description:
    Internal customer enquiry system.

NOTE:
Backend functions currently contain mock implementations.
Replace them with real API/database calls later.
==========================================================
"""
from fileinput import filename
# ==========================================================
# IMPORTS
# ==========================================================

from pathlib import Path
from datetime import date, datetime
import re
import io
import os
import boto3
import time
import uuid
import json
from json import JSONDecodeError

import streamlit as st
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from botocore.exceptions import NoCredentialsError


load_dotenv()
# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Ivy League Associates",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))

def submission_is_valid():
    """
    Returns True if every required field
    has been completed.
    """

    return len(
        get_missing_fields(
            st.session_state.submission_data
        )
    ) == 0

# ==========================================================
# LOAD CSS
# ==========================================================

def load_css():
    """
    Load the external stylesheet.
    """

    css = Path("style.css")

    if css.exists():

        st.markdown(
            f"<style>{css.read_text()}</style>",
            unsafe_allow_html=True
        )


load_css()


# ==========================================================
# SESSION STATE INITIALIZATION
# ==========================================================

DEFAULT_SESSION = {

    "page": "home",

    "mode": None,

    "redirect": False,

    "processing": False,

    "audio_file": None,

    "missing_fields": [],

    "submission_id": None,

    "error_message": None,

    "submission_data": {

        "staff_name": "",

        "customer_name": "",

        "mode_of_reaching_out": "",

        "phone": "",

        "email": "",

        "other_contact": "",

        "enquiry_date": date.today(),

        "customer_interest": "",

        "nature_of_enquiry": "",

        "status": "New",

        "follow_up_action": "No Follow-up Required"

    }

}


for key, value in DEFAULT_SESSION.items():

    if key not in st.session_state:

        st.session_state[key] = value



card_class = (
    "glass selected-card"
    if st.session_state.mode == "voice"
    else "glass"
)

REQUIRED_FIELDS = {

    "staff_name": "Staff Name",

    "customer_name": "Customer Full Name",

    "enquiry_date": "Date of Enquiry",

    "mode_of_reaching_out": "Mode of contact",

    "customer_interest": "Customer Interest",

    "nature_of_enquiry": "Nature of Enquiry",

    "status": "Status"

}
# ==========================================================
# PLACEHOLDER BACKEND
# ==========================================================

def download_enquiries():
    """
    Downloads all saved enquiries.
    """

    file_name = "IvyCrmEnquiry.xlsx"
    bucket_name = 'crm-enquiries-670422575422-eu-north-1-an'
    file_stream = io.BytesIO()
    s3.download_fileobj(bucket_name, file_name, file_stream)
    file_stream.seek(0)
    return file_stream


def upload_audio(audio):
    """
    Upload audio.

    Returns
    -------
    dict
    """
    return {

        "success": True,

        "audio_id": str(uuid.uuid4())

    }


def generate_presigned_url(file):
    """
    Placeholder.

    Replace with cloud storage implementation.
    """

    return "https://example.com/mock-file"


def parse_audio(audio):
    """
    Extract information from speech.

    Replace with Whisper or another speech model.
    """


    client = Groq()

    transcription = client.audio.transcriptions.create(
        file=("audio.wav", st.session_state.audio_file["bytes"]),
        model="whisper-large-v3-turbo",
        temperature=0,
        response_format="verbose_json",
    )
    print(transcription.text)

    # message = "This is lucky, i just spoke to EmmanuelEbi-Fredrick, he called to find out what our lecture plan is like, his email is oled@gmail.com and i have plans to send him a file later"
    with open("prompt.txt", mode="r") as f:
        prompt = f.read()
    prompt = prompt.replace("{TRANSCRIPT}", transcription.text)
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
    )
    response = ""
    for i, chunk in enumerate(completion):
        response += chunk.choices[0].delta.content or ""
    response = None if response == "" else response
    try:
        return json.loads(response)
    except JSONDecodeError:
        print("DecodeError", response)
        return {"failed": response}


def save_enquiry(data = st.session_state.submission_data):
    """
    Save an enquiry.
    """

    return False, "#####"

    file_name = "IvyCrmEnquiry.xlsx"
    bucket_name = 'crm-enquiries-670422575422-eu-north-1-an'
    file_stream = io.BytesIO()
    s3.download_fileobj(bucket_name, file_name, file_stream)
    file_stream.seek(0)

    id_ = datetime.now().strftime("%Y%m%d%H:%M")
    new_row = {
        "Submission ID": id_,
        "Staff": data.get("staff_name"),
        "Date of Enquiry": data.get("enquiry_date"),
        "Full Name": data.get("customer_name"),
        "How did the student reach out": data.get("mode_of_reaching_out"),
        "Phone number": data.get("phone"),
        "Email": data.get("email"),
        "Other contact details e.g. SM page": data.get("other_contact"),
        "Interested in?": data.get("customer_interest"),
        "Nature of enquiries": data.get("nature_of_enquiry"),
        "Status": data.get("status"),
        "Follow up action required": data.get("follow_up_action")
    }

    try:
        df = pd.read_excel(file_stream)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        updated_file = io.BytesIO()
        with pd.ExcelWriter(updated_file, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        updated_file.seek(0)
        s3.upload_fileobj(updated_file, bucket_name, file_name)
    except NoCredentialsError:
        return False, "#####"
    except Exception as e:
        return False, "00000"
    else:
        return True, id_
    # return {
    #
    #     "success": True,
    #
    #     "submission_id":
    #         f"IVY-{uuid.uuid4().hex[:8].upper()}"
    #
    # }


# ==========================================================
# VALIDATION HELPERS
# ==========================================================

EMAIL_REGEX = re.compile(

    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

)


PHONE_REGEX = re.compile(

    r"^\+?[0-9]{7,15}$"

)


def validate_email(email):
    """
    Validate email format.
    """

    if not email:

        return True

    return bool(

        EMAIL_REGEX.match(email.strip())

    )


def validate_phone(phone):
    """
    Validate phone number.
    """

    if not phone:

        return True

    cleaned = (

        phone

        .replace(" ", "")

        .replace("-", "")

    )

    return bool(

        PHONE_REGEX.match(cleaned)

    )


def contact_information_valid(
    phone,
    email
):
    """
    Customer must provide either
    phone OR email.
    """

    if not phone and not email:

        return False

    if email and not validate_email(email):

        return False

    if phone and not validate_phone(phone):

        return False

    return True


def required_fields_complete(data= st.session_state.submission_data):
    """
    Checks mandatory fields.
    """
    missing = get_missing_fields(data)
    errors = [f"{field} is required" for field in missing] # if str(data.get(field, "")).strip() == ""]
    # errors += ["Phone or Email is required"] if not (data.get("phone") or data.get("email")) else []
    return len(errors) == 0, errors


# ==========================================================
# NAVIGATION HELPERS
# ==========================================================

def navigate(page):
    """
    Navigate to another screen.
    """

    st.session_state.page = page
    print("navigatiing to", st.session_state.page)

    st.rerun()


def reset_submission():
    """
    Reset the current submission.
    """

    st.session_state.mode = None

    st.session_state.processing = False

    st.session_state.audio_file = None

    st.session_state.missing_fields = []

    st.session_state.error_message = None

    st.session_state.submission_id = None

    st.session_state.submission_data = {

        "staff_name": "",

        "customer_name": "",

        "mode_of_reaching_out": "",

        "phone": "",

        "email": "",

        "other_contact": "",

        "enquiry_date": date.today(),

        "customer_interest": "",

        "nature_of_enquiry": "",

        "status": "New",

        "follow_up_action": "No Follow-up Required"

    }


def start_new_submission():
    """
    Prepare a brand-new enquiry.
    """

    reset_submission()

    navigate("mode")


# ==========================================================
# PAGE LAYOUT HELPERS
# ==========================================================

def page_container():
    """
    Apply a consistent width to every page.
    """

    st.markdown(
        """
        <style>

        .block-container{

            max-width:1150px;

            padding-top:2rem;

            padding-bottom:2rem;

        }

        </style>
        """,
        unsafe_allow_html=True
    )


page_container()


# ==========================================================
# UI COMPONENTS
# ==========================================================


def background():

    st.markdown(
        """
        <div class="background-blur blob1"></div>
        <div class="background-blur blob2"></div>
        """,
        unsafe_allow_html=True
    )

def company_logo():

    st.image(
        "assets/logo.jpeg",
        width=140
    )


def hero(
    title,
    subtitle,
    signature=""
):
    st.markdown(
        f"""
        <h1 style="text-align:center;" class="hero-title hero-gradient">
            {title}
        </h1>

        <p style="
            text-align:center;
            max-width:700px;
            margin:auto;
            font-size:18px;
        ">
            {subtitle}
        </p>

        <p class="signature" style="text-align:center;">
            {signature}
        </p>
        """,
        unsafe_allow_html=True
    )


# def glass_card_start():
#
#
#     st.markdown(
#         """
#         <div class="card_class">
#         """,
#         unsafe_allow_html=True
#     )
#
#
# def glass_card_end():
#
#     st.markdown(
#         """
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

# def section_header(title, icon=""):
#     st.header(f"{icon} {title}")
def section_header(
    title,
    icon=""
):

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:12px;
            margin-top:25px;
            margin-bottom:10px;
        ">

        <span style="
            font-size:26px;
        ">
            {icon}
        </span>

        <h3 style="
            margin:0;
        ">
            {title}
        </h3>

        </div>
        """,
        unsafe_allow_html=True
    )


def divider():

    st.markdown(
        '<div class="divider"></div>',
        unsafe_allow_html=True
    )


def badge(text):

    st.markdown(
        f"""
        <span class="badge">
            {text}
        </span>
        """,
        unsafe_allow_html=True
    )


def loader(text="Processing..."):

    st.markdown(
        f"""
        <div style="text-align:center;padding:40px;">

            <div class="loader"></div>

            <br>

            <h4>{text}</h4>

        </div>
        """,
        unsafe_allow_html=True
    )


def microphone():

    st.markdown(
        """
        <div style="text-align:center;">

            <div class="pulse"></div>

            <br>

            <h4>Listening...</h4>

        </div>
        """,
        unsafe_allow_html=True
    )


def status_message(
    title,
    message,
    success=True
):

    css = "success-card" if success else "error-card"

    st.markdown(
        f"""
        <div class="{css}">

        <h2>{title}</h2>

        <p>{message}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

def footer():

    st.markdown(
        """
        <div class="footer">

            © 2026 Ivy League Associates

        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# HOME SCREEN
# ==========================================================

def home_screen():

    background()

    st.markdown("<br>", unsafe_allow_html=True)

    top_left, center, top_right = st.columns([1, 2, 1])

    with center:

        # company_logo()

        hero(
            title="Ivy League Associates",
            subtitle=(
                "Intelligent Customer Enquiry Platform"
            ),
            signature=(
                "Excellence begins with every conversation."
            )
        )

        st.markdown(
            """
            <div class="glass">

            <h3 style="margin-top:0;">
                Welcome
            </h3>

            <p>
            Capture customer enquiries effortlessly using
            voice or traditional forms. Designed to help
            your team record interactions consistently,
            professionally and efficiently.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🚀 Start Filling",
            use_container_width=True,
            type="primary"
        ):
            navigate("mode")

    with col2:

        if st.button(
            "📥 Download Filled Enquiries",
            use_container_width=True
        ):
            navigate("download")
        # enquiries = download_enquiries

        # st.download_button(
        #     "📥 Download Filled Enquiries",
        #     download_enquiries(),
        #     "enquiries.xlsx",
        #     "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        #     use_container_width=True
        # )

    st.write("")
    divider()

    section_header(
        "Why Teams Love This Tool",
        "✨"
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            """
            <div class="feature-card">

            <h2>🎤</h2>

            <h3>Voice First</h3>

            <p>
            Record enquiries naturally and let AI
            extract the important information.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            """
            <div class="feature-card">

            <h2>🧠</h2>

            <h3>Smart Extraction</h3>

            <p>
            Only missing information is requested,
            reducing manual work significantly.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            """
            <div class="feature-card">

            <h2>⚡</h2>

            <h3>Efficient Workflow</h3>

            <p>
            Capture, review and submit enquiries
            within seconds.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    divider()

    st.markdown(
        """
        <div style="text-align:center;">

        <h3 style="margin-bottom:0;">
        Excellence Begins Here
        </h3>

        <p style="font-style:italic;">
        Every customer interaction is an opportunity
        to build lasting relationships.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    footer()


# ==========================================================
# PLACEHOLDER SCREENS
# ==========================================================

# ==========================================================
# MODE SELECTION
# ==========================================================

def mode_selection():
    """
    Allow the user to choose how they want
    to submit the enquiry.
    """

    background()

    company_logo()

    hero(
        title="Choose Your Preferred Mode",
        subtitle=(
            "Select the method you would like to use "
            "to capture the customer enquiry."
        ),
        signature=""
    )

    st.write("")
    st.write("")

    if st.session_state.mode is None:
        badge("No mode selected")
    else:
        badge(f"Selected: {st.session_state.mode.title()} Mode")

    st.write("")

    voice_col, form_col = st.columns(2)

    # -------------------------------------------------
    # Voice Mode
    # -------------------------------------------------

    with voice_col:

        st.markdown(
            """
            <div class="glass">

            <h3>🎤 Voice Mode</h3>

            <p>
            Record the customer's enquiry naturally.
            The application will automatically extract
            the relevant information and ask only for
            anything that is missing.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Select Voice Mode",
            use_container_width=True,
            type="primary" if st.session_state.mode == "voice" else "secondary"
        ):

            st.session_state.mode = "voice"

    # -------------------------------------------------
    # Form Mode
    # -------------------------------------------------

    with form_col:

        st.markdown(
            """
            <div class="glass">

            <h3>📝 Form Mode</h3>

            <p>
            Complete the enquiry form manually, 
            one section at a time, with full control 
            over every field, allowing you to review, 
            customize, and enter each detail exactly 
            as required.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Select Form Mode",
            use_container_width=True,
            type="primary" if st.session_state.mode == "form" else "secondary"
        ):

            st.session_state.mode = "form"

    st.write("")
    divider()

    left, middle, right = st.columns([1, 2, 1])

    with left:

        if st.button(
            "⬅ Home",
            use_container_width=True
        ):

            navigate("home")

    with right:

        proceed_disabled = st.session_state.mode is None
        print("Mode is", st.session_state.mode)

        if st.button(
            "Continue ➜",
            disabled=proceed_disabled,
            use_container_width=True
        ):

            if st.session_state.mode == "voice":
                navigate("voice")

            elif st.session_state.mode == "form":
                navigate("form")

    footer()

# ==========================================================
# MISSING FIELD DETECTION
# ==========================================================


def get_missing_fields(data):
    """
    Return a list of required fields
    that are missing.
    """

    missing = []

    for key, desc in REQUIRED_FIELDS.items():

        value = str(
            data.get(key, "") or ""
        ).strip()

        if not value:
            missing.append(desc)

    # Phone OR Email
    phone = (data.get("phone", "") or "").strip()

    email = (data.get("email", "") or "").strip()

    if not phone and not email:
        missing.append("Phone or Email")

    return missing

def employee_section():
    """
    Employee Information
    """

    section_header(
        "Employee Information",
        "👤"
    )

    data = st.session_state.submission_data

    data["staff_name"] = st.text_input(
        "Staff Name *",
        value=data["staff_name"],
        placeholder="Enter your full name"
    )

def customer_section():
    """
    Customer Information
    """

    section_header(
        "Customer Information",
        "🤝"
    )

    data = st.session_state.submission_data

    data["customer_name"] = st.text_input(
        "Customer Full Name *",
        value=data["customer_name"]
    )

    contact_modes = [

        "Phone Call",

        "Email",

        "WhatsApp",

        "Walk-in",

        "Referral",

        "Website",

        "Social Media",

        "Other"

    ]

    current = data["mode_of_reaching_out"]

    if current not in contact_modes:
        current = contact_modes[0]

    data["mode_of_reaching_out"] = st.selectbox(

        "Mode of Reaching Out",

        contact_modes,

        index=contact_modes.index(current)

    )

    left, right = st.columns(2)

    with left:

        data["phone"] = st.text_input(

            "Phone Number",

            value=data["phone"]

        )

    with right:

        data["email"] = st.text_input(

            "Email Address",

            value=data["email"]

        )

    data["other_contact"] = st.text_area(

        "Other Contact Details",

        value=data["other_contact"],

        height=80

    )

def enquiry_section():
    """
    Enquiry Information
    """

    section_header(
        "Enquiry Information",
        "📝"
    )

    data = st.session_state.submission_data

    data["enquiry_date"] = st.date_input(

        "Enquiry Date",

        value=data["enquiry_date"]

    )

    data["customer_interest"] = st.text_area(

        "Customer Interest *",

        value=data["customer_interest"],

        height=120

    )

    data["nature_of_enquiry"] = st.text_area(

        "Nature of Enquiry *",

        value=data["nature_of_enquiry"],

        height=150

    )

    statuses = [

        "New",

        "Pending",

        "In Progress",

        "Escalated",

        "Resolved",

        "Closed"

    ]

    current = data["status"]

    if current not in statuses:
        current = "New"

    data["status"] = st.selectbox(

        "Status",

        statuses,

        index=statuses.index(current)

    )

def followup_section():
    """
    Follow-up
    """

    section_header(
        "Follow-up",
        "📅"
    )

    data = st.session_state.submission_data

    actions = [

        "No Follow-up Required",

        "Call Customer",

        "Send Email",

        "Schedule Meeting",

        "Escalate",

        "Await Customer Response",

        "Other"

    ]

    current = data["follow_up_action"]

    if current not in actions:
        current = actions[0]

    data["follow_up_action"] = st.selectbox(

        "Follow-up Action",

        actions,

        index=actions.index(current)

    )

# ==========================================================
# VOICE MODE
# ==========================================================

def voice_mode():
    st.session_state.audio_file = None

    background()

    company_logo()

    hero(
        title="Voice Mode",
        subtitle="Record the customer's enquiry naturally.",
        signature=""
    )

    badge("Voice Recording")

    divider()

    st.markdown(
        """
        <div class="glass">

        <h3>🎤 Record Customer Enquiry</h3>

        <p>
        Speak clearly and naturally.
        The system will extract the
        relevant information automatically.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    audio = mic_recorder(

        start_prompt="🎙 Start Recording",

        stop_prompt="⏹ Stop Recording",

        just_once=True,

        use_container_width=True,

        key="voice_recorder"

    )

    if audio:

        st.session_state.audio_file = audio

    # -------------------------------------------------
    # Audio Preview
    # -------------------------------------------------

    if st.session_state.audio_file:

        st.success("Recording captured successfully.")

        st.audio(

            st.session_state.audio_file["bytes"],

            format="audio/wav"

        )

        st.download_button(

            "⬇ Download Recording",

            data=st.session_state.audio_file["bytes"],

            file_name="customer_enquiry.wav",

            mime="audio/wav",

            use_container_width=True

        )

        st.write("")

        if st.button(

            "✨ Process Recording",

            use_container_width=True

        ):

            st.session_state.processing = True

            # st.rerun()

    # -------------------------------------------------
    # Processing
    # -------------------------------------------------

            with st.status(
                    "🎤 Processing Recording...",
                    expanded=True
            ) as status:

                st.write("⬆ Uploading recording...")

                upload_audio(
                    st.session_state.audio_file
                )

                st.write("🧠 Extracting enquiry details...")

                parsed = parse_audio(
                    st.session_state.audio_file
                )

                for key, value in parsed.items():

                    if key in st.session_state.submission_data:
                        st.session_state.submission_data[key] = value

                st.write("🔎 Detecting missing fields...")

                st.session_state.missing_fields = get_missing_fields(
                    st.session_state.submission_data
                )


                status.update(

                    label="✅ Recording Processed",

                    state="complete"

                )
        # st.session_state.processing = False

            st.success(
                "Recording processed successfully!"
            )

            # -------------------------------------------------
            # Missing Fields
            # -------------------------------------------------

            if st.session_state.missing_fields:
                # divider()
                st.session_state.redirect = True
                navigate("form")
            else:
                result = save_enquiry()
                if result[0]:
                    st.session_state.submission_id = result[1]
                    navigate("success")
                else:
                    navigate("failure")
                # navigate("success")


        # if "staff_name" in st.session_state.missing_fields:
        #     data["staff_name"] = st.text_input(
        #         "Staff Name *",
        #         value=data["staff_name"]
        #     )
        #
        # if "customer_name" in st.session_state.missing_fields:
        #     data["customer_name"] = st.text_input(
        #         "Customer Full Name *",
        #         value=data["customer_name"]
        #     )
        #
        # if "customer_interest" in st.session_state.missing_fields:
        #     data["customer_interest"] = st.text_area(
        #         "Customer Interest *",
        #         value=data["customer_interest"]
        #     )
        #
        # if "nature_of_enquiry" in st.session_state.missing_fields:
        #     data["nature_of_enquiry"] = st.text_area(
        #         "Nature of Enquiry *",
        #         value=data["nature_of_enquiry"]
        #     )
        #
        # if "status" in st.session_state.missing_fields:
        #
        #     options = [
        #
        #         "New",
        #
        #         "Pending",
        #
        #         "In Progress",
        #
        #         "Escalated",
        #
        #         "Resolved",
        #
        #         "Closed"
        #
        #     ]
        #
        #     current = data["status"]
        #
        #     if current not in options:
        #         current = "New"
        #
        #     data["status"] = st.selectbox(
        #
        #         "Status",
        #
        #         options,
        #
        #         index=options.index(current)
        #
        #     )
        #
        # if "contact" in st.session_state.missing_fields:
        #     phone_col, email_col = st.columns(2)
        #
        #     with phone_col:
        #         data["phone"] = st.text_input(
        #
        #             "Phone Number"
        #
        #         )
        #
        #     with email_col:
        #         data["email"] = st.text_input(
        #
        #             "Email Address"
        #
        #         )

    divider()

    can_continue = submission_is_valid()

    left, right = st.columns(2)

    with left:

        if st.button(
                "⬅ Back",
                use_container_width=True
        ):
            navigate("mode")

    with right:

        if st.button(
                "Proceed ➜",
                disabled=not can_continue,
                use_container_width=True
        ):

            response = save_enquiry(
                st.session_state.submission_data
            )

            if response["success"]:

                st.session_state.submission_id = (
                    response["submission_id"]
                )

                navigate("success")

            else:
                navigate("failure")


def form_mode():
    """
    Placeholder Form Mode page.
    """

    background()

    company_logo()
    if st.session_state.redirect:
        section_header(
            "Additional Information Required",
            "⚠️"
        )

        st.info(
            "We extracted most of the enquiry automatically. "
            "Please complete the remaining fields below."
        )
    else:
        hero(
            title="Form Mode",
            subtitle="Fill in the enquiry manually.",
            signature=""
        )
    employee_section()

    divider()

    customer_section()

    divider()

    enquiry_section()

    divider()

    followup_section()

    divider()

    data = st.session_state.submission_data
    is_valid, errors = required_fields_complete()
    if is_valid and contact_information_valid(data.get("phone", "08169957942"), data.get("email", "eguio@gmail.com")):
        pass
    else:
        is_valid = False
        errors.append("Ensure the email and/or phone number is valid!")

    if errors:
        st.warning("Please resolve the following issues:")

        for error in errors:
            st.write(f"• {error}")

    if st.button(
        "💾 Submit",
        disabled=not is_valid,
        use_container_width=True,
    ):
        result = save_enquiry()
        st.session_state.redirect = False
        if result[0]:
            st.session_state.submission_id = result[1]
            navigate("success")
            # st.session_state.page = "success"
            # st.rerun()
        else:
            navigate("failure")
            # st.session_state.page = "failure"
            # st.rerun()

    # validation_panel()

#     form_actions()
    divider()
    if st.button(
        "⬅ Back",
        use_container_width=True
    ):
        st.session_state.redirect = False
        navigate("mode")


def download_page():
    background()
    company_logo()

    hero(
        title="Download Centre",
        subtitle=(
            "Generate and download previously "
            "submitted customer enquiries."
        ),
        signature=""
    )

    divider()

    st.info(
        "Preparing your enquiries..."
    )

    with st.status(
        "Loading enquiries...",
        expanded=True
    ) as status:
        st.write("Retrieving submissions...")
        enquiries = download_enquiries()
        st.write("Preparing Excel file...")
        status.update(
            label="Ready",
            state="complete"
        )

    st.success(
        "Your file is ready."
    )

    st.download_button(
        "⬇ Download Enquiries",
        enquiries,
        "customer_enquiries.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary"
    )
    st.write("")
    left, right = st.columns(2)

    with left:
        if st.button(
            "🏠 Return Home",
            use_container_width=True
        ):
            navigate("home")

    with right:
        if st.button(
            "➕ New Submission",
            use_container_width=True
        ):
            reset_submission()
            navigate("mode")


def success_page():

    background()

    st.balloons()

    company_logo()

    hero(

        "Submission Successful",

        "The enquiry has been saved successfully.",

        ""

    )

    status_message(

        "Success",

        "Thank you. The enquiry has been recorded.",

        success=True

    )

    divider()

    section_header(

        "Submission Summary",

        "📄"

    )

    data = st.session_state.submission_data

    st.markdown(

        f"""
**Submission ID**

`{st.session_state.submission_id}`

---

**Staff**

{data["staff_name"]}

**Customer**

{data["customer_name"]}

**Status**

{data["status"]}

**Interest**

{data["customer_interest"]}

""")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(

            "🏠 Return Home",

            use_container_width=True

        ):

            reset_submission()

            navigate("home")

    with col2:

        if st.button(

            "➕ New Submission",

            use_container_width=True

        ):

            start_new_submission()


def failure_page():

    background()

    company_logo()

    hero(

        "Submission Failed",

        "Something went wrong while saving your enquiry.",

        ""

    )

    status_message(

        "Submission Failed",

        "Please try again or contact the developer.",

        success=False

    )

    divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(

            "🔄 Retry",

            use_container_width=True

        ):

            navigate(st.session_state.mode)

    with col2:

        if st.button(

            "🏠 Return Home",

            use_container_width=True

        ):

            reset_submission()

            navigate("home")

    st.link_button(

        "📧 Contact Developer",

        "mailto:developer@ivyleagueassociates.com",

        use_container_width=True

    )

if st.session_state.page == "home":
    home_screen()
elif st.session_state.page == "voice":
    voice_mode()
elif st.session_state.page == "form":
    form_mode()
elif st.session_state.page == "mode":
    mode_selection()
elif st.session_state.page == "success":
    success_page()
elif st.session_state.page == "failure":
    failure_page()
elif st.session_state.page == "download":
    download_page()