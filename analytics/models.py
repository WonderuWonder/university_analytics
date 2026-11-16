from django.db import models

class Group(models.Model):
    name = models.CharField("Название группы", max_length=50)

    def __str__(self):
        return self.name

class Student(models.Model):
    full_name = models.CharField("ФИО", max_length=150)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа")

    def __str__(self):
        return self.full_name

class Subject(models.Model):
    title = models.CharField("Дисциплина", max_length=100)

    def __str__(self):
        return self.title

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Студент")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Дисциплина")
    value = models.IntegerField("Оценка")
    date = models.DateField("Дата")

    def __str__(self):
        return f"{self.student} - {self.subject}: {self.value}"