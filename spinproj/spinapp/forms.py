# forms.py
from django import forms
from .models import AssignedHouse, User

class AssignHouseForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")
    house_number = forms.IntegerField(label="Enter House Number")

    class Meta:
        model = AssignedHouse
        fields = ['user', 'house_number']
