import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import uuid
from datetime import datetime
from utils import allowed_file, validate_audio_file, generate_pdf, generate_txt
from openai_service import transcribe_audio, summarize_text
from email_service import send_meeting_minutes, parse_participant_emails

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
EXPORT_FOLDER = 'exports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXPORT_FOLDER'] = EXPORT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///meeting_minutes.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Create upload and export directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

with app.app_context():
    # Import models here to ensure they're registered
    import models
    db.create_all()

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    # Check if we're in demo mode
    DEMO_MODE = os.environ.get("DEMO_MODE", "False").lower() in ["true", "1", "yes"]
    
    try:
        # Get form data
        meeting_title = request.form.get('meeting_title', '').strip()
        meeting_date = request.form.get('meeting_date', '').strip()
        participants = request.form.get('participants', '').strip()
        
        if not meeting_title:
            flash('Meeting title is required', 'error')
            return redirect(url_for('index'))
        
        # In demo mode, skip actual file upload and use mock data
        if DEMO_MODE:
            app.logger.info("DEMO MODE: Skipping file upload, using sample data")
            
            # Generate demo meeting directly
            transcript = transcribe_audio("demo.mp3")  # Will return mock transcript
            summary = summarize_text(transcript)  # Will return mock summary
            
            # Save to database
            meeting = models.Meeting()
            meeting.title = meeting_title
            meeting.date = datetime.strptime(meeting_date, '%Y-%m-%d').date() if meeting_date else datetime.now().date()
            meeting.participants = participants
            meeting.transcript = transcript
            meeting.summary = summary
            meeting.filename = "demo_audio.mp3"
            db.session.add(meeting)
            db.session.commit()
            
            flash('Meeting minutes generated successfully! (Demo Mode)', 'success')
            return redirect(url_for('result', meeting_id=meeting.id))
        
        # Normal mode - process actual file upload
        # Validate form data
        if 'audio_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['audio_file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Validate file
        if not file.filename or not allowed_file(file.filename):
            flash('Invalid file format. Please upload MP3 or WAV files only.', 'error')
            return redirect(url_for('index'))
        
        # Generate unique filename
        filename = secure_filename(file.filename or "")
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(file_path)
        
        # Validate audio file
        try:
            if not validate_audio_file(file_path):
                os.remove(file_path)
                flash('Invalid audio file. Please upload a valid MP3 or WAV file.', 'error')
                return redirect(url_for('index'))
        except Exception as e:
            app.logger.warning(f"File validation failed: {str(e)}, proceeding anyway")
            # Continue processing - some valid audio files might not pass magic validation
        
        # Process the audio file
        try:
            # Transcribe audio
            app.logger.info(f"Starting transcription for file: {unique_filename}")
            transcript = transcribe_audio(file_path)
            
            if not transcript or len(transcript.strip()) < 10:
                raise Exception("Transcription resulted in very short or empty text")
            
            # Summarize transcript
            app.logger.info("Starting summarization")
            summary = summarize_text(transcript)
            
            # Save to database
            meeting = models.Meeting()
            meeting.title = meeting_title
            meeting.date = datetime.strptime(meeting_date, '%Y-%m-%d').date() if meeting_date else datetime.now().date()
            meeting.participants = participants
            meeting.transcript = transcript
            meeting.summary = summary
            meeting.filename = unique_filename
            db.session.add(meeting)
            db.session.commit()
            
            # Clean up uploaded file
            os.remove(file_path)
            
            flash('Meeting minutes generated successfully!', 'success')
            return redirect(url_for('result', meeting_id=meeting.id))
            
        except Exception as e:
            app.logger.error(f"Error processing audio: {str(e)}")
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Check if it's an API quota issue
            error_message = str(e)
            if "quota" in error_message.lower() or "429" in error_message:
                flash('OpenAI API quota exceeded. Please check your OpenAI account billing and usage limits.', 'error')
            elif "insufficient_quota" in error_message.lower():
                flash('Insufficient OpenAI API quota. Please add credits to your OpenAI account or upgrade your plan.', 'error')
            else:
                flash(f'Error processing audio file: {str(e)}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        app.logger.error(f"Unexpected error in upload: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/result/<int:meeting_id>')
def result(meeting_id):
    """Display meeting minutes result"""
    try:
        meeting = models.Meeting.query.get_or_404(meeting_id)
        return render_template('result.html', meeting=meeting)
    except Exception as e:
        app.logger.error(f"Error loading result: {str(e)}")
        flash('Error loading meeting minutes', 'error')
        return redirect(url_for('index'))

@app.route('/export/<int:meeting_id>/<format>')
def export_meeting(meeting_id, format):
    """Export meeting minutes as PDF or TXT"""
    try:
        meeting = models.Meeting.query.get_or_404(meeting_id)
        
        if format not in ['pdf', 'txt']:
            flash('Invalid export format', 'error')
            return redirect(url_for('result', meeting_id=meeting_id))
        
        # Generate export file
        export_filename = f"meeting_{meeting_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        export_path = os.path.join(app.config['EXPORT_FOLDER'], export_filename)
        
        if format == 'pdf':
            generate_pdf(meeting, export_path)
            mimetype = 'application/pdf'
        else:  # txt
            generate_txt(meeting, export_path)
            mimetype = 'text/plain'
        
        return send_file(
            export_path,
            as_attachment=True,
            download_name=f"{meeting.title}_{format}.{format}",
            mimetype=mimetype
        )
        
    except Exception as e:
        app.logger.error(f"Error exporting meeting: {str(e)}")
        flash(f'Error exporting meeting minutes: {str(e)}', 'error')
        return redirect(url_for('result', meeting_id=meeting_id))

@app.route('/send-email/<int:meeting_id>', methods=['POST'])
def send_email(meeting_id):
    """Send meeting minutes via email to participants"""
    try:
        meeting = models.Meeting.query.get_or_404(meeting_id)
        
        # Parse participant emails
        participant_emails = parse_participant_emails(meeting.participants)
        
        if not participant_emails:
            flash('No valid email addresses found in participants list. Please include email addresses (e.g., john@example.com).', 'error')
            return redirect(url_for('result', meeting_id=meeting_id))
        
        # Generate PDF for attachment
        export_filename = f"meeting_{meeting_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        export_path = os.path.join(app.config['EXPORT_FOLDER'], export_filename)
        generate_pdf(meeting, export_path)
        
        # Send email
        try:
            send_meeting_minutes(
                to_emails=participant_emails,
                meeting_title=meeting.title,
                meeting_date=meeting.date.strftime('%B %d, %Y'),
                summary=meeting.summary,
                pdf_path=export_path
            )
            
            flash(f'Meeting minutes sent successfully to {len(participant_emails)} participant(s)!', 'success')
        finally:
            # Clean up temporary PDF
            if os.path.exists(export_path):
                os.remove(export_path)
        
        return redirect(url_for('result', meeting_id=meeting_id))
        
    except Exception as e:
        app.logger.error(f"Error sending email: {str(e)}")
        flash(f'Error sending email: {str(e)}', 'error')
        return redirect(url_for('result', meeting_id=meeting_id))

@app.route('/history')
def history():
    """Display meeting history"""
    try:
        meetings = models.Meeting.query.order_by(models.Meeting.created_at.desc()).all()
        return render_template('history.html', meetings=meetings)
    except Exception as e:
        app.logger.error(f"Error loading history: {str(e)}")
        flash('Error loading meeting history', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 100MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    flash('Page not found', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Internal server error: {str(e)}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))
