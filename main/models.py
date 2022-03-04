
from django.db import models
from django.contrib.auth.models import AbstractUser
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
from zmq import device
from .managers import CustomUserManager

# from django.contrib.auth import get_user_model
# User = get_user_model()

#custom user model
class User(AbstractUser):
    username = None
    email = models.EmailField(('email address'), unique=True)
    is_email_verified = models.BooleanField(default=False)   
    
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
        return self.designation + '('+self.category.category+')'

class Category(models.Model):             
    category =models.CharField(max_length=400)
    def __str__(self):
        return self.category
    
#office table:-> konse koonse rooms allot hote hai faculty ko ,lab staff ko,office staff ko,

#inventory ka table:-> staff,category of devices,description

#staff ke andr office ki foreinkey dedenge

class CategoryOfDevice(models.Model):
    category = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.category

class Room(models.Model):
    room_id = models.CharField(max_length=20, blank=False, unique=True)
    name = models.CharField(max_length=255, blank=True)
    floor = models.IntegerField(blank=False, null=False, default=0)
    is_lab=models.BooleanField(default=False)
    def __str__(self):
        return self.room_id


class Staff(models.Model):
    user_obj = models.ForeignKey(User, on_delete=CASCADE, blank=False, null=False, default=None)
    name=models.CharField(max_length=100)
    initials=models.CharField(max_length=4,null=True,blank=True,default=None)
    mobile_number=models.IntegerField()
    email=models.EmailField()
    category=models.ForeignKey('Category',on_delete=CASCADE)
    designation=models.ForeignKey('Designation',on_delete=CASCADE)
    agency = models.ForeignKey('Agency',on_delete=CASCADE)
    room=models.ForeignKey('Room',blank=True,null=True,on_delete=SET_NULL,default=None)
    
    def __str__(self):
        return self.name + " " + self.designation.designation

class StaffInventory(models.Model):
    staff=models.ForeignKey('Staff',on_delete=CASCADE)
    device=models.ForeignKey('Devices',on_delete=CASCADE)
    date_added=models.DateTimeField(auto_now_add=True)
    is_requested_for_return=models.BooleanField(default=False)

    def __str__(self):
        return self.staff.name + '-' + self.device.name.category

class Inventory_log(models.Model):
    request_type=models.CharField(max_length=100)
    staff=models.ForeignKey('Staff',on_delete=CASCADE)
    device_id=models.CharField(max_length=100,default=0)
    device_name=models.CharField(max_length=100)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.request_type+ " " +self.staff.name + '-' + self.device_id+ " "+self.device_name+" "+str(self.date)

class TotalLeaves(models.Model):
    LeaveName = models.CharField(max_length=100, blank=True)
    count = models.IntegerField(default=0)
    year = models.IntegerField(default=2021)

    def __str__(self):
        return self.LeaveName + "("+ str(self.year) + ")"

TYPE_OF_LEAVE = [
    ('FULL_DAY', 'Full Day'),
    ("MULTI", 'Multiple Leaves'),
    ('FIRST_HALF', "First Half"),
    ('SECOND_HALF', "Second half")
]

class UserLeaveStatus(models.Model):
    staff=models.ForeignKey('Staff', on_delete=CASCADE, related_name='user')
    leave_type=models.ForeignKey(TotalLeaves, on_delete=CASCADE)
    from_date=models.DateField(blank=False, default=None)   
    to_date=models.DateField(blank=True, default=None)
    reason = models.TextField()
    substitute=models.ForeignKey('Staff', blank=None, on_delete=CASCADE, related_name='Substitute', null=True)
    substitute_approval = models.BooleanField(default=False)               # field -> substitute ka
    admin_approval = models.BooleanField(default=False)                       # field -> admin ka
    admin=models.ForeignKey("Staff", on_delete=models.SET_DEFAULT, default=None, blank=True, related_name='admin', null=True)
    status = models.CharField(max_length=100, default="Pending", blank=False)
    rejected = models.BooleanField(default=False) 
    month = models.CharField(max_length=20, default=None, null=True, blank=False)
    year = models.IntegerField(default=None, null=True, blank=False)
    type = models.CharField(max_length=20, choices=TYPE_OF_LEAVE, default=None)

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
    count=models.FloatField(default=0)
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

    assigned_to = models.ForeignKey("Staff", on_delete=SET_NULL, null=True, related_name='assignedtechnician',blank=True)

    escalated = models.BooleanField(default=False)
    escalated_by = models.ForeignKey(Staff,null=True,blank=True,related_name='escalatedBy',on_delete=CASCADE)
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalation_note= models.TextField(blank=False, default=None, null=True)

    
    work_Done=models.TextField(max_length=1024,blank=True)
    who_resolved = models.ForeignKey(Staff, null=True, blank=True,related_name='resolver', on_delete=models.SET_NULL)      # if is_active == false toh who_resolved mein vo person daal do
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    # def __str__(self):
        # return "Complaint for lab " + str(self.device.room.room_id)
   
class Lab(models.Model):
    lab=models.ForeignKey(Room,on_delete=CASCADE,unique = True)
    attendant = models.ForeignKey("Staff", on_delete=SET_NULL, null=True, related_name='attendant',blank=True)
    technician = models.ForeignKey("Staff", on_delete=SET_NULL, null=True, related_name='technician',blank=True)

    def __str__(self): 
        return self.lab.room_id+ "Attendant: "+str(self.attendant) + 'Technician: ' + str(self.technician)

class Devices(models.Model):
    device_id = models.CharField(max_length=20, blank=False, null=False,unique=True)
    name=models.ForeignKey("CategoryOfDevice",blank=False,null=False, on_delete=models.CASCADE)
    description = models.TextField(max_length=1024)
    room=models.ForeignKey('Room',blank=True,null=True,on_delete=SET_NULL,default=None)
    in_inventory=models.BooleanField(default=False)
    is_working=models.BooleanField(default=True)
    not_working_reason=models.TextField(default=None,blank=True,null=True)
    who_expired = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.device_id +" - "+str(self.room)



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
    ('LEAVE_REJECTED', 'Leave Rejected'),
    ('INVENTORY','Inventory'),  
    ('TECH_RESOLVE', 'Technician Resolved'),
    ('ESCALATION', 'Escalation'),
] 

class Notification(models.Model):
    sender = models.ForeignKey(Staff, blank=False, on_delete=CASCADE)
    reciever = models.CharField(max_length=255, blank=False)
    isActive = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_FIELDS, default='LEAVE')
    taskId = models.CharField(max_length=100, blank=True, null=True, default=None)

    checked = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

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
    choice = [
    ('EVEN', 'even'),
    ('ODD', 'odd'),  
] 
    course_id=models.CharField(max_length=100,blank=False,default=None)
    course_name=models.CharField(max_length=200,blank=False,default=None)
    course_credit=models.CharField(max_length=5)
    course_year=models.IntegerField(default=2022)
    semester_type=models.CharField(max_length=20,choices=choice,default=None)
    # #year #odd/even ali choice field

    def __str__(self):
        return self.course_name + ' ('+self.course_id+')' + ' '+str(self.course_year)+'('+self.semester_type+')'

class FacultyCourse(models.Model):
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    course=models.ForeignKey('Course' ,on_delete=CASCADE)

    def __str__(self):
        st = self.faculty.name + ' (' + self.course.course_id + ')'
        return st

class Branches(models.Model):
    branch_id=models.CharField(max_length=10, blank=False, default='', null=False)
    branch_name=models.CharField(max_length=200,default='',blank = False, null = False)

    def __str__(self):
        return self.branch_name + ' (' + self.branch_id + ')'

    
class Groups(models.Model):
    choice = [
    ('EVEN', 'even'),
    ('ODD', 'odd'),  
]  
    group_id = models.CharField(max_length = 300, blank = True , null = False, default = "")
    branch = models.ForeignKey('Branches' , on_delete = CASCADE)
    group_year=models.IntegerField(default=2022)
    semester_type=models.CharField(max_length=20,choices=choice,default=None)
    # #year wali field aayegi and odd/even sem wali fields aayengi

    def __str__(self):
        return self.group_id + ' (' + self.branch.branch_id + ')'+ ' '+str(self.group_year)+' ('+self.semester_type+')'

class FacultyGroups(models.Model):
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    groups=models.ForeignKey('Groups' ,on_delete=CASCADE)

    def __str__(self):
        return self.faculty.name + ' (' + self.groups.group_id + ')'

class GroupCourse(models.Model):
    faculty=models.ForeignKey('Staff',on_delete=CASCADE)
    course=models.ForeignKey('FacultyCourse',on_delete=CASCADE)
    group=models.ForeignKey('FacultyGroups',on_delete=CASCADE)

    def __str__(self):
        return self.faculty.name + ' (' + self.group.groups.group_id + ')' + ' (' + self.course.course.course_id + ')'

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
    faculty_group_course=models.ForeignKey('GroupCourse',on_delete=CASCADE,default=0)
    day=models.CharField(max_length=2000, choices=WEEK_DAY,default='Monday')
    starttime=models.TimeField(auto_now=False)
    endtime = models.TimeField(auto_now=False)
    tools_used=models.CharField(max_length=2048,default=None)

    def __str__(self):
        return  self.lab.lab.room_id + self.faculty.name + ' '+ self.faculty_group_course.course.course.course_name + ' ' + self.day + self.faculty_group_course.group.groups.group_id

#Adogra professor:-> dbms coe2
#Adogra professor-> ds coe1

#admin page
#activity page:->
#list of staff jo faculty mai hai
#Sarthak - Professor - Add Activity->click->view


class Jobs(models.Model):
    title=models.CharField(max_length=255, null=False, default=None)
    description=models.TextField()
    date = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class StaffJobs(models.Model):
    staff=models.ForeignKey(Staff, on_delete=models.CASCADE)
    job=models.ForeignKey(Jobs, on_delete=models.CASCADE)
    rejected = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    message = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return str(self.job.date) + " " + self.staff.name + " rejected: "+ str(self.rejected) + " <-> completed: " + str(self.completed)

class CompensatoryLeave(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=False)
    validity = models.DateField(null=False, default=None, blank=True)
    leave = models.ForeignKey(TotalLeaves, on_delete=models.CASCADE, null=False, default=None)
    time_created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.staff.name + " " + str(self.validity)