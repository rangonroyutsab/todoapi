import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'todoapi.settings')
django.setup()

from tasks.models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

def run_seeder():
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'testuser@example.com'}
    )
    if created:
        user.set_password('Password123!')
        user.save()
        print("Created new user: testuser")

    with open('tasks_data.json', 'r') as f:
        tasks_data = json.load(f)

    tasks_to_create = []
    for item in tasks_data:
        tasks_to_create.append(Task(
            owner=user,
            title=item.get('title'),
            description=item.get('description', ''),
            status=item.get('status', 'pending')
        ))
    
    Task.objects.bulk_create(tasks_to_create)
    print(f"Successfully inserted {len(tasks_to_create)} tasks into the database.")

if __name__ == '__main__':
    run_seeder()
