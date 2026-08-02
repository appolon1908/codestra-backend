import uuid
import string
import random
from django.db import models
# from django.contrib.auth.models import User
from auth_app.models import User




def generate_id():
    return uuid.uuid4().hex

def generate_employee_id():
    return ''.join(random.choices(string.digits, k=6))


TEAM_PREFIXES = {
    'dev team': 'DV_',
    'design team': 'DS_',
    'biz dev team': 'BZ_',
    'test team': 'TS_',
    'mkt team': 'MK_',
    'tech team': 'TC_'
}

def generate_employee_id_with_prefix(team):
    if not team:  # Check if team is None or empty
        prefix = 'XX_'  # Default prefix for missing team
    else:
        prefix = TEAM_PREFIXES.get(team.lower(), team[:2].upper() + '_')
    return prefix + ''.join(random.choices(string.digits, k=6))

class Employee(models.Model):
    id = models.CharField(primary_key=True, editable=False, default=generate_id, max_length=70)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile/images/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    country = models.CharField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    team = models.CharField(max_length=256, null=True, blank=True)
    role = models.CharField(max_length=256, null=True, blank=True)
    employee_id = models.CharField(max_length=256, editable=False, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Only generate employee_id if it's not already set
        if not self.employee_id and self.team:
            self.employee_id = generate_employee_id_with_prefix(self.team)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name
    
    

class SocialMedia(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name="social_media_profiles"
    )
    name = models.CharField(max_length=100)  # e.g., Instagram, Twitter
    link = models.URLField()  # e.g., https://instagram.com/username

    def __str__(self):
        return f"{self.name} - {self.employee.first_name} {self.employee.last_name}"
    
    


class Career(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Requirement(models.Model):
    career = models.ForeignKey(Career, related_name="requirements", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.description

class Question(models.Model):
    SINGLE_CHOICE = 'SINGLE_CHOICE'
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE'
    TEXT = 'TEXT'

    QUESTION_TYPES = [
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (TEXT, 'Text'),
    ]

    career = models.ForeignKey(Career, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES)

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(Option, blank=True)  # For multiple-choice
    text_answer = models.TextField(blank=True, null=True)  # For text answers
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question.text}"
    

class CareerApplication(models.Model):
    id = models.CharField(
        primary_key=True, 
        editable=False, default=generate_id, max_length=70
    )
    career = models.ForeignKey(Career, on_delete=models.DO_NOTHING, null=True, blank=True)
    user_id = models.FileField(upload_to="career/", null=True, blank=True)
    resume = models.FileField(upload_to="career/", null=True, blank=True)
    
    full_name = models.CharField(max_length=256)
    email = models.EmailField(max_length=256)
    primary_profession = models.CharField(max_length=256, null=True, blank=True)
    project_link = models.CharField(max_length=256, null=True, blank=True)
    github_repo = models.CharField(max_length=256, null=True, blank=True)
    
    