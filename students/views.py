from django.shortcuts import render,redirect
from django.db.models import Q
from .models import Student,Mark
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


@login_required
def student_list(request):
    students = Student.objects.filter(user=request.user).order_by('pin')
    q = request.GET.get('q', '').strip()
    if q:
        students = students.filter(Q(name__icontains=q) | Q(pin__icontains=q))
    return render(request, 'students/student_list.html', {'students': students, 'q': q})

@login_required
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        pin = request.POST.get('pin')
        age = request.POST.get('age')

        Student.objects.create(
        user=request.user,
        name=name,
        pin=pin,
        age=age
    )

        return redirect('student_list')

    return render(request, 'students/add_student.html')

@login_required
def student_detail(request, id):

    student = Student.objects.get(id=id)

    marks = student.mark_set.all()

    total = 0

    for mark in marks:
        total += mark.marks

    return render(request, 'students/student_detail.html', {
        'student': student,
        'marks': marks,
        'total': total
    })

def add_mark(request, id):
    student = Student.objects.get(id=id)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        marks = request.POST.get('marks')

        Mark.objects.create(
            student=student,
            subject=subject,
            marks=marks
        )

        return redirect('student_detail', id=student.id)

    return render(request, 'students/add_mark.html', {'student': student})

@login_required
def delete_student(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return redirect('student_list')

@login_required
def edit_student(request, id):
    student = Student.objects.get(id=id)
    marks = student.mark_set.all()

    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.age = request.POST.get('age')
        student.pin = request.POST.get('pin')
        student.save()

        for mark in marks:
            subject = request.POST.get(f'subject_{mark.id}')
            score = request.POST.get(f'marks_{mark.id}')

            mark.subject = subject
            mark.marks = score
            mark.save()

        new_subjects = request.POST.getlist('new_subject')
        new_scores = request.POST.getlist('new_marks')

        for subject, score in zip(new_subjects, new_scores):
            if subject and score:
                Mark.objects.create(
                    student=student,
                    subject=subject,
                    marks=score
                )

        return redirect('student_detail', id=student.id)

    return render(request, 'students/edit_student.html', {
        'student': student,
        'marks': marks
    })

def register_user(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

    return render(request, 'students/register.html')

def login_user(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('student_list')

    return render(request, 'students/login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')
