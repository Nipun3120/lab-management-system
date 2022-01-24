from tokenize import Name
from django import db
from django.db import models, reset_queries
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from datetime import datetime, time
from email.policy import default
from enum import auto
from pyexpat import model
from typing import cast
from django.conf import settings
from django.db.models.aggregates import Count
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.expressions import Case
from django.db.models.fields import NullBooleanField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy
import string
from django.utils import timezone
from .managers import CustomUserManager

# from django.contrib.auth import get_user_model
# User = get_user_model()

#custom user model
class User(AbstractUser):
    username = None
    email = models.EmailField(('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    def __str__(self):
        return self.email

class Agency(models.Model):
    agency = models.CharField(max_length = 200)
    def __str__(self):
        return self.agency
    
class Designation(models.Model):
    category=models.ForeignKey("Category",on_delete = CASCADE)
    designation =models.CharField(max_length=400)
    def __str__(self):
        return self.designation

class Category(models.Model):             
    category =models.CharField(max_length=400)
    def __str__(self):
        return self.category
    

class Staff(models.Model):
    name=models.CharField(max_length=100)
    mobile_number=models.IntegerField()
    email=models.EmailField()
    category=models.ForeignKey('Category',on_delete=CASCADE)
    designation=models.ForeignKey('Designation',on_delete=CASCADE)
    agency = models.ForeignKey('Agency',on_delete=CASCADE)
    
    def __str__(self):
        return self.name + " " + self.designation.designation



class TotalLeaves(models.Model):
    LeaveName = models.CharField(max_length=100, blank=True)
    count = models.IntegerField(default=0)
    year = models.IntegerField(default=2021)

    def __str__(self):
        return self.LeaveName + "("+ str(self.year) + ")"
    

# usne leave leli
class UserLeaveStatus(models.Model):
    staff=models.ForeignKey('Staff', on_delete=CASCADE, related_name='user')
    # leave_type=models.CharField(max_length=255, )
    leave_type=models.ForeignKey(TotalLeaves, on_delete=CASCADE)
    from_date=models.DateTimeField()    # jis din chahiye
    to_date=models.DateTimeField(null=True)
    reason = models.TextField()
    substitute=models.ForeignKey('Staff', blank=None, on_delete=CASCADE, related_name='Substitute')
    substitute_approval = models.BooleanField(default=False)               # field -> substitute ka
    admin_approval = models.BooleanField(default=False)                       # field -> admin ka
    admin=models.ForeignKey("Staff", on_delete=models.SET_DEFAULT, default=None, blank=True, related_name='admin', null=True)
    status = models.CharField(max_length=100, default="Pending", blank=False)
    rejected = models.BooleanField(default=False) 

    def __str__(self):
        return self.staff.name + " --> " + self.leave_type.LeaveName + " --> " +  self.substitute.name
# 2 admin, adjustment
# adjustment sbse phle vo verify
# after verification -> admin 
# admin approve

# leave request UserLeavesTaken initially null  -> 
# leave request -> form us page pe taken leaves display -> null > count -> error
# # request sent
# approve tick 
# subs -done adin -done
# 
# admin
# userleavetaken-> staff  -> 3 -> 2 -> 2(objects)
# check type of leave in these 2leaves -> count ++
# else create a new leavetaken object

class UserLeavesTaken(models.Model):
    # get object of staff after admin verification
    staff=models.ForeignKey('Staff',on_delete=CASCADE)
    leave_taken = models.ForeignKey('TotalLeaves',on_delete=CASCADE)      
    count=models.IntegerField(default=0)
    def __str__(self):
        return self.staff.name + " " + str(self.leave_taken.LeaveName) + " "+ str(self.count)

    # staff unique 
    # get staff object -> set of taken leaves
    #   

class Complaint(models.Model):
    created_by=models.ForeignKey(Staff,null=True,blank=False,related_name='sender',on_delete=CASCADE)
    device=models.ForeignKey('Devices', on_delete=models.CASCADE,default=None)
    complaint=models.TextField(blank=False)
    created_at=models.DateTimeField(auto_now_add=True)
    isActive=models.BooleanField(default=True)
    work_Done=models.TextField(max_length=1024,blank=True)
    who_resolved = models.ForeignKey(Staff, null=True, blank=True,related_name='resolver', on_delete=models.SET_NULL)      # if is_active == false toh who_resolved mein vo person daal do
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return "Complaint for lab " + str(self.device.lab.lab)
   
class Lab(models.Model):
    lab = models.CharField(max_length=20, blank=False)
    name = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=10,blank=False, null=False)
    staff = models.ForeignKey("Staff", on_delete=SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.lab
    

class CategoryOfDevice(models.Model):
    category = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.category

class Devices(models.Model):
    device_id = models.CharField(max_length=20, blank=False, null=False)
    name=models.ForeignKey("CategoryOfDevice",blank=False,null=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=1024)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)

    def __str__(self):
        return self.device_id +" "+ "(" + self.lab.lab + ")"



# tech profile-> usne kitni complaints resolve kri uska count + which complaint
# leaves -> saare users -> profile-> leave count (casual leave: 8, special casual leve: 10, restricted leave: 2)


# email address se register
# email, password confirm password, mobile no, category(faculty, lab staff, office staff, student), designation , agency
# lab (system analys, lab sup, lab aasso, lab tech, lab attendant)
# student (phd, me)
# faulty (prof, assoc proff, assis proff)

# agency: lab/office (regular, adhoc, )



# sender (ek banda)
# reciever (either ek banda or a group-> desigination)
# active status
# time (jis din notification crate hui)
# text message
# type of notification

# leave, technician, time table change vala access

NOTIFICATION_FIELDS = [
    ('LEAVE', 'Leave'),
    ('TECH', 'Technician'),
    ('TTC', 'Time Table Change'),
    ('LEAVE_ACCEPTED', 'Leave Accepted'),
    ('LEAVE_REJECTED', 'Leave Rejected')
]

class Notification(models.Model):
    sender = models.ForeignKey(Staff, blank=False, on_delete=CASCADE)
    reciever = models.CharField(max_length=255, blank=False)
    isActive = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_FIELDS, default='LEAVE')
    taskId = models.CharField(max_length=100, blank=True, null=True, default=None)

    def __str__(self) -> str:
        return str(self.time.date()) + " " +  self.notification_type + " from "  + self.sender.name + " to " + self.reciever

    #  add count notifications function here


# tab -> click -> query -> display

# tech -> click -> query -> technician -> display

# lab tech -> filter from staff ? 

# 3 forms 
# -> leave regarding -> ek band vo dusre ko tag krega reciever fields -> user list 
# -> complaint -> group notify -> reciever -> designation list
# -> baad mein krte 


# -> Time Table models

class Course(models.Model):
    course_id=models.CharField(max_length=100,blank=False,default=None)
    course_name=models.CharField(max_length=200,blank=False,default=None)
    course_credit=models.CharField(max_length=5)

    def __str__(self):
        return self.course_name + ' ('+self.course_id+')'

class FacultyCourse(models.Model):
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    course=models.ForeignKey('Course' ,on_delete=CASCADE)

    def __str__(self):
        st = self.faculty.name + ' (' + self.course.course_id + ')'
        return st

class Branches(models.Model):
    branch_id=models.CharField(max_length=10,blank=False,default='COE')
    branch_name=models.CharField(max_length=200,default='Computer Engineering',blank = False, null = False)

    def __str__(self):
        return self.branch_name + ' (' + self.branch_id + ')'

    
class Groups(models.Model):
    group_id = models.CharField(max_length = 300, blank = False , null = False, default = "NILL")
    branch = models.ForeignKey('Branches' , on_delete = CASCADE)

    def __str__(self):
        return self.group_id + ' (' + self.branch.branch_id + ')'

class FacultyGroups(models.Model):
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    groups=models.ForeignKey('Groups' ,on_delete=CASCADE)

    def __str__(self):
        return self.faculty.name + ' (' + self.groups.group_id + ')'


class Class(models.Model):
    WEEK_DAY = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday')
    )
    lab=models.ForeignKey('Lab',on_delete=CASCADE)
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    course=models.ForeignKey('FacultyCourse',on_delete=CASCADE)
    group=models.ForeignKey('FacultyGroups',on_delete=CASCADE)
    day=models.CharField(max_length=2000, choices=WEEK_DAY,default='Monday')
    starttime=models.TimeField(auto_now=False)
    endtime = models.TimeField(auto_now=False)

    def __str__(self):
        return self.lab.lab + ' ' + self.faculty.name + ' '+ self.course.course.course_name + ' ' + self.day + self.group.groups.group_id


class GroupCourse(models.Model):
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    course=models.ForeignKey('FacultyCourse',on_delete=CASCADE)
    group=models.ForeignKey('FacultyGroups',on_delete=CASCADE)

    def __str__(self):
        return self.faculty.name + ' (' + self.group.groups.group_id + ')' + ' (' + self.course.course.course_id + ')'

#admin page
#activity page:->
#list of staff jo faculty mai hai
#Sarthak - Professor - Add Activity->click->view

