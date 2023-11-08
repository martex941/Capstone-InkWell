# forms.py
from django import forms
from .models import Chapter, CoAuthorRequest
from django_quill.widgets import QuillWidget
from django_quill.fields import QuillField

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('chapterTitle', 'chapterContents',)
        widgets = {
            'chapterContents': QuillWidget(),
        }

class CoAuthorRequestForm(forms.ModelForm):
    class Meta:
        model = CoAuthorRequest
        fields = ('chapterContents',)
        widgets = {
            'chapterContents': QuillWidget(),
        }
