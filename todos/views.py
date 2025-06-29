from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from .models import Todo
from django.http import HttpResponseRedirect
from datetime import datetime, date

class IndexView(generic.ListView):
    template_name = 'todos/index.html'
    context_object_name = 'todo_list'

    def get_queryset(self):
        """Return filtered todos based on filter parameter."""
        filter_type = self.request.GET.get('filter', 'all')
        queryset = Todo.objects.all()
        
        if filter_type == 'overdue':
            queryset = queryset.filter(due_date__lt=date.today())
        elif filter_type == 'due-today':
            queryset = queryset.filter(due_date=date.today())
        elif filter_type == 'upcoming':
            queryset = queryset.filter(due_date__gt=date.today())
        # 'all' shows all todos
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add filter_type to context for template."""
        context = super().get_context_data(**kwargs)
        context['filter_type'] = self.request.GET.get('filter', 'all')
        return context

def add(request):
    title = request.POST['title']
    due_date_str = request.POST.get('due_date', '')
    
    # Create todo with optional due date
    todo = Todo.objects.create(title=title)
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            todo.due_date = due_date
            todo.save()
        except ValueError:
            # If date parsing fails, just create without due date
            pass

    return redirect('todos:index')

def delete(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    todo.delete()

    return redirect('todos:index')

def update(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
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