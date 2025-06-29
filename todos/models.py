from django.db import models
from datetime import date
from django.contrib.auth.models import User

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField('Created', auto_now_add=True)
    update_at = models.DateTimeField('Updated', auto_now=True)
    isCompleted = models.BooleanField(default=False)
    due_date = models.DateField('Due Date', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_due_status(self):
        """Return the status of the due date for styling"""
        if not self.due_date:
            return 'no-due-date'
        
        today = date.today()
        if self.due_date < today:
            return 'overdue'
        elif self.due_date == today:
            return 'due-today'
        else:
            return 'upcoming'
