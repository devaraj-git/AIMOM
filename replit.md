# Overview

This is a Flask-based AI Meeting Minutes Generator application that automatically transcribes meeting audio files and generates summarized meeting minutes using OpenAI's Whisper and GPT-4o APIs. Users can upload MP3 or WAV audio files, provide meeting details, and receive professionally formatted meeting summaries that can be exported as PDF or TXT files. The application also supports sending meeting minutes via email to participants with PDF attachments.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **UI Framework**: Bootstrap 5 with dark theme optimized for Replit
- **File Upload**: Dropzone.js for drag-and-drop audio file uploads with client-side validation
- **Responsive Design**: Mobile-first responsive layout with Font Awesome icons
- **Form Handling**: Traditional HTML forms with CSRF protection via Flask's secret key

## Backend Architecture
- **Web Framework**: Flask with modular structure separating concerns into distinct modules
- **Application Factory Pattern**: Central app configuration in `app.py` with model imports
- **Route Organization**: RESTful endpoints for upload, processing, viewing, and export operations
- **File Management**: Secure file handling with `werkzeug.utils.secure_filename` and validation
- **Error Handling**: Comprehensive exception handling with user-friendly error messages

## Data Storage Solutions
- **Primary Database**: SQLAlchemy ORM with SQLite default (configurable to PostgreSQL via DATABASE_URL)
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability
- **Schema Design**: Single `Meeting` model storing title, date, participants, transcript, summary, and metadata
- **File Storage**: Local filesystem storage in `uploads/` and `exports/` directories

## Authentication and Authorization
- **Session Management**: Flask sessions with configurable secret key from environment variables
- **Security Headers**: ProxyFix middleware for proper header handling behind proxies
- **File Validation**: Multi-layer validation using file extensions and MIME type checking with python-magic
- **Upload Limits**: 100MB maximum file size restriction

## AI Processing Pipeline
- **Speech-to-Text**: OpenAI Whisper API for audio transcription with error handling
- **Text Summarization**: GPT-4o for intelligent meeting summary generation
- **Service Layer**: Dedicated `openai_service.py` module with proper API key management
- **Processing Flow**: Asynchronous-style processing with user feedback during long operations

## Document Generation
- **PDF Export**: ReportLab library for professional PDF generation with custom styling
- **Text Export**: Plain text formatting for universal compatibility
- **Template System**: Reusable export templates with consistent formatting

## Email Functionality
- **Email Service**: SMTP-based email sending via `email_service.py` module
- **Participant Notification**: Automatically send meeting minutes to participants via email
- **Email Parsing**: Extract email addresses from participants field using regex pattern matching
- **HTML Emails**: Professional HTML-formatted emails with inline CSS styling
- **PDF Attachments**: Attach generated PDF meeting minutes to emails
- **SMTP Configuration**: Supports Gmail, Outlook, Yahoo, and custom SMTP servers via environment variables
- **Demo Mode**: Optional demo mode (`DEMO_MODE=True`) for testing without OpenAI API calls

# External Dependencies

## AI Services
- **OpenAI API**: Whisper model for transcription and GPT-4o for summarization
- **API Key Management**: Environment variable-based configuration with validation

## Database Systems
- **SQLite**: Default development database (file-based)
- **PostgreSQL**: Production database option via DATABASE_URL environment variable
- **SQLAlchemy**: ORM layer with migration support

## File Processing Libraries
- **python-magic**: MIME type detection for file validation
- **werkzeug**: Secure filename handling and file utilities

## Document Generation
- **ReportLab**: PDF generation with advanced formatting capabilities
- **Font and styling**: Custom paragraph styles and layouts

## Frontend Assets
- **Bootstrap 5**: UI framework with Replit's dark theme integration
- **Dropzone.js**: Advanced file upload interface with drag-and-drop
- **Font Awesome**: Icon library for enhanced user interface
- **CDN Delivery**: External CDN hosting for frontend assets

## Email Services
- **SMTP Support**: Native Python smtplib for email delivery
- **Multi-Provider**: Compatible with Gmail (App Passwords), Outlook, Yahoo, and custom SMTP
- **Email Parsing**: Regex-based email extraction from participant lists
- **HTML Templating**: Inline CSS for email client compatibility

## Development and Testing
- **unittest**: Python testing framework for application testing
- **Flask testing**: Built-in test client for endpoint testing
- **Mock libraries**: Unit test mocking for external service dependencies
- **Demo Mode**: Testing mode that bypasses OpenAI API calls with sample data

## Environment Variables
- **DEMO_MODE**: Set to `True` to use sample data instead of OpenAI API (for testing without credits)
- **SMTP_HOST**: SMTP server hostname (default: smtp.gmail.com)
- **SMTP_PORT**: SMTP server port (default: 587)
- **SMTP_USER**: Email account username for sending
- **SMTP_PASSWORD**: Email account password or app password
- **FROM_EMAIL**: Email address to send from (defaults to SMTP_USER)
- **FROM_NAME**: Display name for sender (default: AI Meeting Minutes)
- **OPENAI_API_KEY**: OpenAI API key for Whisper and GPT-4o
- **DATABASE_URL**: Database connection string (default: SQLite)
- **SESSION_SECRET**: Flask session secret key

## Additional Features
- **Email to Participants**: Send meeting minutes with PDF attachments to participant email addresses
- **Email Validation**: Automatic extraction and validation of email addresses from participant field
- **Demo Mode**: Test full application workflow without consuming OpenAI API credits