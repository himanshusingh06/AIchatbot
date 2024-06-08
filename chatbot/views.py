from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import google.generativeai as genai
from dotenv import load_dotenv
import os
from django.utils import timezone
from .models import Chat

# Load environment variables
load_dotenv()

# Configure API key
gapi_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gapi_key)

def to_markdown(text):
    text = text.replace('•', '  *')
    return text  # Simplified to return plain text for debugging

# Register view
def register(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('f_name')
        last_name = request.POST.get('l_name')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        # Check if username or email already exists
        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists!")
            return redirect('login')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('login')
        elif pass1 != pass2:
            messages.error(request, "Your password and confirm password are not the same!")
            return redirect('login')
        else:
            # Create new user
            my_user = User(username=uname, email=email, first_name=first_name, last_name=last_name)
            my_user.set_password(pass1)  # Use set_password() to properly hash the password
            my_user.save()
            messages.success(request, "Your account has been created successfully!")
            return redirect('login')

# Login view
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if user exists
        if user is None:
            messages.error(request, "Invalid UserName or Password.")
        else:
            # User exists, check password
            if user.check_password(password):
                # Password is correct, log in user
                auth.login(request, user)
                return redirect('home')
            else:
                # Incorrect password
                messages.error(request, "Invalid UserName or Password.")


    return render(request, 'login.html')

# Logout view
def logout(request):
    auth.logout(request)
    return redirect('home')

# Home view
def home(request):
    user = request.user if request.user.is_authenticated else None
    return render(request, 'landing.html', {'user': user})

# Chatbot view
@login_required(login_url='login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user).order_by('created_at')
    if request.method == 'POST':
        message = request.POST.get('message')
        history = [{"role": "user", "content": chat.message} for chat in chats] + \
                  [{"role": "model", "content": chat.response} for chat in chats]
        response = ask_genai(message, history)
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})

# Ask GenAI function
def ask_genai(message, history):
    try:
        # Ensure history has the correct format
        formatted_history = []
        for entry in history:
            formatted_history.append({
                "role": entry["role"],
                "parts": [{"text": entry["content"]}]
            })

        # Add the current user message to the formatted history
        formatted_history.append({
            "role": "user",
            "parts": [{"text": message}]
        })

        # Initialize the model and create the chat session with the formatted history
        model = genai.GenerativeModel('gemini-1.5-flash')
        chat_session = model.start_chat(history=formatted_history)

        # Send a message to the chat session
        response = chat_session.send_message(message)

        # Get the response text
        answer = response.text
        
        # Convert to markdown if needed (simplified for debugging)
        markdown_response = to_markdown(answer)
        return markdown_response
    except Exception as e:
        return f"Error: {e}"

# Generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)
