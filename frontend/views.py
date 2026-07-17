from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import login
from tasks.models import Task
from tasks.views import GenerateDescriptionMinThrottle, GenerateDescriptionDayThrottle
from tasks.services import get_description_service
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .forms import CustomUserCreationForm, CustomAuthenticationForm, TaskForm

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([GenerateDescriptionMinThrottle, GenerateDescriptionDayThrottle])
def generate_description_api(request):
    title = request.data.get('title', '')
    description = request.data.get('description', '')
    
    if not title:
        return Response({'success': False, 'message': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        service = get_description_service()
        generated_text = service.generate(title, description)
        return Response({
            'success': True,
            'message': 'Description generated successfully',
            'data': {'description': generated_text}
        })
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "task_form.html"
    success_url = reverse_lazy("task_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "task_form.html"
    success_url = reverse_lazy("task_list")

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "task_confirm_delete.html"
    success_url = reverse_lazy("task_list")

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

class TaskListView(LoginRequiredMixin, ListView):
    template_name = "task_list.html"
    model = Task
    context_object_name = "tasks"
    login_url = "login"

    def get_paginate_by(self, queryset):
        limit = self.request.GET.get('limit', '10')
        try:
            return int(limit)
        except ValueError:
            return 10

    def get_queryset(self):
        qs = Task.objects.filter(owner=self.request.user)
        
        status = self.request.GET.get('status')
        if status in ['pending', 'done']:
            qs = qs.filter(status=status)
            
        sort_by = self.request.GET.get('sort_by')
        order = self.request.GET.get('order')
        
        valid_sort_fields = ['created_at', 'updated_at', 'title', 'status']
        if sort_by in valid_sort_fields:
            if order == 'desc':
                qs = qs.order_by(f"-{sort_by}")
            else:
                qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by("-created_at")
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['current_sort_by'] = self.request.GET.get('sort_by', 'created_at')
        context['current_order'] = self.request.GET.get('order', 'desc')
        context['current_limit'] = self.request.GET.get('limit', '10')
        return context

class RegisterView(CreateView):
    template_name = "register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("task_list")
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class CustomLoginView(LoginView):
    template_name = "login.html"
    form_class = CustomAuthenticationForm
    
    def get_success_url(self):
        return reverse_lazy("task_list")
