from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User
from .models import ChatMessage, MoodAnalysis, FacialExpression
from django.utils.timezone import now
from textblob import TextBlob  # For sentiment analysis
from transformers import AutoModelForCausalLM, AutoTokenizer  # For conversational AI
import torch  # Import torch for tensor operations

# A mapping of sentiment polarity ranges to emotions
def classify_emotion(polarity):
    if polarity > 0.5:
        return "Happy"
    elif 0.1 < polarity <= 0.5:
        return "Content"
    elif -0.1 <= polarity <= 0.1:
        return "Neutral"
    elif -0.5 <= polarity < -0.1:
        return "Sad"
    else:
        return "Angry"

# Load the pre-trained conversational model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

# Maintain conversation history for context
conversation_history = {}

@login_required
def dashboard(request):
    """
    Render the dashboard with all historical data for chat history, mood analysis, and mood swings.
    If requested via AJAX, return JSON data for charts.
    """
    # Fetch all chat history and mood analysis for the logged-in user
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    mood_analysis = MoodAnalysis.objects.filter(user=request.user).order_by('timestamp')

    # Analyze mood swings
    mood_swings = []
    previous_mood = None
    for mood in mood_analysis:
        if previous_mood and previous_mood.mood != mood.mood:
            mood_swings.append({
                'from': previous_mood.mood, 
                'to': mood.mood, 
                'timestamp': mood.timestamp.isoformat()
            })
        previous_mood = mood

    # Return JSON data if requested via AJAX or with format=json parameter
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # Prepare JSON data
        mood_analysis_data = [{
            'timestamp': mood.timestamp.isoformat(),
            'mood': mood.mood
        } for mood in mood_analysis]
        
        return JsonResponse({
            'mood_analysis': mood_analysis_data,
            'mood_swings': mood_swings,
        })
    
    # Render HTML template for normal requests
    return render(request, 'chatbot/dashboard.html', {
        'chat_history': chat_history,
        'mood_analysis': mood_analysis,
        'mood_swings': mood_swings,
    })

@login_required
def chatbot(request):
    """
    Handle chat messages and dynamically update mood analysis and mood swings.
    """
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            message = data.get('message')
            facial_data = data.get('facial_data')
            
            if message:
                # Save the user's chat message
                chat_message = ChatMessage.objects.create(user=request.user, message=message, timestamp=now())
                chat_message.save()
                
                # Save facial expression data if available
                if facial_data and isinstance(facial_data, dict):  # Add type check
                    try:
                        facial_expression = FacialExpression.objects.create(
                            user=request.user,
                            expression=facial_data.get('expression', 'unknown'),
                            confidence=float(facial_data.get('confidence', 0.0)),
                            timestamp=now()
                        )
                        facial_expression.save()
                    except Exception as e:
                        print(f"Error saving facial data: {e}")
                        # Continue even if saving facial data fails
                
                # Perform text sentiment analysis
                analysis = TextBlob(message)
                polarity = analysis.sentiment.polarity
                text_emotion = classify_emotion(polarity)
                
                # Use text emotion as the default when facial data isn't available
                final_emotion = text_emotion
                
                # Update final emotion with facial data if available and valid
                if facial_data and isinstance(facial_data, dict) and 'expression' in facial_data:
                    # Map facial expressions to our emotion categories
                    facial_to_emotion = {
                        'happy': 'Happy',
                        'surprised': 'Content',
                        'neutral': 'Neutral',
                        'sad': 'Sad',
                        'angry': 'Angry',
                        'disgusted': 'Angry',
                        'fearful': 'Sad'
                    }
                    
                    facial_emotion = facial_to_emotion.get(
                        str(facial_data.get('expression', '')).lower(), 
                        text_emotion
                    )
                    
                    # If facial and text emotions disagree, trust facial with higher weight
                    confidence = float(facial_data.get('confidence', 0))
                    if facial_emotion != text_emotion and confidence > 0.65:
                        final_emotion = facial_emotion
                
                # Save the final emotion analysis
                mood_analysis = MoodAnalysis.objects.create(user=request.user, mood=final_emotion, timestamp=now())
                mood_analysis.save()
                
                # Generate a response considering both text and facial expressions
                response = generate_ai_response(request.user, message, facial_data)
                
                # Save the chatbot's response
                bot_message = ChatMessage.objects.create(user=request.user, message=response, timestamp=now())
                bot_message.save()

                # Fetch all mood analysis and mood swings
                mood_analysis = list(MoodAnalysis.objects.filter(user=request.user).values('timestamp', 'mood'))
                mood_swings = []
                previous_mood = None
                for mood in mood_analysis:
                    if previous_mood and previous_mood['mood'] != mood['mood']:
                        mood_swings.append({'from': previous_mood['mood'], 'to': mood['mood'], 'timestamp': mood['timestamp']})
                    previous_mood = mood

                # Return the bot's response and updated data as JSON
                return JsonResponse({
                    'response': response,
                    'mood_analysis': mood_analysis,
                    'mood_swings': mood_swings,
                })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def chatbot_page(request):
    """
    Render the dedicated chatbot interface page.
    """
    # Fetch chat history for the current user
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    
    return render(request, 'chatbot/chatbot_interface.html', {
        'chat_history': chat_history,
    })

def generate_ai_response(user, user_message, facial_data=None):
    """
    Generate a friendly and context-aware response using a conversational AI model.
    Consider facial expressions when available.
    """
    # Retrieve or initialize the conversation history for the user
    if user not in conversation_history:
        conversation_history[user] = []

    # Tokenize the input and append it to the conversation history
    new_user_input_ids = tokenizer.encode(user_message + tokenizer.eos_token, return_tensors="pt")
    conversation_history[user].append(new_user_input_ids)

    # Concatenate the conversation history
    bot_input_ids = torch.cat(conversation_history[user], dim=-1)

    # Generate a response
    bot_output = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

    # Decode the response and append it to the conversation history
    bot_response = tokenizer.decode(bot_output[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    conversation_history[user].append(bot_output)

    # Enhance the response with friendly and empathetic logic
    return enhance_response(user_message, bot_response, facial_data)

def enhance_response(user_message, bot_response, facial_data=None):
    """
    Enhance the chatbot's response to make it more friendly, empathetic, and engaging.
    Now considers facial expressions to detect potential discrepancies.
    """
    # Convert message to lowercase for easier matching
    user_message_lower = user_message.lower()
    
    # Check for discrepancy between text and facial expression
    if facial_data:
        text_seems_positive = any(word in user_message_lower for word in ['happy', 'good', 'great', 'awesome', 'nice'])
        text_seems_negative = any(word in user_message_lower for word in ['sad', 'bad', 'upset', 'angry', 'frustrated'])
        
        facial_expr = facial_data.get('expression', '').lower()
        facial_is_positive = facial_expr in ['happy', 'surprised']
        facial_is_negative = facial_expr in ['sad', 'angry', 'disgusted', 'fearful']
        
        # Detect potential discrepancy
        if (text_seems_positive and facial_is_negative and facial_data.get('confidence', 0) > 0.7):
            return "I notice that while your words sound positive, you seem to be feeling differently. Would you like to talk about what's really going on?"
        
        if (text_seems_negative and facial_is_positive and facial_data.get('confidence', 0) > 0.7):
            return "It seems like there might be more to how you're feeling than what you're saying. I'm here to listen if you want to share more."
    else:
        # Check if user mentioned camera issues
        if any(phrase in user_message_lower for phrase in ['camera not working', 'camera issue', 'cant see me', 
                                                         'camera denied', 'no camera', 'detection not working']):
            return "Don't worry about the camera - I'm still here to chat! What would you like to talk about today?"
    
    # Emotion-based responses
    if any(word in user_message_lower for word in ['sad', 'upset', 'unhappy', 'depressed']):
        return "I'm really sorry to hear that you're feeling down. Would you like to talk about what's bothering you? Sometimes sharing our feelings helps lighten the burden."
    
    if any(word in user_message_lower for word in ['happy', 'glad', 'joy', 'excited']):
        return "That's wonderful to hear! Your happiness is contagious. What's something specific that's bringing you joy today?"
    
    if any(word in user_message_lower for word in ['angry', 'mad', 'furious', 'upset']):
        return "I can sense you're feeling frustrated. That's completely valid. Would it help to talk through what's causing these feelings? I'm here to listen without judgment."
    
    # Greeting responses
    if any(word in user_message_lower for word in ['hi', 'hello', 'hey', 'greetings']):
        return "Hi there! It's great to connect with you today. How are you feeling right now? I'm here to chat about anything that's on your mind."
    
    # Questions about the chatbot
    if "what are you" in user_message_lower or "who are you" in user_message_lower:
        return "I'm your friendly AI companion, designed to chat with you and help track your emotions. Think of me as a friend who's always ready to listen. How can I support you today?"
    
    if "how are you" in user_message_lower:
        return "Thanks for asking! I'm here and ready to be helpful. More importantly, how are YOU doing today? I'd love to hear about your day."
    
    # Personal questions
    if any(phrase in user_message_lower for phrase in ["about me", "know about me", "tell me about myself"]):
        return "I know we've been chatting and I'm tracking your mood patterns to help you understand your emotional trends. What else would you like to share about yourself? I'd love to get to know you better."
    
    # Activity-related responses
    if any(word in user_message_lower for word in ["bored", "boring", "nothing to do"]):
        return "Feeling a bit bored? How about trying something creative like drawing, writing, or maybe going for a walk? Sometimes a change of scenery can spark new energy. What kinds of activities do you usually enjoy?"
    
    if "not doing anything" in user_message_lower:
        return "Sometimes taking time to just be is important too. It gives us space to think and reflect. Is there something specific you'd like to chat about during this downtime?"
    
    # Help-seeking responses
    if any(phrase in user_message_lower for phrase in ["help me", "need help", "can you help"]):
        return "I'm absolutely here to help. What specific kind of support are you looking for today? Whether it's just chatting or something more specific, I'll do my best."
    
    # Opinion-seeking responses
    if "what do you think" in user_message_lower:
        return "That's an interesting question! While I don't have personal opinions in the same way humans do, I can help you explore different perspectives on this topic. What are your thoughts so far?"
    
    # General fallback with more personality
    if len(bot_response.strip()) < 5 or bot_response == "I don't know.":
        return "That's an interesting point. Could you tell me more about what you mean? I'm curious to understand your perspective better."
    
    # Default to the AI-generated response if none of the above conditions are met
    return bot_response

@login_required
def logout_view(request):
    """
    Log the user out and redirect to the home page.
    """
    logout(request)
    return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to the dashboard after successful login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'chatbot/login.html')  # Render the login page for GET requests or failed login

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'chatbot/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'chatbot/register.html')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('login')  # Redirect to the login page after successful registration

    return render(request, 'chatbot/register.html')  # Render the registration page for GET requests

def home(request):
    """
    Render the landing page.
    """
    # Prepare context with project description - keeping it under 350 characters
    context = {
        'project_name': 'MoodMate',
        'tagline': 'Your AI Companion for Emotional Wellness',
        'description': 'MoodMate is an AI-powered emotional intelligence platform that combines text sentiment analysis with facial expression recognition to understand emotions, track mood patterns, and provide empathetic responses.',
        'features': [
            {
                'title': 'Dual-Analysis Technology',
                'description': 'Text + facial analysis for deeper emotional understanding'
            },
            {
                'title': 'Mood Tracking',
                'description': 'Visualize emotional patterns over time'
            },
            {
                'title': 'Empathetic Conversations',
                'description': 'AI companion with emotional intelligence'
            },
            {
                'title': 'Privacy-Focused',
                'description': 'Secure data with optional camera usage'
            }
        ]
    }
    
    return render(request, 'chatbot/home.html', context)
