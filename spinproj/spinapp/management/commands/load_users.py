import csv
from django.core.management.base import BaseCommand
from spinapp.models import User, AssignedHouse 
import os
from django.conf import settings

class Command(BaseCommand):
    help = "Load users and house numbers from a CSV file"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.MEDIA_ROOT, "data/house_user_list.csv")  

        try:
            with open(file_path, "r") as file:
                reader = csv.reader(file)
                next(reader)  

                for row in reader:
                    email, house_number = row

                    
                    if AssignedHouse.objects.filter(house_number=house_number).exists():
                        self.stdout.write(self.style.WARNING(f"House {house_number} is already assigned! Skipping..."))
                        continue  

                   
                    user, created = User.objects.get_or_create(email=email, defaults={"name": email.split('@')[0], "age": 25})

                   
                    AssignedHouse.objects.create(user=user, house_number=house_number)
                    self.stdout.write(self.style.SUCCESS(f"Assigned House {house_number} to {email}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("CSV file not found!"))