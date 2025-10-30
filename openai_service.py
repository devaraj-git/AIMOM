import os
import logging
from openai import OpenAI

# Demo mode - set to True to use mock data instead of OpenAI API
DEMO_MODE = os.environ.get("DEMO_MODE", "False").lower() in ["true", "1", "yes"]

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not DEMO_MODE and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required (or set DEMO_MODE=True for testing)")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using OpenAI Whisper API
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    if DEMO_MODE:
        logging.info("DEMO MODE: Using sample transcript instead of OpenAI API")
        return """
        Good morning everyone. Let's start our weekly team meeting. First on the agenda is the project status update.
        
        Sarah, can you share an update on the new feature development? Sure, we've completed the user authentication module 
        and it's currently in testing. The team has been working really hard and we're about 80% done with the overall sprint goals.
        
        Great work Sarah. Now, regarding the database migration that Tom mentioned last week, what's the status on that? 
        Tom here - the migration is scheduled for this Friday night at 11 PM. We've done dry runs in the staging environment 
        and everything looks good. We expect minimal downtime, probably around 30 minutes.
        
        Perfect. Let's make sure all stakeholders are notified. Moving on to the next topic, we need to discuss the upcoming 
        client presentation. Lisa, you're leading that, correct? Yes, I am. I've prepared the slides and sent them to everyone 
        yesterday. Please review them and send me your feedback by tomorrow so I can incorporate any changes before the Friday presentation.
        
        Excellent. Are there any blockers or concerns anyone wants to raise? Mike has a question about the API rate limits 
        we're seeing in production. Good point Mike. Let's schedule a separate technical discussion about that after this meeting.
        
        Any other items? If not, let's wrap up. Great job everyone, keep up the good work. Meeting adjourned.
        """
    
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = openai_client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text"
            )
        
        if not response or len(response.strip()) < 5:
            raise Exception("Transcription resulted in very short or empty text")
            
        return response
        
    except Exception as e:
        logging.error(f"Error transcribing audio: {str(e)}")
        raise Exception(f"Failed to transcribe audio: {str(e)}")

def summarize_text(text):
    """
    Summarize text using OpenAI GPT-4o
    
    Args:
        text (str): Text to summarize
        
    Returns:
        str: Summarized text in bullet points
        
    Raises:
        Exception: If summarization fails
    """
    if DEMO_MODE:
        logging.info("DEMO MODE: Using sample summary instead of OpenAI API")
        return """
**Key Discussion Points:**
- Project status update: User authentication module completed and in testing phase (80% sprint completion)
- Database migration scheduled for Friday night at 11 PM with expected 30-minute downtime
- Staging environment dry runs completed successfully
- Client presentation preparation in progress

**Action Items:**
- Tom: Execute database migration on Friday at 11 PM
- Lisa: Incorporate team feedback into presentation slides by tomorrow
- All team members: Review presentation slides and provide feedback by tomorrow
- Team: Schedule separate technical discussion about API rate limits after meeting

**Decisions Made:**
- Database migration approved for Friday night
- Client presentation scheduled for Friday
- Stakeholder notifications to be sent regarding migration

**Next Steps:**
- Stakeholder notification about database migration
- Technical discussion on API rate limiting issues
- Final review of client presentation materials
- Continue sprint work toward completion goals
        """
    
    try:
        if not text or len(text.strip()) < 10:
            raise Exception("Text is too short to summarize")
        
        prompt = f"""
        Please analyze the following meeting transcript and create a comprehensive summary in bullet points.
        Focus on:
        - Key decisions made
        - Action items and responsibilities
        - Important discussion points
        - Next steps or follow-ups
        
        Format the response as clear, concise bullet points that capture the essence of the meeting.
        
        Transcript:
        {text}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert meeting minutes assistant. Create clear, actionable summaries from meeting transcripts."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content
        
        if not summary or len(summary.strip()) < 10:
            raise Exception("Summarization resulted in very short or empty text")
            
        return summary
        
    except Exception as e:
        logging.error(f"Error summarizing text: {str(e)}")
        raise Exception(f"Failed to summarize text: {str(e)}")
