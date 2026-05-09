from django.shortcuts import render,redirect, get_object_or_404
from django.db.models import Q
from .models import Student,Mark
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache


@never_cache
@login_required
def student_list(request):
    students = Student.objects.filter(user=request.user).order_by('pin')
    q = request.GET.get('q', '').strip()
    if q:
        students = students.filter(Q(name__icontains=q) | Q(pin__icontains=q))
    return render(request, 'students/student_list.html', {'students': students, 'q': q})

@never_cache
@login_required
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        pin = request.POST.get('pin', '').strip()
        age = request.POST.get('age')

        if Student.objects.filter(user=request.user, pin=pin).exists():
            messages.error(request, 'Student PIN already exists. Please use a unique PIN.')
            return redirect('add_student')

        Student.objects.create(user=request.user, name=name, pin=pin, age=age)
        messages.success(request, 'Student added successfully.')

        return redirect('student_list')

    return render(request, 'students/add_student.html')

@never_cache
@login_required
def student_detail(request, id):

    student = get_object_or_404(Student, id=id, user=request.user)

    marks = student.mark_set.all()

    total = 0

    for mark in marks:
        total += mark.marks

    return render(request, 'students/student_detail.html', {
        'student': student,
        'marks': marks,
        'total': total
    })

@never_cache
@login_required
def add_mark(request, id):
    student = get_object_or_404(Student, id=id, user=request.user)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        marks = request.POST.get('marks')

        try:
            marks_value = int(marks)
        except (TypeError, ValueError):
            messages.error(request, 'Marks must be a valid number between 0 and 100.')
            return redirect('add_mark', id=student.id)

        if marks_value < 0 or marks_value > 100:
            messages.error(request, 'Marks must be between 0 and 100.')
            return redirect('add_mark', id=student.id)

        Mark.objects.create(
            student=student,
            subject=subject,
            marks=marks_value
        )
        messages.success(request, 'Mark added successfully.')

        return redirect('student_detail', id=student.id)

    return render(request, 'students/add_mark.html', {'student': student})

@never_cache
@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id, user=request.user)
    student.delete()
    messages.success(request, 'Student deleted successfully.')
    return redirect('student_list')

@never_cache
@login_required
def edit_student(request, id):
    student = get_object_or_404(Student, id=id, user=request.user)
    marks = student.mark_set.all()

    if request.method == 'POST':
        student.name = request.POST.get('name', '').strip()
        student.age = request.POST.get('age')
        new_pin = request.POST.get('pin', '').strip()

        if Student.objects.filter(user=request.user, pin=new_pin).exclude(id=student.id).exists():
            messages.error(request, 'Student PIN already exists. Please use a unique PIN.')
            return redirect('edit_student', id=student.id)

        student.pin = new_pin
        student.save()

        for mark in marks:
            subject = request.POST.get(f'subject_{mark.id}', '').strip()
            score = request.POST.get(f'marks_{mark.id}')

            try:
                score_value = int(score)
            except (TypeError, ValueError):
                messages.error(request, 'Each mark must be a valid number between 0 and 100.')
                return redirect('edit_student', id=student.id)

            if score_value < 0 or score_value > 100:
                messages.error(request, 'Each mark must be between 0 and 100.')
                return redirect('edit_student', id=student.id)

            mark.subject = subject
            mark.marks = score_value
            mark.save()

        new_subjects = request.POST.getlist('new_subject')
        new_scores = request.POST.getlist('new_marks')

        for subject, score in zip(new_subjects, new_scores):
            if subject and score:
                try:
                    score_value = int(score)
                except (TypeError, ValueError):
                    messages.error(request, 'New marks must be valid numbers between 0 and 100.')
                    return redirect('edit_student', id=student.id)

                if score_value < 0 or score_value > 100:
                    messages.error(request, 'New marks must be between 0 and 100.')
                    return redirect('edit_student', id=student.id)

                Mark.objects.create(
                    student=student,
                    subject=subject.strip(),
                    marks=score_value
                )

        messages.success(request, 'Student updated successfully.')
        return redirect('student_detail', id=student.id)

    return render(request, 'students/edit_student.html', {
        'student': student,
        'marks': marks
    })

@never_cache
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        # Create the user if the username is unique
        User.objects.create_user(
            username=username,
            password=password
        )
        messages.success(request, 'User registered successfully.')
        return redirect('login')

    # Render the registration page for GET requests
    return render(request, 'students/register.html')
    
    
    

@never_cache
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'User does not exist. Please register first.')
            return redirect('login')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('student_list')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    # Render the login page for GET requests
    return render(request, 'students/login.html')


@never_cache
@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


def error_400(request, exception):
    return render(request, 'students/error.html', {'code': 400, 'message': 'Bad request.'}, status=400)


def error_403(request, exception):
    return render(request, 'students/error.html', {'code': 403, 'message': 'You are not allowed to access this page.'}, status=403)


def error_404(request, exception):
    return render(request, 'students/error.html', {'code': 404, 'message': 'The page you are looking for was not found.'}, status=404)


def error_500(request):
    return render(request, 'students/error.html', {'code': 500, 'message': 'Something went wrong on our side.'}, status=500)
