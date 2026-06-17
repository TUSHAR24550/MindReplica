import json
import requests

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# =========================
# AUTHENTICATION VIEWS
# =========================

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect("login")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "accounts/login.html")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, f"Account created successfully. Welcome, {user.username}!")
        return redirect("home")

    return render(request, "accounts/signup.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# =========================
# AI CHAT (OLLAMA)
# =========================

OLLAMA_API_URL = "http://localhost:11434/api/generate"

@csrf_exempt
@login_required
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "Message cannot be empty."}, status=400)

        payload = {
            "model": "phi3",
            "prompt": f"You are Tushar’s AI twin. Talk casually.\nUser: {user_message}\nAI:",
            "stream": False
        }

        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=120
        )

        result = response.json()
        ai_reply = result.get("response", "").strip()

        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        print("AI ERROR:", e)
        return JsonResponse(
            {"reply": "AI is thinking... please try again."},
            status=500 
        )


@login_required
def chat_page(request):
    return render(request, "chat.html")