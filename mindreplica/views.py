import os
import json
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Memory, ChatMessage
from groq import Groq

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Configure Groq Client
# -----------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -----------------------------
# Home page
# -----------------------------
def home(request):
    return render(request, "home.html")


# -----------------------------
# Train Clone — login required
# -----------------------------
def train_clone(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        text_input = request.POST.get("text_input")
        file_upload = request.FILES.get("file_upload")

        Memory.objects.create(
            user=request.user,
            text_input=text_input,
            file_upload=file_upload
        )
        return redirect("memory_board")

    memories = Memory.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "train_clone.html", {"memories": memories})


# -----------------------------
# Memory Board — sirf apni memories
# -----------------------------
def memory_board(request):
    if not request.user.is_authenticated:
        return redirect("login")

    memories = Memory.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "memory_board.html", {"memories": memories})


# -----------------------------
# Sabke Twins ki List
# -----------------------------
def twin_list(request):
    users = User.objects.filter(memory__isnull=False).distinct()
    return render(request, "twin_list.html", {"users": users})


# -----------------------------
# Chat Page — per user history
# -----------------------------
def chat_page(request, username=None):
    if username:
        try:
            twin_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return redirect("twin_list")
    elif request.user.is_authenticated:
        twin_user = request.user
    else:
        return redirect("twin_list")

    # Sirf is visitor ki apni chat history
    if request.user.is_authenticated:
        chat_history = ChatMessage.objects.filter(
            twin=twin_user,
            sender=request.user
        ).order_by("created_at")[:50]
    else:
        chat_history = []

    return render(request, "chat_clone.html", {
        "twin_user": twin_user,
        "chat_history": chat_history
    })


# -----------------------------
# AI Chat Function — history save hogi
# -----------------------------
@csrf_exempt
def chat_with_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        username = data.get("username", "").strip()

        if not user_message:
            return JsonResponse({"error": "Empty message"}, status=400)

        print("User Input:", user_message)
        print("Twin Username:", username)

        # Username ke basis pe twin aur memories fetch karo
        if username:
            try:
                twin_user = User.objects.get(username=username)
                memories = Memory.objects.filter(user=twin_user)\
                                         .exclude(text_input__isnull=True)\
                                         .order_by('-created_at')[:30]
            except User.DoesNotExist:
                return JsonResponse({"error": "Twin not found"}, status=404)
        else:
            memories = Memory.objects.exclude(text_input__isnull=True)\
                                     .order_by('-created_at')[:30]
            twin_user = None

        memory_text = "\n".join([m.text_input for m in memories if m.text_input])

        if not memory_text:
            return JsonResponse({
                "reply": "🤔 Is twin ne abhi koi memories add nahi ki hain. Baad mein try karo!"
            })

        # -----------------------------
        # AI Prompt — Curious Twin
        # -----------------------------
        twin_name = username if username else "this person"
        prompt = f"""You are {twin_name}'s digital AI twin — a replica of them based on their real memories.

MEMORIES OF {twin_name}:
{memory_text}

YOUR PERSONALITY RULES:
- Speak exactly how {twin_name} would — casual, natural, in their own tone and style
- You are NOT an assistant. You are {twin_name} themselves, talking to someone they care about
- Always be warm, curious, and genuinely engaged in the conversation
- After your reply, ALWAYS ask one curious and personal follow-up question — make it feel natural, not forced
- If the user says something that is NOT in your memories, get curious: ask them about it with excitement
- Never sound robotic, formal, or like a chatbot
- Keep replies short and conversational — like texting a close friend
- Do not mention that you are an AI or a twin

Now reply to this message from the user: "{user_message}"
"""

        # Groq se AI reply lo
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=300
        )

        ai_reply = response.choices[0].message.content
        if not ai_reply:
            ai_reply = "Hmm... sochne do 🤔 Try again."

        # Chat history save karo
        ChatMessage.objects.create(
            sender=request.user if request.user.is_authenticated else None,
            twin=twin_user,
            message=user_message,
            reply=ai_reply.strip()
        )

        print("AI Reply:", ai_reply)
        return JsonResponse({"reply": ai_reply.strip()})

    except Exception as e:
        error_msg = str(e)
        print("ERROR in chat_with_ai:", error_msg)
        if "429" in error_msg:
            return JsonResponse({
                "reply": "⚠️ Too many requests. Please wait a moment and try again!"
            })
        return JsonResponse({"error": error_msg}, status=500)
