from typing import BinaryIO
from xml.dom import ValidationErr
from django import forms
from django.db import models
from django.db.models import fields
from django.forms.fields import ChoiceField
from .models import Class, Designation, Devices, FacultyCourse, FacultyGroups, Staff, Notification, TotalLeaves,UserLeaveStatus
from django.contrib.auth.forms import  AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.password_validation import validate_password

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
import datetime
from django.forms import ModelForm

User = get_user_model()

# class ComplaintResolveFrom(forms.Form):
#     WorkDone=forms.Textarea(widget=forms.Textarea(attrs={'placeholder': 'Enter Workdone'}))

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ['email',]

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['email']


class ComplaintForm(forms.Form):
    complaint=forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter complaint'}))

class NewComputerForm(forms.ModelForm):
    # device_id = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter Device ID'}))
    # device_name = forms.ChoiceField(widget=forms.TextInput(attrs={'placeholder': 'Enter Device Name'}))
    # description = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter description of the device'}))
    class Meta:
        model = Devices
        fields = ['device_id','name','description']

class AddCourseForm(forms.ModelForm):

    class Meta:
        model = FacultyCourse
        fields = ['faculty','course']

class AddGroupForm(forms.ModelForm):

    class Meta:
        model = FacultyGroups
        fields = ['faculty','groups']



class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    password = forms.CharField(required=True , widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    
    class Meta:
        model=User
        fields=['email', 'password']
        
# class LoginForm(AuthenticationForm):
#     username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
#     class Meta:
#         model=User
#         fields=['username', 'password']

# class NewUserForm(UserCreationForm):
    # name=forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Full Name'}))
    # email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'placeholder':'Email'}))
    # password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    # password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password Confirm'}))
    # mobile_number=forms.IntegerField(required=True, widget=forms.TextInput(attrs={'placeholder':'Mobile Number'}))
    # category=forms.ChoiceField(choices=CATEGORY)
#     Designation=forms.ChoiceField(choices=DESIGNATION)

#     class Meta:
#         model = User
#         fields = ("username", "name", "mobile_number","email", "password1", "password2", "type")

#     

#         user = super(NewUserForm, self).save(commit=False)
#         user.email = self.cleaned_data['email']

#         user_email = self.cleaned_data['email']
#         username = self.cleaned_data['username']
#         user_mobile = self.cleaned_data['mobile_number']
#         name = self.cleaned_data['name']
#         type=self.cleaned_data['type']
        


        
#         staff,was_created=Staff.objects.get_or_create(staff_id=username, name=name,email=user_email,mobile_number= user_mobile, type=type)
#         staff.save()
        
#         if commit:
#             user.save()
#         return user


class EditProfileForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Full Name'}))
    mobile_number = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'placeholder':'Mobile Number'}))


class SignupForm(UserCreationForm):
    name=forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Full Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}), validators=[validate_password])
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))
    mobile_number=forms.IntegerField(required=True, widget=forms.TextInput(attrs={'placeholder':'Mobile Number'}))

        
    class Meta:
        model = User
        fields = ("email", "password1", "password2", "name", "mobile_number")
        
    # def cleaned_emal(self):
    #     email = self.cleaned_data['email']
    #     try:
    #         account = User.objects.get(email=email)
    #     except Exception as e:
    #         return email
    #     raise forms.ValidationError(f"{email} already in use")


    # def cleaned_password(self):
    #     return self.cleaned_data['password1']
        
    # def save(self, commit=True):
    #     # save user in user model fields email password
    #     email = self.cleaned_data['email']
    #     password = self.cleaned_data['password1']
    #     name= self.cleaned_data['name']

    #     user = super(UserCreationForm, self).save(commit=False)
        
    #     user.set_password(password)
    #     user.email = email
    #     user.username = name
    #     if commit:
    #       user.save()
    #     return user


class AddNewLeave(forms.ModelForm):
    class Meta:
        model = TotalLeaves
        fields = '__all__'


# class ComplaintNotification(forms.Form):
#     sender=forms.CharField(settings.AUTH_USER_MODEL)
#     receiver=forms.CharField(widget=forms.CharField(attrs={'placeholder': 'Enter complaint'}))



# class LeaveNotification(forms.Form):
#     sender = forms.CharField(settings.AUTH_USER_MODEL)
#     reciever = 

# class LeaveForm(forms.ModelForm):

#     year = datetime.datetime.now().year
#     currentYearLeaves = TotalLeaves.objects.filter(year=year).all()
#     CHOICES=[]
#     i=0
#     for leave in currentYearLeaves:
#         # print('aaaa')
#         print(leave.LeaveName)
#         tup=()
#         tup+=(i,)
#         tup+=(leave.LeaveName,)
#         CHOICES.append(tup)
#         i+=1
#     type_of_leave=forms.ChoiceField(choices=CHOICES)
#     class Meta:
#         model = UserLeaveStatus
#         # fields = ("staff", "leavetype",  "date", "reason", "substitute")
#         fields = ("staff", "type_of_leave", "date_time", "reason", "substitute")

# class EditProfileForm(ModelForm):
#         class Meta:
#             model = User
#             fields = (
#                  'email',
#                  'first_name',
#                  'last_name'
#                 )
# class ProfileForm(ModelForm):
#          class Meta:
#             model = Staff
#             fields = ('name','mobile_number','email', 'category', 'designation', 'agency') #Note that we didn't mention user field here.


class AddClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['faculty',"course","group","day","starttime"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = FacultyCourse.objects.none()
        self.fields['group'].queryset = FacultyGroups.objects.none()


        if 'faculty' in self.data:
            try:
                faculty_id = int(self.data.get('faculty'))
                self.fields['course'].queryset = FacultyCourse.objects.filter(faculty_id=faculty_id)
                self.fields['group'].queryset = FacultyGroups.objects.filter(faculty_id=faculty_id)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['course'].queryset = FacultyCourse.objects.filter(faculty_id=self.instance.faculty)
            self.fields['group'].queryset = FacultyGroups.objects.filter(faculty_id=self.instance.faculty)

class AddFacultyClassForm(forms.ModelForm):
    class Meta:
        model=Class
        fields = ['lab',"course","group","day","starttime"]
    def __init__(self, faculty,*args, **kwargs):
        # print(faculty)
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = FacultyCourse.objects.filter(faculty=faculty)
        self.fields['group'].queryset = FacultyGroups.objects.filter(faculty=faculty)

