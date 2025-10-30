import os
import magic
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'm4a'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_audio_file(file_path):
    """Validate that the file is actually an audio file using python-magic"""
    try:
        # Check file using magic
        file_type = magic.from_file(file_path, mime=True)
        return file_type in ['audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/mp4', 'audio/m4a']
    except Exception:
        # Fallback to extension check if magic is not available
        return allowed_file(file_path)

def generate_pdf(meeting, output_path):
    """Generate PDF export of meeting minutes"""
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add title
        story.append(Paragraph(f"Meeting Minutes: {meeting.title}", title_style))
        story.append(Spacer(1, 12))
        
        # Add meeting details
        story.append(Paragraph(f"<b>Date:</b> {meeting.get_formatted_date()}", styles['Normal']))
        story.append(Spacer(1, 6))
        
        if meeting.participants:
            participants_text = ", ".join(meeting.get_participants_list())
            story.append(Paragraph(f"<b>Participants:</b> {participants_text}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Add summary section
        story.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
        story.append(Spacer(1, 6))
        
        # Add summary points
        summary_points = meeting.get_summary_points()
        for point in summary_points:
            story.append(Paragraph(f"• {point}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
        
        # Add full transcript section
        story.append(Paragraph("<b>Full Transcript:</b>", styles['Heading2']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(meeting.transcript, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")

def generate_txt(meeting, output_path):
    """Generate TXT export of meeting minutes"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"MEETING MINUTES: {meeting.title.upper()}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Date: {meeting.get_formatted_date()}\n")
            
            if meeting.participants:
                participants_text = ", ".join(meeting.get_participants_list())
                f.write(f"Participants: {participants_text}\n")
            
            f.write("\n" + "SUMMARY" + "\n")
            f.write("-" * 20 + "\n")
            
            # Add summary points
            summary_points = meeting.get_summary_points()
            for point in summary_points:
                f.write(f"• {point}\n")
            
            f.write("\n" + "FULL TRANSCRIPT" + "\n")
            f.write("-" * 30 + "\n")
            f.write(meeting.transcript)
            
    except Exception as e:
        raise Exception(f"Error generating TXT file: {str(e)}")
