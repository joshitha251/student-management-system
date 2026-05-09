from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)

    pin = models.CharField(max_length=20)

    age = models.IntegerField()

    def __str__(self):
        return self.name


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.name} - {self.subject}"