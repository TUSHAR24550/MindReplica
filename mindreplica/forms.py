from django import forms
from .models import Memory

class MemoryForm(forms.ModelForm):
    class Meta:
        model = Memory
        fields = ["text_input", "file_upload"]   # these should match your Memory model fields

        
        
       