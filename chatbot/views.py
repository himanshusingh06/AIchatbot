from django.contrib import messages
from django.shortcuts import render,HttpResponse,redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

from .models import Chat
from django.http import JsonResponse
import google.generativeai as genai
from dotenv import load_dotenv
import os
import textwrap
from django.utils import timezone
from IPython.display import Markdown
# Create your views here.

load_dotenv()

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


gapi_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gapi_key)


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

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pass')
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        # Check if user exists
        if user is None:
            # Username does not exist
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

def logout(request):
    auth.logout(request)
    return redirect('home')



# Create your views here.
def home (request):
    user = request.user if request.user.is_authenticated else None
    return render(request,'landing.html',{'user': user})







@login_required(login_url='login')
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_genai(message)
        chat=Chat(user=request.user,message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html',{'chats':chats})





def ask_genai(message):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(message)
        answer = response.text
        
        # Convert to markdown if needed
        markdown_response = to_markdown(answer)
        return answer
    except Exception as e:
        return f"Error: {e}"
