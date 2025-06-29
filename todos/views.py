from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Todo
from django.http import HttpResponseRedirect
from datetime import datetime, date
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'todos/index.html'
    context_object_name = 'todo_list'
    login_url = '/todos/login/'

    def get_queryset(self):
        """Return filtered todos based on filter parameter and user."""
        filter_type = self.request.GET.get('filter', 'all')
        queryset = Todo.objects.filter(user=self.request.user)
        
        if filter_type == 'overdue':
            queryset = queryset.filter(due_date__lt=date.today())
        elif filter_type == 'due-today':
            queryset = queryset.filter(due_date=date.today())
        elif filter_type == 'upcoming':
            queryset = queryset.filter(due_date__gt=date.today())
        # 'all' shows all todos for the user
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add filter_type to context for template."""
        context = super().get_context_data(**kwargs)
        context['filter_type'] = self.request.GET.get('filter', 'all')
        return context

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('todos:index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'todos/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('todos:index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # Handle validation errors
            if 'password' in form.errors:
                if 'This field is required.' in str(form.errors['password']):
                    messages.error(request, 'Password is required.')
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'todos/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('todos:login')

@login_required(login_url='/todos/login/')
def add(request):
    title = request.POST['title']
    due_date_str = request.POST.get('due_date', '')
    
    # Create todo with optional due date and user
    todo = Todo.objects.create(title=title, user=request.user)
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            todo.due_date = due_date
            todo.save()
        except ValueError:
            # If date parsing fails, just create without due date
            pass

    return redirect('todos:index')

@login_required(login_url='/todos/login/')
def delete(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    todo.delete()
    return redirect('todos:index')

@login_required(login_url='/todos/login/')
def update(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)
    isCompleted = request.POST.get('isCompleted', False)
    due_date_str = request.POST.get('due_date', '')
    
    if isCompleted == 'on':
        isCompleted = True
    
    todo.isCompleted = isCompleted
    
    # Update due date if provided
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            todo.due_date = due_date
        except ValueError:
            # If date parsing fails, keep existing due date
            pass
    else:
        todo.due_date = None

    todo.save()
    return redirect('todos:index')