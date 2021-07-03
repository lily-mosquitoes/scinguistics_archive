from django.db import models
from django.urls import reverse
from django_backblaze_b2 import BackblazeB2Storage

class Tag(models.Model):
    """Model for lesson tags"""

    name = models.CharField(max_length=100, unique=True, help_text='Enter a new tag name')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Type(models.Model):
    """Model for lesson type (e.g. Voice Feminization)"""

    name = models.CharField(max_length=100, unique=True, help_text='Enter a new lesson type')

    def __str__(self):
        return self.name

class Teacher(models.Model):
    """Model for the student name"""

    name = models.CharField(max_length=200, unique=True, help_text='Enter a new teacher')

    def __str__(self):
        return self.name

class Student(models.Model):
    """Model for the student name"""

    name = models.CharField(max_length=200, unique=True, help_text='Enter a new student')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """returns the url to access the record of this student"""
        return reverse('student-detail', args=[str(self.id)])

    class Meta:
        ordering = ['name']

class Lesson(models.Model):
    """Model for the lesson entry"""

    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, null=True)
    student = models.ForeignKey('Student', on_delete=models.PROTECT, null=True)
    type = models.ManyToManyField('Type', help_text='Select a type of lesson')
    tags = models.ManyToManyField('Tag', help_text='Select tags for the lesson')
    date_and_time = models.DateTimeField(blank=True, null=True, unique=True, help_text='Date and time of the recording (autofilled from CRAIG/GIARC link)')
    recording = models.FileField(blank=True, null=True, upload_to='uploads', storage=BackblazeB2Storage, help_text='Recording link from the CDN (autofilled from CRAIG/GIARC link)')

    def __str__(self):
        return f"{self.student}'s lesson with {self.teacher} - {self.date_and_time.isoformat()}"

    def get_recording_stamp(self):
        return f"{self.student}-s_lesson_with_{self.teacher}_-_{int(self.date_and_time.timestamp())}"

    def get_absolute_url(self):
        """returns the url to access the record of this lesson"""
        return reverse('lesson-detail', args=[str(self.id)])

    class Meta:
        ordering = ['-date_and_time']
