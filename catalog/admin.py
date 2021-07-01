from django.contrib import admin
from .models import Tag, Type, Student, Teacher, Lesson

# Register your models here.
admin.site.register(Tag)
admin.site.register(Type)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Lesson)
