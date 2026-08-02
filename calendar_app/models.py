import uuid
from django.db import models


def generate_id():
    return uuid.uuid4().hex



class Event(models.Model):
    id = models.UUIDField(default=generate_id, primary_key=True, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    employee_id = models.IntegerField()

    #Employee fue removido.
    
    def __str__(self):
        return self.title


