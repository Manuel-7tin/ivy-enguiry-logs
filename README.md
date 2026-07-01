# Ivy League Associates Customer Enquiry Platform

A modern internal application for capturing, reviewing, and managing customer enquiries through either structured forms or AI-assisted voice input.

Built with **Python** and **Streamlit**, the platform was designed to replace manual enquiry capture with a streamlined workflow that emphasizes usability, consistency, and future scalability.

---

## Overview

The Customer Enquiry Platform enables staff members to record customer enquiries efficiently using either a traditional form or voice recording.

When voice mode is used, the application processes the recording, extracts relevant information, and presents the results in a reviewable form. Employees can verify, edit, or complete the extracted information before submitting the enquiry.

The application is intentionally frontend-focused. Backend services are currently represented by placeholder implementations, making the interface fully functional while remaining ready for integration with production APIs and databases.

---

## Key Features

### Dual Submission Modes

Choose between two methods of capturing enquiries:

* **Voice Mode** – Record a conversation, process the audio, review the extracted information, and complete any remaining fields before submission.
* **Form Mode** – Capture enquiries manually using a structured multi-section form.

---

### AI-Assisted Voice Workflow

Voice submissions are designed as a review process rather than a blind automation.

After audio processing:

* extracted values are automatically populated,
* missing information remains empty,
* users can review every field,
* corrections can be made before submission.

This approach combines automation with human verification to improve accuracy.

---

### Structured Enquiry Form

The manual form is divided into logical sections to improve readability and reduce cognitive load:

* Employee Information
* Customer Information
* Enquiry Information
* Follow-up Details

Related information is grouped together, making the interface easier to complete and maintain.

---

### Smart Validation

Validation occurs before submission to ensure enquiry quality.

The application validates:

* required fields
* email addresses
* phone numbers
* mandatory contact information
* overall form completeness

Users are prevented from proceeding until the required information has been provided.

---

### Download Centre

Previously submitted enquiries can be downloaded from a dedicated Download Centre.

Moving this functionality away from the home page prevents unnecessary loading during normal navigation while providing a focused workflow for exporting enquiry data.

---

### Session-Based Navigation

The application operates as a single-page experience using Streamlit's session state.

Rather than relying on multiple Streamlit pages, navigation is managed internally, creating a smoother and more application-like user experience.

---

### Modern User Interface

The interface has been designed to move beyond Streamlit's default appearance.

Highlights include:

* responsive layouts
* reusable UI components
* modern typography
* custom CSS styling
* glass-inspired cards
* consistent spacing and hierarchy
* animated loading states
* dedicated success and failure pages
* polished navigation flow

The design draws inspiration from modern SaaS products while remaining practical for internal business use.

---

## Technology Stack

* Python
* Streamlit
* HTML
* CSS
* Streamlit Session State

---

## Project Structure

```text
project/
│
├── app.py
├── style.css
├── assets/
│   └── logo.png
└── README.md
```

The project intentionally maintains a lightweight structure to simplify development and future maintenance.

---

## Application Flow

```text
Home
│
├── Start Filling
│      │
│      ▼
│  Select Submission Mode
│      │
│      ├── Voice Mode
│      │      │
│      │      ▼
│      │  Record Audio
│      │      │
│      │      ▼
│      │  Process Recording
│      │      │
│      │      ▼
│      │  Review & Complete Form
│      │      │
│      │      ▼
│      │     Submit
│      │
│      └── Form Mode
│             │
│             ▼
│       Complete Form
│             │
│             ▼
│           Submit
│
└── Download Centre
       │
       ▼
 Download Enquiries
```

---

## Application Architecture

The application is organised around reusable page and helper functions.

Core pages include:

* Home
* Mode Selection
* Voice Submission
* Manual Form
* Download Centre
* Success Page
* Failure Page

Supporting helpers manage:

* navigation
* validation
* session management
* reusable UI components
* placeholder backend services

This modular structure keeps the application easy to extend without introducing unnecessary complexity.

---

## Placeholder Backend Services

The current implementation includes placeholder functions representing future backend integrations.

These include:

* `parse_audio()`
* `upload_audio()`
* `save_enquiry()`
* `download_enquiries()`
* `generate_presigned_url()`

Each function currently returns mock data so that the user interface can be developed independently of backend infrastructure.

Replacing these placeholders with production services requires minimal changes to the surrounding interface.

---

## Running the Project

Clone the repository:

```bash
git clone <repository-url>
```

Navigate into the project directory:

```bash
cd <project-directory>
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run app.py
```

The application will open automatically in your default web browser.

---

## Future Enhancements

The current architecture has been designed to support future integrations with minimal restructuring.

Planned improvements include:

* database persistence
* user authentication
* role-based permissions
* cloud storage for audio recordings
* AI-powered speech transcription
* automatic enquiry categorisation
* search and filtering
* reporting dashboard
* analytics
* email notifications
* audit logging
* export to Excel and PDF

---

## Design Principles

Several principles guided the development of this application:

* Keep workflows simple.
* Reduce unnecessary user input.
* Make validation immediate and understandable.
* Present AI-generated information for review rather than blind acceptance.
* Keep navigation intuitive.
* Build reusable components wherever practical.
* Design for future backend integration without coupling the interface to implementation details.

The result is an application that feels closer to a modern business tool than a traditional Streamlit application while remaining straightforward to maintain.

---

## License

This project is proprietary software developed for **Ivy League Associates**.

All rights reserved.
