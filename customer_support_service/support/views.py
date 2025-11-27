from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
import jwt
from django.conf import settings
import logging

from .models import ChatSession, ChatMessage
from .serializers import ChatMessageSerializer, ChatSessionSerializer
from .chatbot import ChatbotEngine
from .ai_service import AIService
from .rabbitmq import publish_chat_message

logger = logging.getLogger(__name__)

# Initialize chatbot and AI service
chatbot = ChatbotEngine()
ai_service = AIService()


def get_user_from_token(request):
    """Extract user info from JWT token"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return {
            'user_id': decoded.get('user_id'),
            'username': decoded.get('username'),
            'role': decoded.get('role')
        }
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None


@api_view(['POST'])
def send_message(request):
    """
    Send a message and get bot response
    POST /api/support/chat
    Body: {"message": "user message text"}
    """
    user_info = get_user_from_token(request)
    if not user_info:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user_message = request.data.get('message', '').strip()
    if not user_message:
        return Response(
            {'error': 'Message is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get or create active session for user
        session, created = ChatSession.objects.get_or_create(
            user_id=user_info['user_id'],
            status='active',
            defaults={'username': user_info['username']}
        )
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            sender='user',
            message=user_message,
            response_type='user_message'
        )
        
        # Process message with chatbot
        bot_response_data = chatbot.process_message(user_message, user_info['user_id'])
        
        # Determine response
        if bot_response_data['matched']:
            # Rule-based response
            bot_response_text = bot_response_data['response']
            response_type = 'rule_based'
            rule_id = bot_response_data['rule_id']
            logger.info(f"✅ Rule {rule_id} matched for user {user_info['username']}")
        else:
            # Try AI response
            if ai_service.is_enabled():
                bot_response_text = ai_service.generate_response(
                    user_message,
                    context=f"User: {user_info['username']}, Role: {user_info['role']}"
                )
                response_type = 'ai_generated'
                rule_id = None
                logger.info(f"✅ AI response generated for user {user_info['username']}")
            else:
                # Fallback response
                bot_response_text = (
                    "I'm not sure how to answer that. Please try:\n"
                    "• Type 'help' to see what I can do\n"
                    "• Rephrase your question\n"
                    "• Type 'admin' to contact an administrator"
                )
                response_type = 'rule_based'
                rule_id = None
                logger.warning(f"⚠️  No match and AI disabled for: {user_message[:50]}")
        
        # Save bot response
        bot_msg = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message=bot_response_text,
            response_type=response_type,
            rule_id=rule_id
        )
        
        # Publish to WebSocket queue if needed
        try:
            publish_chat_message({
                'session_id': str(session.id),
                'recipient_id': str(user_info['user_id']),
                'sender': 'bot',
                'message': bot_response_text,
                'timestamp': bot_msg.timestamp.isoformat()
            })
        except Exception as e:
            logger.error(f"Failed to publish to WebSocket: {e}")
        
        # Return response
        return Response({
            'session_id': str(session.id),
            'user_message': {
                'id': str(user_msg.id),
                'message': user_msg.message,
                'timestamp': user_msg.timestamp
            },
            'bot_response': {
                'id': str(bot_msg.id),
                'message': bot_msg.message,
                'response_type': bot_msg.response_type,
                'rule_id': bot_msg.rule_id,
                'timestamp': bot_msg.timestamp
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_sessions(request):
    """
    Get user's chat sessions
    GET /api/support/sessions
    """
    user_info = get_user_from_token(request)
    if not user_info:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    sessions = ChatSession.objects.filter(user_id=user_info['user_id'])
    serializer = ChatSessionSerializer(sessions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_session_history(request, session_id):
    """
    Get chat history for a session
    GET /api/support/history/{session_id}
    """
    user_info = get_user_from_token(request)
    if not user_info:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        session = ChatSession.objects.get(id=session_id, user_id=user_info['user_id'])
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        
        return Response({
            'session': ChatSessionSerializer(session).data,
            'messages': serializer.data
        }, status=status.HTTP_200_OK)
        
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def close_session(request, session_id):
    """
    Close a chat session
    POST /api/support/sessions/{session_id}/close
    """
    user_info = get_user_from_token(request)
    if not user_info:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        session = ChatSession.objects.get(id=session_id, user_id=user_info['user_id'])
        session.status = 'closed'
        session.closed_at = timezone.now()
        session.save()
        
        return Response({
            'message': 'Session closed successfully',
            'session': ChatSessionSerializer(session).data
        }, status=status.HTTP_200_OK)
        
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def chatbot_info(request):
    """
    Get chatbot information
    GET /api/support/info
    """
    return Response({
        'service': 'Customer Support Chatbot',
        'version': '1.0.0',
        'rules_count': chatbot.get_rule_count(),
        'ai_enabled': ai_service.is_enabled(),
        'features': {
            'rule_based_responses': True,
            'ai_responses': ai_service.is_enabled(),
            'admin_chat': True,
            'session_management': True
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'customer-support-service',
        'chatbot_rules': chatbot.get_rule_count(),
        'ai_enabled': ai_service.is_enabled()
    }, status=status.HTTP_200_OK)
