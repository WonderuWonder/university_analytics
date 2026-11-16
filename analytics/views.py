from django.shortcuts import render
from django.db.models import Avg, Count
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from .models import Grade, Student, Group, Subject


# --- Вспомогательный класс для стилизации форм Bootstrap ---
class BootstrapFormMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field in form.fields.values():
            if field.widget.__class__.__name__ in ['Select', 'SelectMultiple']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        return form


# --- 1. Дашборд ---
def dashboard(request):
    total_students = Student.objects.count()
    avg_grade_query = Grade.objects.aggregate(Avg('value'))
    total_avg = round(avg_grade_query['value__avg'], 2) if avg_grade_query['value__avg'] else 0.0
    failed_count = Grade.objects.filter(value=2).count()

    subjects_data = Grade.objects.values('subject__title').annotate(avg_grade=Avg('value'))
    bar_labels = [item['subject__title'] for item in subjects_data]
    bar_data = [round(item['avg_grade'], 2) for item in subjects_data]

    grades_dist = Grade.objects.values('value').annotate(count=Count('value')).order_by('value')
    pie_labels = [f"Оценка {item['value']}" for item in grades_dist]
    pie_data = [item['count'] for item in grades_dist]

    context = {
        'total_students': total_students,
        'total_avg': total_avg,
        'failed_count': failed_count,
        'bar_labels': bar_labels,
        'bar_data': bar_data,
        'pie_labels': pie_labels,
        'pie_data': pie_data,
    }
    return render(request, 'analytics/dashboard.html', context)


# --- 2. Списки ---
class StudentListView(ListView):
    model = Student
    template_name = 'analytics/student_list.html'
    context_object_name = 'students'


class GroupListView(ListView):
    model = Group
    template_name = 'analytics/group_list.html'
    context_object_name = 'groups'


class SubjectListView(ListView):
    model = Subject
    template_name = 'analytics/subject_list.html'
    context_object_name = 'subjects'


class GradeListView(ListView):
    model = Grade
    template_name = 'analytics/grade_list.html'
    context_object_name = 'grades'

    def get_queryset(self):
        return Grade.objects.select_related('student', 'subject').all()


# --- 3. Студенты (Добавление, Профиль, Удаление) ---
class StudentCreateView(BootstrapFormMixin, CreateView):
    model = Student
    fields = ['full_name', 'group']
    template_name = 'analytics/student_form.html'
    success_url = reverse_lazy('student_list')


class StudentDetailView(DetailView):
    model = Student
    template_name = 'analytics/student_detail.html'
    context_object_name = 'student'

    # Добавляем оценки студента в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = self.object.grade_set.select_related('subject').all()
        return context


class StudentDeleteView(DeleteView):
    model = Student
    template_name = 'analytics/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')


# --- 4. Дисциплины и Оценки (Добавление) ---
class SubjectCreateView(BootstrapFormMixin, CreateView):
    model = Subject
    fields = ['title']
    template_name = 'analytics/subject_form.html'
    success_url = reverse_lazy('subject_list')


class GradeCreateView(BootstrapFormMixin, CreateView):
    model = Grade
    fields = ['student', 'subject', 'value', 'date']
    template_name = 'analytics/grade_form.html'
    success_url = reverse_lazy('grade_list')


# --- 5. Заглушки ---
def reports_view(request):
    return render(request, 'analytics/reports.html')


def analytics_view(request):
    return render(request, 'analytics/analytics.html')


def settings_view(request):
    return render(request, 'analytics/settings.html')