from django import forms
from .models import Lesson
from django.core.exceptions import ValidationError
from urllib.request import urlopen
import json
from datetime import datetime

class LessonCreateForm(forms.ModelForm):

    recording_processing_link = forms.CharField(required=False, max_length=300, help_text='Input a CRAIG or GIARC link')
    form_date_and_time = forms.CharField(required=False, max_length=50, help_text='Input the date and time of the lesson as an ISO timestamp string (e.g.: 2021-06-15T00:04:22.468Z) -> this is in info.txt')
    form_recording_file = forms.FileField(required=False, help_text='Upload the lesson recording file')

    def clean(self):
        cleaned_data = super(LessonCreateForm, self).clean()

        # make sure at least one of the two recording fields are used
        req1 = cleaned_data.get('recording_processing_link')
        req2 = cleaned_data.get('form_recording_file')
        if not req1 and not req2:
            raise ValidationError('Please input either the recording link or the file + date and time')

        # make sure the date and time gets set if upload is selected
        req3 = cleaned_data.get('form_date_and_time')
        if req2 and not req3:
            raise ValidationError('Please input the lesson date and time when directly upploading the recording file')

        return cleaned_data

    def clean_recording_processing_link(self):
        base_url = self.cleaned_data.get('recording_processing_link')
        if base_url == '':
            return None

        # check no file upload exists
        uploaded_file = self.cleaned_data.get('form_recording_file')
        if uploaded_file == None:
            pass
        else:
            raise ValidationError('ONLY CHOOSE ONE OPTION: INPUT CRAIG/GIARC LINK OR UPLOAD A FILE')

        if 'craig' in base_url:
            html = urlopen(base_url).read()
        else:
            raise ValidationError('Invalid CRAIG/GIARC URL')

        if 'Invalid ID' not in str(html):
            # get info
            info_url = f"{base_url}&fetch=info"
            info = json.loads(urlopen(info_url).read())
            lesson_date_and_time = datetime.fromisoformat(info['startTime'].replace('Z', '+00:00'))
            # get file
            file_url = f"{base_url}&fetch=cooked&format=powersfxu"
            file_name = f"recording-{lesson_date_and_time.isoformat()}"
        else:
            raise ValidationError('Expired CRAIG/GIARC URL')

        if Lesson.objects.filter(date_and_time=lesson_date_and_time).exists():
            raise ValidationError('Lesson already in archive')
        else:
            pass

        return lesson_date_and_time, file_url, file_name

    def clean_form_date_and_time(self):
        str_timestamp = self.cleaned_data.get('form_date_and_time')
        if str_timestamp == '':
            return None

        try:
            form_date_and_time = datetime.fromisoformat(str_timestamp.replace('Z', '+00:00'))
        except:
            raise ValidationError('The string provided is not a valid ISO timestamp')

        return form_date_and_time

    class Meta:
        model = Lesson
        fields = ['teacher', 'student', 'type', 'tags']
