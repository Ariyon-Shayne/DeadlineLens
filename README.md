# 📅 DeadlineLens — AI Deadline & Task Extractor

DeadlineLens is a Streamlit application that uses **Gemini Vision + chat**
to turn photos of real-world documents into structured deadlines, tasks,
priorities, and action items.

## Features

- 📸 Upload notices, assignment sheets, exam timetables, posters, etc.
- 👁️ Gemini Vision extracts dates and tasks from images.
- 💬 Chat with the document using follow-up questions.
- 🔴 Assigns practical task priorities.
- 📧 Sends a complete deadline digest by Gmail.
- 🔐 Secrets are kept outside Git with Streamlit secrets.

## Project structure

```text
DeadlineLens/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml
```

## 1. Get a Gemini API key

Create a Gemini API key through Google AI Studio.

## 2. Configure Gmail

The app uses Gmail SMTP.

On the Gmail account used to SEND messages:

1. Enable 2-Step Verification.
2. Create an App Password.
3. Use the 16-character App Password, not your normal Gmail password.

## 3. Create secrets


```text
.streamlit/secrets.toml
```

Then fill in:

```toml
GEMINI_API_KEY = "..."
GMAIL_ADDRESS = "..."
GMAIL_APP_PASSWORD = "..."
```

Never upload the real `secrets.toml` to GitHub.

## 4. Install

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Run

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, normally:

```text
http://localhost:8501
```

## Example documents

Try uploading:

- College assignment notice
- Exam timetable
- Internship poster
- Scholarship notice
- Event poster
- Project submission notice

Then ask:

> What is the earliest deadline?

or:

> What documents do I need?

or:

> Give me a 3-step action plan.

## Deployment

The app can be deployed on Streamlit Community Cloud.

Push the project to GitHub, create a Streamlit app using `app.py`,
and add the same values from your local `secrets.toml` in the deployment
Secrets settings.

## Security

Do not commit:

```text
.streamlit/secrets.toml
```

Only commit:

```text
.streamlit/secrets.toml.example
```
