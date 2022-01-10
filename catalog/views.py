from django.shortcuts import render
from .models import Tag, Type, Teacher, Student, Lesson
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from catalog.forms import TagForm, TypeForm, TeacherForm, StudentForm, LessonCreateForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from urllib.request import urlretrieve, urlopen, Request
from django import db
import os
import shutil
from zipfile import ZipFile
from django.core.files import File
import time
from django.http import HttpResponseRedirect, HttpResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
import json

def index(request):
    """Home Page view function"""

    # generate counts
    num_students = Student.objects.all().count()
    num_lessons = Lesson.objects.all().count()

    types = list(Type.objects.all())
    list_num_lessons_per_type = [(type_name, Lesson.objects.filter(type=type_name).count()) for type_name in types]

    # context
    context = {
        'num_students': num_students,
        'num_lessons': num_lessons,
        'list_num_lessons_per_type': list_num_lessons_per_type,
    }

    # render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def thanks(request):
    """Thank You Page view function"""

    # # getting Patreon campaign id
    # patreon_request_url = "https://www.patreon.com/api/oauth2/v2/campaigns"
    # headers = {'Authorization': 'Bearer ' + os.environ.get('PATREON_CREATOR_ACCESS_TOKEN')}
    # import requests
    # resp = requests.get(patreon_request_url, headers=headers)
    # campaign_id = resp.json().get('data')[0]['id']
    #
    # # getting Patreon campaign members names
    # headers = {'Authorizatiorequestn': 'Bearer ' + os.environ.get('PATREON_CREATOR_ACCESS_TOKEN')}
    # cursor = ''
    # names = list()
    # while cursor != 'END':
    #     patreon_request_url = f"https://www.patreon.com/api/oauth2/v2/campaigns/{campaign_id}/members?include=address&fields[member]=full_name&page[cursor]={cursor}"
    #     resp = requests.get(patreon_request_url, headers=headers)
    #     try:
    #         cursor = resp.json().get('meta')['pagination']['cursors']['next']
    #     except:
    #         cursor = 'END'
    #     finally:
    #         data = resp.json().get('data')
    #         names.extend([member['attributes']['full_name'] for member in data])
    #
    # # context
    # context = {
    #     'patreon_supporters': sorted(names),
    # }

    return render(request, 'thanks.html')#, context=context)

def cors_request(request):
    url = request.META.get('QUERY_STRING').replace('url=', '')
    print("url: ", url)
    if url:
        response_data = urlopen(url)
        response_data = json.loads(response_data.read())
        response_status = 200
    else:
        response_data = {'none': None}
        response_status = 204
    return HttpResponse(json.dumps(response_data), status=response_status, content_type="application/json")

# class based views
class LessonListView(LoginRequiredMixin, generic.ListView):
    """Lesson List view function"""

    model = Lesson
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LessonListView, self).get_context_data(**kwargs)
        # Add data to the context
        ALL_PROCESSES = [name.replace('.zip', '') for name in os.listdir('.') if 'lesson-recording-' in name]

        context['ALL_PROCESSES'] = ALL_PROCESSES
        context['EMPTY_LIST'] = list()

        return context

class LessonDetailView(LoginRequiredMixin, generic.DetailView):
    """Lesson Detail view function"""

    model = Lesson

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(LessonDetailView, self).get_context_data(**kwargs)
        # Add data to the context
        # set variable
        PROCESSING = False
        # check if files are still present
        file_name = context['lesson'].recording_processing_filestorage_name
        for name in os.listdir('.'):
            if file_name in name:
                PROCESSING = True
        # add variable to context
        context['PROCESSING'] = PROCESSING

        return context

class StudentListView(LoginRequiredMixin, generic.ListView):
    """Student List view function"""

    model = Student
    paginate_by = 10

class StudentDetailView(LoginRequiredMixin, generic.DetailView):
    """Student Detail view function"""

    model = Student

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(StudentDetailView, self).get_context_data(**kwargs)
        # Add data to the context
        context['lesson_list'] = Lesson.objects.filter(student=context['student'])
        return context

class TeacherListView(LoginRequiredMixin, generic.ListView):
    """Teacher List view function"""

    model = Teacher
    paginate_by = 10

class TypeListView(LoginRequiredMixin, generic.ListView):
    """Type List view function"""

    model = Type
    paginate_by = 10

class TagListView(LoginRequiredMixin, generic.ListView):
    """Tag List view function"""

    model = Tag
    paginate_by = 10

# generic editing views
# tag
class TagCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_tag'
    model = Tag
    form_class = TagForm

    def form_valid(self, form):
        tag = form.save(commit=False)
        tag.name = form.cleaned_data.get('name')
        tag.save()

        next = self.request.POST.get('next') or reverse_lazy('tags')
        return HttpResponseRedirect(next)

class TagUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_tag'
    model = Tag
    form_class = TagForm

    def form_valid(self, form):
        tag = form.save(commit=False)
        tag.name = form.cleaned_data.get('name')
        tag.save()

        next = self.request.POST.get('next') or reverse_lazy('tags')
        return HttpResponseRedirect(next)

class TagDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_tag'
    model = Tag
    success_url = reverse_lazy('tags')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # check if lessons are using the instance
        in_use = list()
        for lesson in Lesson.objects.all():
            in_use.extend([tag.name for tag in lesson.tags.all()])

        print(in_use)
        if self.object.name in in_use:
            context = self.get_context_data(object=self.object, error='Cannot delete in use object instance, delete all uses first')
            return self.render_to_response(context)
        else:
            self.object.delete()

        return HttpResponseRedirect(success_url)

# type
class TypeCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_type'
    model = Type
    form_class = TypeForm

    def form_valid(self, form):
        type = form.save(commit=False)
        type.name = form.cleaned_data.get('name')
        type.save()

        next = self.request.POST.get('next') or reverse_lazy('types')
        return HttpResponseRedirect(next)

class TypeUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_type'
    model = Type
    form_class = TypeForm

    def form_valid(self, form):
        type = form.save(commit=False)
        type.name = form.cleaned_data.get('name')
        type.save()

        next = self.request.POST.get('next') or reverse_lazy('types')
        return HttpResponseRedirect(next)

class TypeDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_type'
    model = Type
    success_url = reverse_lazy('types')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        # check if lessons are using the instance
        in_use = list()
        for lesson in Lesson.objects.all():
            in_use.extend([type.name for type in lesson.types.all()])

        print(in_use)
        if self.object.name in in_use:
            context = self.get_context_data(object=self.object, error='Cannot delete in use object instance, delete all uses first')
            return self.render_to_response(context)
        else:
            self.object.delete()

        return HttpResponseRedirect(success_url)

# teacher
class TeacherCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_teacher'
    model = Teacher
    form_class = TeacherForm

    def form_valid(self, form):
        teacher = form.save(commit=False)
        teacher.name = form.cleaned_data.get('name')
        teacher.save()

        next = self.request.POST.get('next') or reverse_lazy('teachers')
        return HttpResponseRedirect(next)

class TeacherUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_teacher'
    model = Teacher
    form_class = TeacherForm

    def form_valid(self, form):
        teacher = form.save(commit=False)
        teacher.name = form.cleaned_data.get('name')
        teacher.save()

        next = self.request.POST.get('next') or reverse_lazy('teachers')
        return HttpResponseRedirect(next)

class TeacherDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_teacher'
    model = Teacher
    success_url = reverse_lazy('teachers')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()

        except ProtectedError:
            context = self.get_context_data(object=self.object, error='Cannot delete in use object instance, delete all uses first')
            return self.render_to_response(context)

        return HttpResponseRedirect(success_url)

# student
class StudentCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_student'
    model = Student
    form_class = StudentForm

    def form_valid(self, form):
        student = form.save(commit=False)
        student.name = form.cleaned_data.get('name')
        student.save()

        next = self.request.POST.get('next') or reverse_lazy('students')
        return HttpResponseRedirect(next)

class StudentUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_student'
    model = Student
    form_class = StudentForm

    def form_valid(self, form):
        student = form.save(commit=False)
        student.name = form.cleaned_data.get('name')
        student.save()

        next = self.request.POST.get('next') or reverse_lazy('students')
        return HttpResponseRedirect(next)

class StudentDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_student'
    model = Student
    success_url = reverse_lazy('students')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            self.object.delete()

        except ProtectedError:
            context = self.get_context_data(object=self.object, error='Cannot delete in use object instance, delete all uses first')
            return self.render_to_response(context)

        return HttpResponseRedirect(success_url)

# lesson
class LessonCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_lesson'
    template_name_suffix = '_create_form'
    form_class = LessonCreateForm
    model = Lesson
    # date_and_time and recording are filled programatically from
    # a provided CRAIG/GIARC link

    def form_valid(self, form):
        link_data = form.cleaned_data.get('recording_processing_link')
        direct_upload_file = form.cleaned_data.get('form_recording_file')
        direct_upload_date_and_time = form.cleaned_data.get('form_date_and_time')

        if link_data != None:
            # get data
            lesson_date_and_time, file_url, file_name = link_data

            # save lesson date_and_time
            lesson = form.save(commit=False)
            lesson.date_and_time = lesson_date_and_time
            lesson.save()

            # get recording from CRAIG/GIARC link (for processing and then saving)
            # kill db connections to start forked process
            db.connections.close_all()
            pid = os.fork()
            if pid == 0:
                try:
                    # show PID (for debugging)
                    print('################### DEBUG ##################')
                    print('PID: ', os.getpid())
                    # download zip file from CRAIG/GIARC url
                    print('download started')
                    r = urlretrieve(file_url, f"{file_name}.zip")
                    # unzip
                    print('download finished')
                    ZipFile(f"{file_name}.zip").extractall(file_name)
                    os.remove(f"{file_name}.zip")
                    # process files to single track
                    print('processing started')
                    shutil.copyfile('process_recording.sh', f"{file_name}/process_recording.sh")
                    # Heroku server only acceps standard Bourne/POSIX shell syntax (hence the use of 2>&1 for piping stdio)
                    os.system(f"sh {file_name}/process_recording.sh > /dev/null 2>&1")
                    print('processing ended!!!')
                    ### results in file_name/craig.m4a file
                    # save lesson recording to database
                    lesson = Lesson.objects.get(date_and_time=lesson_date_and_time)
                    with open(f"{file_name}/craig.m4a", 'rb') as recording:
                        lesson.recording.save(f"{lesson.get_recording_stamp()}.m4a", File(recording))
                except Exception as e:
                    print('PROBLEM SOMEWHERE')
                    raise e
                # cleanup
                print('cleanup started')
                # remove downloaded files
                os.system(f"rm -r {file_name}")
                # terminate forked process to avoid problems
                os._exit(os.EX_OK)
            else:
                file_exists = False
                while not file_exists:
                    for name in os.listdir('.'):
                        if file_name in name:
                            file_exists = True

        elif direct_upload_file != None and direct_upload_date_and_time != None:
            # save lesson date_and_time and recording
            lesson = form.save(commit=False)
            lesson.date_and_time = direct_upload_date_and_time
            # lesson.recording = File(direct_upload_file, name=lesson.get_recording_stamp())
            form.save()

            # file name for creating a file for view to display "processing" message
            file_name = f"recording-{direct_upload_date_and_time.isoformat()}"

            # need to fork to bypass heroku's 30s request timeout
            # kill db connections to start forked process
            db.connections.close_all()
            pid = os.fork()
            if pid == 0:
                try:
                    # show PID (for debugging)
                    print('################### DEBUG 2 ##################')
                    print('PID: ', os.getpid())
                    # create the file for view to display "processing" message
                    open(file_name, 'wt').write('direct upload')
                    # save lesson recording to database
                    lesson = Lesson.objects.get(date_and_time=direct_upload_date_and_time)
                    lesson.recording.save(f"{lesson.get_recording_stamp()}.m4a", File(direct_upload_file))
                    print('finished direct upload of file')
                except Exception as e:
                    print('PROBLEM SOMEWHERE 2')
                    raise e
                # cleanup
                os.system(f"rm {file_name}")
                # terminate forked process to avoid problems
                # IT LITERALLY DOES NOT SAVE THE DATABASE IF THE PROCESS DOESN'T EXIT UGGGGGGGGGGGGGGGGGGGGGH
                os._exit(os.EX_OK)
            else:
                file_exists = False
                while not file_exists:
                    for name in os.listdir('.'):
                        if file_name in name:
                            file_exists = True

        else:
            raise Exception

        return super(LessonCreate, self).form_valid(form)

class LessonUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_lesson'
    template_name_suffix = '_update_form'
    model = Lesson
    fields = ['teacher', 'student', 'type', 'tags', 'date_and_time', 'recording']

    def form_valid(self, form):
        new_recording = form.cleaned_data.get('recording')
        new_date_and_time = form.cleaned_data.get('date_and_time')

        # save lesson date_and_time
        lesson = form.save(commit=False)
        lesson.date_and_time = new_date_and_time
        if type(new_recording) is InMemoryUploadedFile:
            lesson.recording = File(new_recording, name=f"{lesson.get_recording_stamp()}.m4a")
        lesson.save()

        return super(LessonUpdate, self).form_valid(form)

class LessonDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_lesson'
    model = Lesson
    success_url = reverse_lazy('lessons')
