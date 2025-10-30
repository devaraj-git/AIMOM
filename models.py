from app import db
from datetime import datetime

class Meeting(db.Model):
    """Model for storing meeting information and minutes"""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    participants = db.Column(db.Text)
    transcript = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Meeting {self.title}>'
    
    def get_formatted_date(self):
        """Get formatted date string"""
        return self.date.strftime('%B %d, %Y')
    
    def get_participants_list(self):
        """Get participants as a list"""
        if not self.participants:
            return []
        return [p.strip() for p in self.participants.split(',') if p.strip()]
    
    def get_summary_points(self):
        """Get summary as bullet points list"""
        if not self.summary:
            return []
        
        # Split by bullet points or line breaks
        points = []
        for line in self.summary.split('\n'):
            line = line.strip()
            if line:
                # Remove existing bullet points or dashes
                line = line.lstrip('•-*').strip()
                if line:
                    points.append(line)
        return points
