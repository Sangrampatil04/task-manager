from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from datetime import date
from django.conf import settings

from .models import Task


# ---------------- HOME ----------------
def home(request):
    return redirect('dashboard')


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):
    # CREATE TASK
    if request.method == "POST":
        title = request.POST.get("title")
        priority = request.POST.get("priority")
        due_date = request.POST.get("due_date")

        Task.objects.create(
            title=title,
            priority=priority,
            due_date=due_date if due_date else None,
            user=request.user
        )
        return redirect("dashboard")

    # FILTER TASKS
    filter_type = request.GET.get("filter", "all")
    tasks = Task.objects.filter(user=request.user)

    if filter_type == "completed":
        tasks = tasks.filter(completed=True)
    elif filter_type == "pending":
        tasks = tasks.filter(completed=False)
    elif filter_type == "overdue":
        tasks = tasks.filter(completed=False, due_date__lt=date.today())

    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    pending_tasks = total_tasks - completed_tasks

    progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks else 0

    return render(request, "tasks/dashboard.html", {
        "tasks": tasks,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "progress_percent": progress_percent,
        "filter_type": filter_type
    })


# ---------------- EDIT TASK ----------------
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.priority = request.POST.get("priority")
        task.due_date = request.POST.get("due_date")
        task.save()
        return redirect("dashboard")

    return render(request, "tasks/edit_task.html", {"task": task})


# ---------------- COMPLETE TASK ----------------
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = True
    task.save()
    return redirect("dashboard")


# ---------------- DELETE TASK ----------------
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect("dashboard")


# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        send_mail(
            "Welcome to Task Manager",
            "Your account has been created successfully.",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True,
        )

        login(request, user)
        return redirect("dashboard")

    return render(request, "tasks/signup.html")


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid credentials")
        return redirect("login")

    return render(request, "tasks/login.html")


# ---------------- LOGOUT ----------------
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- REMINDERS ----------------
def send_task_reminders():
    today = date.today()
    tasks = Task.objects.filter(due_date=today, completed=False)

    for task in tasks:
        if task.user.email:
            send_mail(
                "⏰ Task Reminder",
                f"Reminder: '{task.title}' is due today.",
                settings.EMAIL_HOST_USER,
                [task.user.email],
                fail_silently=True,
            )


@login_required
def test_reminder(request):
    send_task_reminders()
    return HttpResponse("Reminders sent")
