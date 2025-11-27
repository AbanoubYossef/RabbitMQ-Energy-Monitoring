"""
Rule-Based Chatbot Engine
Implements 12+ rules for automatic customer support responses
"""
import re
import requests
from django.conf import settings


class ChatbotEngine:
    """Rule-based chatbot with pattern matching"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self):
        """Define chatbot rules with patterns and responses"""
        return [
            # Rule 1: Consumption/Usage queries
            {
                'id': 1,
                'patterns': [r'\b(consumption|usage|how much|energy)\b'],
                'keywords': ['consumption', 'usage', 'how much', 'energy'],
                'response_type': 'dynamic',
                'handler': self._handle_consumption_query
            },
            
            # Rule 2: Device listing
            {
                'id': 2,
                'patterns': [r'\b(my devices|list devices|show devices|devices)\b'],
                'keywords': ['my devices', 'list devices', 'show devices', 'devices'],
                'response_type': 'dynamic',
                'handler': self._handle_device_list
            },
            
            # Rule 3: Add/Assign device
            {
                'id': 3,
                'patterns': [r'\b(add device|assign device|new device|register device)\b'],
                'keywords': ['add device', 'assign', 'new device'],
                'response_type': 'static',
                'response': (
                    "To add a device to your account:\n\n"
                    "1. Contact your administrator\n"
                    "2. Provide the device details (name, max consumption)\n"
                    "3. Admin will create and assign the device to you\n\n"
                    "Note: Only administrators can add new devices to the system."
                )
            },
            
            # Rule 4: Help/Commands
            {
                'id': 4,
                'patterns': [r'\b(help|commands|what can you do|how to use)\b'],
                'keywords': ['help', 'commands', 'what can you do'],
                'response_type': 'static',
                'response': (
                    "I can help you with:\n\n"
                    "📊 Check your energy consumption\n"
                    "🔌 List your devices\n"
                    "➕ Guide you to add devices\n"
                    "🔔 Explain overconsumption alerts\n"
                    "🔑 Reset your password\n"
                    "👤 Contact an administrator\n"
                    "⏰ System availability info\n"
                    "📚 Usage tutorials\n\n"
                    "Just ask me anything!"
                )
            },
            
            # Rule 5: Password reset
            {
                'id': 5,
                'patterns': [r'\b(reset password|forgot password|change password|password)\b'],
                'keywords': ['reset password', 'forgot password', 'change password'],
                'response_type': 'static',
                'response': (
                    "To reset your password:\n\n"
                    "1. Contact your system administrator\n"
                    "2. Provide your username and email\n"
                    "3. Admin will reset your password\n"
                    "4. You'll receive new credentials\n\n"
                    "For security reasons, password resets must be done by administrators."
                )
            },
            
            # Rule 6: Contact admin
            {
                'id': 6,
                'patterns': [r'\b(admin|administrator|contact admin|speak to admin|talk to admin)\b'],
                'keywords': ['admin', 'administrator', 'contact admin'],
                'response_type': 'static',
                'response': (
                    "I've notified the administrators about your request. "
                    "An admin will respond to you shortly.\n\n"
                    "In the meantime, you can continue asking me questions!"
                )
            },
            
            # Rule 7: Working hours/Availability
            {
                'id': 7,
                'patterns': [r'\b(hours|working hours|availability|when available|open)\b'],
                'keywords': ['hours', 'working hours', 'availability', 'when available'],
                'response_type': 'static',
                'response': (
                    "🕐 System Availability:\n\n"
                    "The Energy Management System is available 24/7.\n"
                    "You can monitor your devices and check consumption anytime!\n\n"
                    "Administrator support hours: Monday-Friday, 9 AM - 5 PM"
                )
            },
            
            # Rule 8: Max consumption/Limits
            {
                'id': 8,
                'patterns': [r'\b(max consumption|limit|maximum|threshold|cap)\b'],
                'keywords': ['max consumption', 'limit', 'maximum', 'threshold'],
                'response_type': 'dynamic',
                'handler': self._handle_max_consumption
            },
            
            # Rule 9: Alerts/Notifications
            {
                'id': 9,
                'patterns': [r'\b(alert|notification|warning|overconsumption|exceeded)\b'],
                'keywords': ['alert', 'notification', 'warning', 'overconsumption'],
                'response_type': 'static',
                'response': (
                    "🔔 About Overconsumption Alerts:\n\n"
                    "You receive alerts when a device exceeds its maximum consumption limit.\n\n"
                    "Alert Severity Levels:\n"
                    "• Medium: 100-150% of max consumption\n"
                    "• High: Above 150% of max consumption\n\n"
                    "Alerts appear as real-time notifications in your dashboard."
                )
            },
            
            # Rule 10: How to/Tutorial
            {
                'id': 10,
                'patterns': [r'\b(how to|tutorial|guide|instructions|learn)\b'],
                'keywords': ['how to', 'tutorial', 'guide', 'instructions'],
                'response_type': 'static',
                'response': (
                    "📚 Quick Start Guide:\n\n"
                    "1. **Dashboard**: View your devices and consumption overview\n"
                    "2. **Monitoring**: Check hourly/daily energy consumption charts\n"
                    "3. **Devices**: See all your assigned devices\n"
                    "4. **Alerts**: Get notified of overconsumption\n\n"
                    "Navigate using the menu on the left side of the screen."
                )
            },
            
            # Rule 11: Error/Problem
            {
                'id': 11,
                'patterns': [r'\b(error|problem|issue|not working|broken|bug)\b'],
                'keywords': ['error', 'problem', 'issue', 'not working', 'broken'],
                'response_type': 'static',
                'response': (
                    "🔧 Troubleshooting Steps:\n\n"
                    "1. Refresh your browser page\n"
                    "2. Clear browser cache and cookies\n"
                    "3. Try logging out and back in\n"
                    "4. Check your internet connection\n\n"
                    "If the problem persists, please describe the issue in detail "
                    "and I'll notify an administrator to help you."
                )
            },
            
            # Rule 12: Thanks/Gratitude
            {
                'id': 12,
                'patterns': [r'\b(thank|thanks|appreciate|helpful)\b'],
                'keywords': ['thank', 'thanks', 'appreciate'],
                'response_type': 'static',
                'response': (
                    "You're welcome! 😊\n\n"
                    "I'm here to help anytime. Feel free to ask if you have more questions!"
                )
            },
        ]
    
    def process_message(self, message, user_id=None):
        """
        Process user message and return appropriate response
        
        Args:
            message: User's message text
            user_id: User ID for dynamic responses
            
        Returns:
            dict: Response with type, text, and matched rule
        """
        message_lower = message.lower()
        
        # Check each rule
        for rule in self.rules:
            # Check if any pattern matches
            for pattern in rule['patterns']:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    # Rule matched
                    if rule['response_type'] == 'static':
                        return {
                            'response': rule['response'],
                            'type': 'rule_based',
                            'rule_id': rule['id'],
                            'matched': True
                        }
                    elif rule['response_type'] == 'dynamic':
                        # Call handler function
                        response_text = rule['handler'](message, user_id)
                        return {
                            'response': response_text,
                            'type': 'rule_based',
                            'rule_id': rule['id'],
                            'matched': True
                        }
        
        # No rule matched
        return {
            'response': None,
            'type': 'no_match',
            'rule_id': None,
            'matched': False
        }
    
    def _handle_consumption_query(self, message, user_id):
        """Handle consumption/usage queries"""
        if not user_id:
            return "Please log in to view your consumption data."
        
        try:
            # Query monitoring service for user's consumption
            # This is a placeholder - actual implementation would call the API
            return (
                "📊 To view your energy consumption:\n\n"
                "1. Go to the **Monitoring** page from the menu\n"
                "2. Select a device from the dropdown\n"
                "3. Choose a date range\n"
                "4. View hourly/daily consumption charts\n\n"
                "You can also see real-time consumption on your Dashboard."
            )
        except Exception as e:
            return f"I encountered an error retrieving your consumption data. Please try again or contact support."
    
    def _handle_device_list(self, message, user_id):
        """Handle device listing queries"""
        if not user_id:
            return "Please log in to view your devices."
        
        try:
            # Query device service for user's devices
            # This is a placeholder - actual implementation would call the API
            return (
                "🔌 To view your devices:\n\n"
                "1. Go to the **Devices** page from the menu\n"
                "2. You'll see all devices assigned to you\n"
                "3. Click on a device to see details\n\n"
                "Each device shows its name, description, and maximum consumption limit."
            )
        except Exception as e:
            return f"I encountered an error retrieving your devices. Please try again or contact support."
    
    def _handle_max_consumption(self, message, user_id):
        """Handle max consumption queries"""
        return (
            "⚡ Maximum Consumption Limits:\n\n"
            "Each device has a maximum consumption limit set by your administrator.\n\n"
            "• You can view limits in the Devices page\n"
            "• Exceeding limits triggers overconsumption alerts\n"
            "• Only administrators can modify limits\n\n"
            "To request a limit change, contact your administrator."
        )
    
    def get_rule_count(self):
        """Return total number of rules"""
        return len(self.rules)
    
    def get_rules_summary(self):
        """Return summary of all rules"""
        return [
            {
                'id': rule['id'],
                'keywords': rule['keywords'],
                'type': rule['response_type']
            }
            for rule in self.rules
        ]
