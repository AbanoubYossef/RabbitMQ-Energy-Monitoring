"""
AI Service Integration with Google Gemini
Provides intelligent responses when rule-based chatbot doesn't match
"""
import google.generativeai as genai
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Google Gemini AI integration for customer support"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = None
        self.enabled = False
        
        if self.api_key and self.api_key != 'your-gemini-api-key-here':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.enabled = True
                logger.info("✅ Google Gemini AI initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini AI: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️  Gemini API key not configured - AI responses disabled")
    
    def is_enabled(self):
        """Check if AI service is available"""
        return self.enabled
    
    def generate_response(self, user_message, context=None):
        """
        Generate AI response for user message
        
        Args:
            user_message: User's question/message
            context: Optional context about the user or system
            
        Returns:
            str: AI-generated response or error message
        """
        if not self.enabled:
            return self._get_fallback_response()
        
        try:
            # Build prompt with context
            prompt = self._build_prompt(user_message, context)
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info(f"✅ AI response generated for: {user_message[:50]}...")
                return response.text
            else:
                logger.warning("⚠️  AI returned empty response")
                return self._get_fallback_response()
                
        except Exception as e:
            logger.error(f"❌ AI generation error: {e}")
            return self._get_fallback_response()
    
    def _build_prompt(self, user_message, context=None):
        """Build prompt for Gemini with system context"""
        system_context = """
You are a helpful customer support assistant for an Energy Management System.

System Features:
- Users can monitor their device energy consumption
- Devices have maximum consumption limits
- Users receive overconsumption alerts
- Administrators manage users and devices
- Real-time monitoring with hourly/daily charts

Your role:
- Answer questions about the Energy Management System
- Be helpful, concise, and friendly
- If you don't know something, suggest contacting an administrator
- Keep responses under 200 words
- Use emojis sparingly for better readability

User Question:
"""
        
        # Add user context if available
        if context:
            system_context += f"\nUser Context: {context}\n\n"
        
        return system_context + user_message
    
    def _get_fallback_response(self):
        """Fallback response when AI is unavailable"""
        return (
            "I'm not sure how to answer that question. "
            "Please try rephrasing, or type 'help' to see what I can assist you with. "
            "You can also contact an administrator for further assistance."
        )
    
    def test_connection(self):
        """Test AI service connection"""
        if not self.enabled:
            return False, "API key not configured"
        
        try:
            response = self.model.generate_content("Hello, this is a test.")
            if response and response.text:
                return True, "AI service is working"
            return False, "AI returned empty response"
        except Exception as e:
            return False, str(e)
