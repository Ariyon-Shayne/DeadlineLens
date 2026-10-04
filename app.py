import json
import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)

st.set_page_config(
    page_title="DeadlineLens",
    page_icon="📅",
    layout="centered",
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")

MODEL_NAME = "gemini-2.5-flash"


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append(
        {"role": role, "kind": kind, "content": content}
    )


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"


def clean_email_text(text):
    if not text:
        return "No deadline summary available."
    return text.strip()


def send_email(to_address, subject, body):
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        return False, "Gmail credentials are missing in Streamlit secrets."

    if not to_address.strip():
        return False, "Recipient email is missing."

    try:
        message = MIMEText(body, "plain", "utf-8")
        message["Subject"] = subject
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address.strip()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(message)

        return True, "Email sent successfully."
    except Exception as error:
        return False, str(error)


# -------------------------
# Onboarding
# -------------------------
if "onboarded" not in st.session_state:
    st.title("📅 DeadlineLens")
    st.caption("Snap it. Extract it. Act on it.")

    st.markdown(
        """
        **Turn photos of notices, timetables, assignments and documents
        into a clear list of deadlines and tasks.**
        """
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your name", placeholder="Aryan")
        email = st.text_input(
            "Email address for your deadline digest",
            placeholder="you@example.com",
        )

        submitted = st.form_submit_button("Let's go 🚀")

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please fill in both your name and email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()

            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                ),
            )

            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# -------------------------
# Main interface
# -------------------------
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("📅 DeadlineLens")
    st.caption(
        f"Logged in as {st.session_state.name} · digest → {st.session_state.email}"
    )

with button_col:
    send_disabled = len(st.session_state.messages) <= 1

    if st.button(
        "📧 Send Digest",
        disabled=send_disabled,
        use_container_width=True,
    ):
        with st.spinner("Building your deadline digest..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        success, info = send_email(
            st.session_state.email,
            "📅 Your DeadlineLens Digest",
            clean_email_text(summary),
        )

        if success:
            st.success("Digest sent! Check your email 📧")
        else:
            st.error(f"Couldn't send the digest: {info}")


# -------------------------
# Chat history
# -------------------------
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )

for message in st.session_state.messages:
    render_message(message)


# -------------------------
# Input: text + images
# -------------------------
user_input = st.chat_input(
    "Ask about a deadline, or attach a notice/photo",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text

    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            """
            Analyze this image as a deadline/task document.
            Extract every useful deadline, date, task, requirement,
            and action item you can identify.
            """
        )

    with st.spinner("Reading the document with Gemini Vision..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
    st.rerun()
