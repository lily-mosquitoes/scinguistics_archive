from django import forms
from .models import Tag, Type, Teacher, Student, Lesson
from django.core.exceptions import ValidationError
from urllib.request import urlopen
import urllib3
from urllib.parse import urlparse, parse_qs
import os
import json
from datetime import datetime

class TagForm(forms.ModelForm):

    def clean_name(self):
        # make sure name is unique (case insensitive)
        name = self.cleaned_data.get('name')
        if name.upper() in [obj.name.upper() for obj in Tag.objects.all()]:
            raise ValidationError('Tag with this name already exists')

        return name

    class Meta:
        model = Tag
        fields = ['name']

class TypeForm(forms.ModelForm):

    def clean_name(self):
        # make sure name is unique (case insensitive)
        name = self.cleaned_data.get('name')
        if name.upper() in [obj.name.upper() for obj in Type.objects.all()]:
            raise ValidationError('Type with this name already exists')

        return name

    class Meta:
        model = Type
        fields = ['name']

class TeacherForm(forms.ModelForm):

    def clean_name(self):
        # make sure name is unique (case insensitive)
        name = self.cleaned_data.get('name')
        if name.upper() in [obj.name.upper() for obj in Teacher.objects.all()]:
            raise ValidationError('Type with this name already exists')

        return name

    class Meta:
        model = Teacher
        fields = ['name']

class StudentForm(forms.ModelForm):

    def clean_name(self):
        # make sure name is unique (case insensitive)
        name = self.cleaned_data.get('name')
        if name.upper() in [obj.name.upper() for obj in Student.objects.all()]:
            raise ValidationError('Type with this name already exists')

        return name

    class Meta:
        model = Student
        fields = ['name']

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
            parsed = urlparse(base_url)
            query = parse_qs(parsed.query)
            rec_n = parsed.path.split("/")[-1]
            rec_key = query['key'][0]
            base_url = f"{parsed.scheme}://{parsed.netloc}/api/v1/recordings/{rec_n}?key={rec_key}"
            print('base_url: ', base_url)

            http = urllib3.PoolManager()
            r = http.request('GET', base_url)

            html = r.data.decode('utf-8')
        else:
            raise ValidationError('Invalid CRAIG/GIARC URL')

        if 'Invalid ID' not in str(html):
            # get info
            # info_url = f"{base_url}&fetch=info"
            ## changed because of craig api change
            info_url = f"{parsed.scheme}://{parsed.netloc}/api/recording/{rec_n}/.txt?key={rec_key}"
            print('info_url: ', info_url)

            http = urllib3.PoolManager()
            r = http.request('GET', info_url, preload_content=False)
            with open(f"{rec_n}.txt", "wb") as out:
                while True:
                    data = r.read()
                    if not data:
                        break
                    out.write(data)
            r.release_conn()

            # info = json.loads(urlopen(info_url).read())
            info = []
            with open(f"{rec_n}.txt", "rt") as f:
                for line in f.read().split("\n"):
                    if "Start time" in line:
                        info.extend(line.split("\t"))
                        break
            info = info[-1]
            os.system(f"rm {rec_n}.txt")
            # lesson_date_and_time = datetime.fromisoformat(info['startTime'].replace('Z', '+00:00'))
            lesson_date_and_time = datetime.fromisoformat(info.replace('Z', '+00:00'))
            # get file
            # file_url = f"{base_url}&fetch=cooked&format=powersfxu"
            # file_url = f"{parsed.scheme}://{parsed.netloc}/api/recording/{rec_n}/cook/run?key={rec_key}&format=powersfxu&container=zip&dynaudnorm=false" # API CHANGED AGAIN
            file_url = f"{parsed.scheme}://{parsed.netloc}/api/v1/recordings/{rec_n}/job?key={rec_key}"
            # print('file_url: ', file_url)
            file_name = f"lesson-recording-{lesson_date_and_time.isoformat()}"
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
