import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
from app import app, db
from models import Meeting
from utils import allowed_file, validate_audio_file, generate_pdf, generate_txt
from datetime import datetime

class MeetingMinutesTestCase(unittest.TestCase):
    """Test cases for the Meeting Minutes Generator application"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create a temporary database
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_index_page_loads(self):
        """Test that the main page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Meeting Minutes Generator', response.data)
        self.assertIn(b'Upload Meeting Audio', response.data)

    def test_allowed_file_validation(self):
        """Test file extension validation"""
        # Valid files
        self.assertTrue(allowed_file('test.mp3'))
        self.assertTrue(allowed_file('test.wav'))
        self.assertTrue(allowed_file('meeting_audio.MP3'))
        self.assertTrue(allowed_file('recording.WAV'))
        
        # Invalid files
        self.assertFalse(allowed_file('test.txt'))
        self.assertFalse(allowed_file('video.mp4'))
        self.assertFalse(allowed_file('image.jpg'))
        self.assertFalse(allowed_file('document.pdf'))
        self.assertFalse(allowed_file('no_extension'))

    def test_file_upload_no_file(self):
        """Test upload endpoint with no file"""
        response = self.app.post('/upload', data={
            'meeting_title': 'Test Meeting',
            'meeting_date': '2024-01-01',
            'participants': 'John Doe, Jane Smith'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No file selected', response.data)

    def test_file_upload_invalid_extension(self):
        """Test upload with invalid file extension"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'This is not an audio file')
            tmp.flush()
            
            try:
                with open(tmp.name, 'rb') as test_file:
                    response = self.app.post('/upload', data={
                        'audio_file': (test_file, 'test.txt'),
                        'meeting_title': 'Test Meeting',
                        'meeting_date': '2024-01-01',
                        'participants': 'John Doe'
                    }, follow_redirects=True)
                
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Invalid file format', response.data)
            finally:
                os.unlink(tmp.name)

    def test_file_upload_missing_title(self):
        """Test upload with missing meeting title"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp.flush()
            
            try:
                with open(tmp.name, 'rb') as test_file:
                    response = self.app.post('/upload', data={
                        'audio_file': (test_file, 'test.mp3'),
                        'meeting_date': '2024-01-01',
                        'participants': 'John Doe'
                    }, follow_redirects=True)
                
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Meeting title is required', response.data)
            finally:
                os.unlink(tmp.name)

    @patch('openai_service.transcribe_audio')
    @patch('openai_service.summarize_text')
    @patch('utils.validate_audio_file')
    def test_successful_upload_and_processing(self, mock_validate, mock_summarize, mock_transcribe):
        """Test successful file upload and processing"""
        # Mock the external services
        mock_validate.return_value = True
        mock_transcribe.return_value = "This is a test transcript of the meeting."
        mock_summarize.return_value = "• Meeting was productive\n• Action items assigned\n• Next meeting scheduled"
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp.flush()
            
            try:
                with open(tmp.name, 'rb') as test_file:
                    response = self.app.post('/upload', data={
                        'audio_file': (test_file, 'test.mp3'),
                        'meeting_title': 'Test Meeting',
                        'meeting_date': '2024-01-01',
                        'participants': 'John Doe, Jane Smith'
                    }, follow_redirects=True)
                
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Meeting minutes generated successfully', response.data)
                
                # Verify meeting was saved to database
                with app.app_context():
                    meeting = Meeting.query.first()
                    self.assertIsNotNone(meeting)
                    self.assertEqual(meeting.title, 'Test Meeting')
                    self.assertEqual(meeting.transcript, "This is a test transcript of the meeting.")
                    
            finally:
                os.unlink(tmp.name)

    def test_result_page_with_invalid_id(self):
        """Test result page with non-existent meeting ID"""
        response = self.app.get('/result/999')
        self.assertEqual(response.status_code, 404)

    def test_meeting_model_methods(self):
        """Test Meeting model helper methods"""
        with app.app_context():
            meeting = Meeting(
                title="Test Meeting",
                date=datetime(2024, 1, 1),
                participants="John Doe, Jane Smith, Bob Wilson",
                transcript="This is a test transcript.",
                summary="• Point 1\n• Point 2\n• Point 3",
                filename="test.mp3"
            )
            
            # Test formatted date
            self.assertEqual(meeting.get_formatted_date(), "January 01, 2024")
            
            # Test participants list
            participants = meeting.get_participants_list()
            self.assertEqual(len(participants), 3)
            self.assertIn("John Doe", participants)
            self.assertIn("Jane Smith", participants)
            self.assertIn("Bob Wilson", participants)
            
            # Test summary points
            points = meeting.get_summary_points()
            self.assertEqual(len(points), 3)
            self.assertIn("Point 1", points)
            self.assertIn("Point 2", points)
            self.assertIn("Point 3", points)

    def test_export_invalid_format(self):
        """Test export with invalid format"""
        with app.app_context():
            meeting = Meeting(
                title="Test Meeting",
                date=datetime(2024, 1, 1),
                participants="John Doe",
                transcript="Test transcript",
                summary="• Test summary",
                filename="test.mp3"
            )
            db.session.add(meeting)
            db.session.commit()
            
            response = self.app.get(f'/export/{meeting.id}/invalid', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid export format', response.data)

    def test_pdf_generation(self):
        """Test PDF generation functionality"""
        with app.app_context():
            meeting = Meeting(
                title="Test Meeting",
                date=datetime(2024, 1, 1),
                participants="John Doe, Jane Smith",
                transcript="This is a test transcript for PDF generation.",
                summary="• Meeting was productive\n• Action items were assigned\n• Follow-up scheduled",
                filename="test.mp3"
            )
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                try:
                    generate_pdf(meeting, tmp.name)
                    
                    # Check that file was created and has content
                    self.assertTrue(os.path.exists(tmp.name))
                    self.assertGreater(os.path.getsize(tmp.name), 0)
                    
                    # Basic PDF validation (check for PDF header)
                    with open(tmp.name, 'rb') as pdf_file:
                        header = pdf_file.read(4)
                        self.assertEqual(header, b'%PDF')
                        
                finally:
                    if os.path.exists(tmp.name):
                        os.unlink(tmp.name)

    def test_txt_generation(self):
        """Test TXT generation functionality"""
        with app.app_context():
            meeting = Meeting(
                title="Test Meeting",
                date=datetime(2024, 1, 1),
                participants="John Doe, Jane Smith",
                transcript="This is a test transcript for TXT generation.",
                summary="• Meeting was productive\n• Action items were assigned\n• Follow-up scheduled",
                filename="test.mp3"
            )
            
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
                try:
                    generate_txt(meeting, tmp.name)
                    
                    # Check that file was created and has content
                    self.assertTrue(os.path.exists(tmp.name))
                    self.assertGreater(os.path.getsize(tmp.name), 0)
                    
                    # Validate content
                    with open(tmp.name, 'r', encoding='utf-8') as txt_file:
                        content = txt_file.read()
                        self.assertIn("TEST MEETING", content)
                        self.assertIn("January 01, 2024", content)
                        self.assertIn("John Doe, Jane Smith", content)
                        self.assertIn("Meeting was productive", content)
                        self.assertIn("This is a test transcript", content)
                        
                finally:
                    if os.path.exists(tmp.name):
                        os.unlink(tmp.name)

    def test_history_page(self):
        """Test meeting history page"""
        response = self.app.get('/history')
        self.assertEqual(response.status_code, 200)

    @patch('openai_service.transcribe_audio')
    def test_transcription_error_handling(self, mock_transcribe):
        """Test handling of transcription errors"""
        mock_transcribe.side_effect = Exception("Transcription failed")
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp.flush()
            
            try:
                with patch('utils.validate_audio_file', return_value=True):
                    with open(tmp.name, 'rb') as test_file:
                        response = self.app.post('/upload', data={
                            'audio_file': (test_file, 'test.mp3'),
                            'meeting_title': 'Test Meeting',
                            'meeting_date': '2024-01-01'
                        }, follow_redirects=True)
                    
                    self.assertEqual(response.status_code, 200)
                    self.assertIn(b'Error processing audio file', response.data)
                    
            finally:
                os.unlink(tmp.name)

    def test_empty_transcript_handling(self):
        """Test handling of empty or very short transcripts"""
        with app.app_context():
            meeting = Meeting(
                title="Test Meeting",
                date=datetime(2024, 1, 1),
                participants="",
                transcript="",
                summary="",
                filename="test.mp3"
            )
            
            # Test methods with empty data
            self.assertEqual(meeting.get_participants_list(), [])
            self.assertEqual(meeting.get_summary_points(), [])

if __name__ == '__main__':
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(MeetingMinutesTestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
