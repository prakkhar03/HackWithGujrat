from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    occupation = models.CharField(max_length=255, blank=True, null=True)
    monthly_income = models.FloatField(default=0)
    savings_goal = models.FloatField(default=0)
    risk_tolerance = models.CharField(max_length=50, default='medium', 
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    investment_goals = models.TextField(blank=True, null=True)
    total_expenditure = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class BankStatement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='statements/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Statement - {self.uploaded_at}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - ₹{self.amount}"

class ChatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Chat - {self.created_at}"
