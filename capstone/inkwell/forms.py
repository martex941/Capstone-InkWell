# forms.py
from django import forms
from .models import Chapter
from django_quill.widgets import QuillWidget

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('chapterTitle', 'chapterContents',)
        widgets = {
            'chapterContents': QuillWidget(),
        }