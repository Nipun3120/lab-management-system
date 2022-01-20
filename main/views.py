import email
from urllib import response
from verify_email.email_handler import send_verification_email
from django import http
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User

from django.db.models.base import Model
from django.http.response import Http404
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm #add this
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from  django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from django.urls import reverse_lazy
from .models import *
from .forms import LoginForm, ComplaintForm, NewComputerForm, SignupForm, AddNewLeave, EditProfileForm
import datetime
from .utils import send_email  # custom
from django.core.mail import send_mail # default

# from django_email_verification import send_email

# from django.contrib.auth import get_user_model


UserModel = get_user_model()


# Create your views here.
@login_required
def home(request):
	if request.user.is_staff:
		# email='a@thaapr.edu'
		a = User.objects.get(email=request.user)
		print(a)
		return render(request, "admin/dashboard.html", {})

	staff = Staff.objects.get(email=request.user.email)
	userLabs = Lab.objects.filter(staff=staff).order_by('id').all()
	return render(request, "home.html", {'userLabs': userLabs, "staff":staff})

	# except:
	# 	tech = Technician.objects.get(tech_id=request.user.username)
	# 	complaints = Complaint.objects.all()
	# 	context = { "complaints": complaints}
	# 	return render(request, "tech_dashboard.html", context)

def user_profile_details(request):
	staff=Staff.objects.get(email=request.user.email)
	return render(request, "user profiles/user_profile.html", {'staff':staff})

@login_required
def user_profile(request):
	# print(request.user)
	user_email=request.user.email
	#print(user_email)
	staff = Staff.objects.get(email=user_email)
	#print(staff.designation)

	if staff.category.category == "Lab Staff":
		
		# for admin 

		if staff.designation.designation == "System Analyst" or staff.designation.designation == "Lab Supervisor":
			# labs = Lab.objects.get().all()
			#notifications=Notification.objects.filter(reciever='admin').all()
			return render(request, "admin/dashboard.html", {"staff":staff})

		
		if staff.designation.designation == "Lab Associate":
			pass

		
		if staff.designation.designation == "Lab Attendent":

			staff_1 = Staff.objects.get(email=request.user.email)
			userLabs = Lab.objects.filter(staff=staff).order_by('id').all()

			#leaves=Leaves.objects.get(staff=staff)
			context = {
				'userLabs' : userLabs,
				'staff'	: staff_1,
				#'leaves' : leaves,
			}
			return render(request, 'user profiles/lab_attendent.html',context)
			# pass
			
		if staff.designation.designation == "Lab Technician":
			staff = Staff.objects.get(email=request.user.email)			
			complaints = Complaint.objects.all()
			current_notifications = Notification.objects.filter(reciever='Lab Technician').order_by('id').all()


			context = { 
				"staff":staff,
				"complaints": complaints,
				"notifications": current_notifications
			}
			return render(request, "user profiles/Lab_technician.html", context)
			
			# complaint resolve form details
			# static-> device id, lab id, complaint, jisne complaint kri hai vo user, 
			# dynamic -> message kya problem thi
			# who resolved = staff (obv tech hoga koi) 			
			# that complaint -> isActive = False
			# notification remove isActive = False

	elif staff.category.category == "Office Staff":
		if staff.designation.designation == " Program Manager":
			pass
		if staff.designation.designation == " Program Coordinator":
			pass
		if staff.designation.designation == " Senior Assistant":
			pass
		if staff.designation.designation == " Skilled Helper":
			pass

	elif staff.category.category == "Faculty":
		if staff.designation.designation == " Professor":
			pass
		if staff.designation.designation == " Associate Professor":
			pass
		if staff.designation.designation == " Assistant Professor":
			pass
		
	else :
		if staff.designation.designation == " PHD":
			pass
		if staff.designation.designation == " ME":
			pass

@login_required
def editProfile(request, pk):
	staff = Staff.objects.get(id=pk)		#jo user h

	if request.user.is_staff:
		admin=Staff.objects.get(email=request.user.email)	# curr user
		if request.method=="POST":
			form=request.POST
			name=form['name']
			designationId = form['designation']
			agencyId=form['agency']
			mobile_number=form['mobile_number']
			updatedAgency = Agency.objects.get(id=agencyId)
			updatedDesgination = Designation.objects.get(id=designationId)
			staff.name=name
			staff.designation=updatedDesgination
			staff.agency = updatedAgency
			staff.mobile_number=mobile_number
			staff.save()
			return redirect('main:adminStaff')
		else:
			category=Category.objects.get(category=staff.category)
			designations=Designation.objects.filter(category=category)
			desig=[]
			for des in designations:
				if des != staff.designation:
					desig.append(des)

			agency=Agency.objects.exclude(agency=staff.agency)
			context = {
				"staff": admin,
				"staff1": staff,
				"designations":desig,
				"agency":agency

			}
			return render(request, "user profiles/edit_profile.html", context)
	else:
		if request.method == "POST":
			name = request.POST['name']
			mobile_number = request.POST['mobile_number']
			staff.name = name
			staff.mobile_number = mobile_number
			staff.save()
			return redirect('/')

		else:
			context = {
				"staff": staff
			}
			return render(request, "user profiles/edit_profile.html", context)


@login_required
def userLeaves(request):
	staff = Staff.objects.get(email=request.user.email)	
	year = datetime.datetime.now().year
	leavesThisYear = TotalLeaves.objects.filter(year=year).all()
	
	userLeavesTaken = UserLeavesTaken.objects.filter(staff=staff)
	
	# print(userLeavesTaken)
	context = {
		"staff":staff,
		"totalLeaves" : leavesThisYear,
		"year": year,
		"userLeavesTaken":userLeavesTaken,
	}
	return render(request, "leaves/leaves.html", context)

@csrf_protect
def requestleave(request):
	staff= Staff.objects.get(email=request.user.email)

	if request.method == 'POST':
		# check kr ki jo leave request kri hai vo exceed toh nai h 
		# for eg ek year mein 8 casual 
		# cas -> 8 decline status 

		form=request.POST
		applicant=form['applicant']
		leaveSelection=form['leaveSelection']
		substitute=form['substitute']		
		fromDate=form['fromDate']
		reason=form['reason']
		substitute=Staff.objects.get(id=substitute)
		year=datetime.datetime.now().year
		leave_type=TotalLeaves.objects.get(id=leaveSelection)
		fromDateNumber = fromDate.split("-")[2]
		try:
			multipleLeaves = form['multipleLeaveCheckbox']
			toDate=form['toDate']
			todateNumber = toDate.split("-")[2]
			
			# total count of leaves 
			countOfLeaves = int(todateNumber) - int(fromDateNumber)
			
			
			userstatus,wascreated=UserLeaveStatus.objects.get_or_create(staff=staff,leave_type=leave_type,from_date=fromDate,to_date=toDate, reason=reason,substitute=substitute)
			userstatus.save()
			##notification

			customMessage1 = staff.name + " requested for leave"
			notification, was_created = Notification.objects.get_or_create(
				sender=staff, 
				reciever=str(substitute.id)+' '+substitute.name, 
				message=customMessage1,
				notification_type = 'LEAVE',
				taskId = userstatus.id
			)
			notification.save()

			customMessage2 = "your request for " + leave_type.LeaveName + " leave is placed"
			notification, was_created = Notification.objects.get_or_create(
				sender=staff, 
				reciever=str(staff.id) + ' ' + staff.name, 
				message=customMessage2,
				notification_type = 'LEAVE',
				taskId=userstatus.id
			)
			notification.save()
			return HttpResponse(200)

		except:
			# userstatus,wascreated=UserLeaveStatus.objects.get_or_create(staff=staff,leave_type=leave_type,from_date=fromDate, reason=reason,substitute=substitute)
			# userstatus.save()
			# ##notification

			# customMessage1 = staff.name + " requested for leave"
			# notification, was_created = Notification.objects.get_or_create(
			# 	sender=staff, 
			# 	reciever=str(substitute.id)+' '+substitute.name, 
			# 	message=customMessage1,
			# 	notification_type = 'LEAVE',
			# 	taskId = userstatus.id
			# )
			# notification.save()

			# customMessage2 = "your request for " + leave_type.LeaveName + " leave is placed"
			# notification, was_created = Notification.objects.get_or_create(
			# 	sender=staff, 
			# 	reciever=str(staff.id) + ' ' + staff.name, 
			# 	message=customMessage2,
			# 	notification_type = 'LEAVE',
			# 	taskId=userstatus.id
			# )
			# notification.save()


			return HttpResponse(200)

# leave req-> nofitification to substi
#		   -> current user can check leave status
#          -> substitute confirm leave
#		   -> admin ke pass confirm leave 


	else:
		year = datetime.datetime.now().year  # 2022
		totalLeavesCurrYear = TotalLeaves.objects.filter(year=year).all()
		# check ki if any leave category is  > 0 then display
		userleavetaken=UserLeavesTaken.objects.filter(staff=staff)
		user_leaves_remaining=[]

		for leave in userleavetaken:
			if leave.count<leave.leave_taken.count:
				user_leaves_remaining.append(leave.leave_taken.LeaveName)
		totalLeavesCurrYear=[leaves for leaves in totalLeavesCurrYear if leaves.LeaveName in user_leaves_remaining]
		substitutes = Staff.objects.exclude(name=staff.name).all()
		# substitutes = Staff.objects.all()

		context={
			'staff':staff,
			'totalLeavesCurrYear': totalLeavesCurrYear,
			'substitutes': substitutes
		}
	
		return render(request,"leaves/leaverequest.html",context)


@login_required
def checkLeaveStatus(request):
	staff = Staff.objects.get(email=request.user.email)
	print(staff)

	pendingRequests = UserLeaveStatus.objects.filter(staff=staff).order_by("-id")
	# get all the pending requests 
	context = {
		'staff':staff,
		"pendingRequests": pendingRequests
	}
	return render(request, "leaves/leaveRequestStatus.html", context)

@login_required
def checkLeaveStatusId(request, pk):
	staff = Staff.objects.get(email=request.user.email)
	leaveRequest = UserLeaveStatus.objects.get(id=pk)
	context = {
		'staff':staff,
		'leaveRequest':leaveRequest
	}
	return render(request, "leaves/leaveRequestStatusId.html", context)

# user cancels its posted leave
@login_required
def cancelLeaveRequest(request, pk): 
	# get object and delete from db
	leave = UserLeaveStatus.objects.get(id=pk)
	leave.delete()
	return redirect('main:checkLeaveStatus')

@login_required
def approveLeaves(request):
	staff=Staff.objects.get(email=request.user.email)
	#for admin
	if request.user.is_staff:
		#return HttpResponse(201)
		requestedleaves=UserLeaveStatus.objects.filter(substitute_approval=True,admin_approval=False,rejected=False)
		approvedleaves=UserLeaveStatus.objects.filter(substitute_approval=True,admin_approval=True,rejected=False)
		rejectedleaves=UserLeaveStatus.objects.filter(substitute_approval=True,admin_approval=False,rejected=True)
	
		context={
			'staff':staff,
			"requestedleaves":requestedleaves,
			"approvedleaves":approvedleaves,
			"rejectedleaves":rejectedleaves
		}
		return render(request,'admin/adminLeaveApproval.html',context)

	# get leaves in which current user is substitute

	leaves = UserLeaveStatus.objects.filter(substitute=staff).order_by("-date_time")
	context = {
		'staff':staff,
		"leaves": leaves
	}
	return render(request, 'leaves/leaveapproval.html', context)


@login_required
def approveRequest(request, pk):
	# get leave
	if request.user.is_staff:
		sender=Staff.objects.get(email=request.user.email)
		leave = UserLeaveStatus.objects.get(id=pk)
		leave.admin_approval = True
		leave.rejected = False
		leave.status = "Approved"
		leave.admin=sender 
		leave.save()
		notification_receiver = Staff.objects.get(id=leave.staff.id)
		notification, was_created = Notification.objects.get_or_create(
			sender=sender,
			reciever=str(notification_receiver.id) + " " + (notification_receiver.name),
			message="your " + str(leave.leave_type.LeaveName) + " leave application was approved by admin",
			notification_type="LEAVE_ACCEPTED",
			taskId=str(leave.id)
		)
		notification.save()

		
		# 1) ki user leaves taken hai uss user ka usko update 
		userleavetaken = UserLeavesTaken.objects.get(staff=leave.staff,leave_taken=leave.leave_type)
		userleavetaken.count += 1
		userleavetaken.save()
		
		return redirect("main:approveLeaves")

	leave = UserLeaveStatus.objects.get(id=pk)
	leave.substitute_approval = True
	leave.rejected = False
	leave.status = "Waiting for admin to respond, approved by " + str(leave.substitute.name)
	leave.save()

	
	notification_receiver = Staff.objects.get(id=leave.staff.id)
	notification, was_created = Notification.objects.get_or_create(
		sender=leave.substitute,
		reciever=str(notification_receiver.id) + " " + (notification_receiver.name),
		message="your " + str(leave.leave_type.LeaveName) + " leave application was approved by " + str(leave.substitute.name),
		notification_type="LEAVE_ACCEPTED",
		taskId=str(leave.id)
	)
	notification.save()

	return redirect("main:approveLeaves")

@login_required
def declineRequest(request, pk):
	sender=Staff.objects.get(email=request.user.email)

	if request.user.is_staff:	
		leave = UserLeaveStatus.objects.get(id=pk)
		leave.admin_approval = False
		leave.rejected = True
		leave.status = "Declined by Admin " + str(sender.name) 
		leave.admin=sender
		leave.save()

		notification_receiver = Staff.objects.get(id=leave.staff.id)
		notification, was_created = Notification.objects.get_or_create(
			sender=sender,
			reciever=str(notification_receiver.id) + " " + (notification_receiver.name),
			message="your " + str(leave.leave_type.LeaveName) + " leave application was declined by admin",
			notification_type="LEAVE_REJECTED",
			taskId=str(leave.id)
		)
		notification.save()
		existingNotification = Notification.objects.get(taskId = leave.id, notification_type="LEAVE")
		existingNotification.isActive = False
		existingNotification.save()
		return redirect("main:approveLeaves")

	leave = UserLeaveStatus.objects.get(id=pk)
	notification_receiver = Staff.objects.get(id=leave.staff.id)
	leave.status = "Declined by " + str(leave.substitute.name)
	leave.rejected = True
	leave.save()
	notification, was_created = Notification.objects.get_or_create(
		sender = sender,
		reciever=str(notification_receiver.id) + " " + (notification_receiver.name),
		message="your " + str(leave.leave_type.LeaveName) + " leave application was declined by " + str(sender.name),
		notification_type="LEAVE_REJECTED",
		taskId = str(leave.id)
	)
	notification.save()
	existingNotification = Notification.objects.filter(taskId = leave.id, notification_type="LEAVE").all()
	for notification in existingNotification:
		notification.isActive = False
		notification.save()

	return redirect("main:approveLeaves")

def viewprevleaves(request):
	staff=Staff.objects.get(email=request.user.email)
	all_leaves=UserLeaveStatus.objects.filter(staff=staff,rejected=False,admin_approval=True,substitute_approval=True)
	context={
		'staff':staff,
		'all_leaves':all_leaves,
	}
	return render(request,"leaves/viewprevleaves.html",context)

@login_required	
def complaint(request, pk):
	device = Devices.objects.get(id=pk)
	staff=Staff.objects.get(email=request.user.email)
	if request.method == 'POST':
		form = ComplaintForm(request.POST)
		if form.is_valid():
			dev = device
			complaint=form.cleaned_data['complaint']
			# staff=Staff.objects.get(email=request.user.email)	
			complaint, was_created = Complaint.objects.get_or_create(
				created_by=staff,
				device=dev,
				complaint=complaint
			)
			complaint.save()

			notification, was_created = Notification.objects.get_or_create(
				sender=staff, 
				reciever="Lab Technician", 
				message="You have a new Notification in complaints",
				notification_type = 'TECH',
				taskId=complaint.id
			)			
			notification.save()
			
		return redirect("main:home")

	else:   #get
		form = ComplaintForm()

		context={
			'staff':staff,
			'form': form,
			'name': device.name.category, 
			'id': device.device_id
		}
		return render(request, 'Complaints/complaints.html', context)

def view_complaints(request):
	staff = Staff.objects.get(email=request.user.email)
	active_complaints = Complaint.objects.filter(isActive = True).order_by('-date_created')
	resolved_complaints=Complaint.objects.filter(isActive = False).order_by('-date_created')
	# userLabs = Lab.objects.filter(staff=staff).order_by('id').all()
	# # complaint -> device
	# deviceNo = Complaint.objects.filter(complaint = complaint)	
	context = {
		'staff':staff,
		'active_complaints' : active_complaints,
		'resolved_complaints' :resolved_complaints,
	}
	return render(request,'Complaints/view_complaints.html', context)

@login_required
def notifications(request):
	staff = Staff.objects.get(email=request.user.email)			
	designation = staff.designation.designation
	notifications=[]
	
	if designation == 'Lab Technician':
		notification = Notification.objects.filter(notification_type='TECH').order_by('-time').all()
		notifications.extend(notification)

	receiver=str(staff.id) +' '+staff.name
	notification = Notification.objects.filter(reciever=receiver).order_by('-time').all()
	notifications.extend(notification)

	if request.user.is_staff:
		notification=Notification.objects.filter(reciever=receiver).order_by('-time').all()
		notifications.extend(notification)


	# third type notificatoin baad mein okay? create another if condition
	
	return render(request, "Notifications/notifications.html", {"notifications": notifications, "staff":staff})

@login_required
def handleNotification(request, pk):
	# get notification and userleavestatus objects
	# compare and render 
	staff = Staff.objects.get(email=request.user.email)	 	# current user		
	notification = Notification.objects.get(id=pk)
	taskId = notification.taskId
	
	# reciever_id= int(notification.reciever.split(' ')[0])

	# get notification get leave from that notification
	# display that leave

	# leave = UserLeaveStatus.objects.get(id=taskId, )
	same = False
	if notification.notification_type == 'LEAVE' or notification.notification_type == 'LEAVE_ACCEPTED' or notification.notification_type == 'LEAVE_REJECTED':
		leave = UserLeaveStatus.objects.get(id=taskId)
		if staff == leave.substitute:
			same = True
		return render(request, "Notifications/leaveRequestStatusNotification.html", {"leave":leave, "notification":notification, "staff":staff, "same":same})

	if notification.notification_type == 'TECH':
		complaint = Complaint.objects.get(id=taskId)
		return render(request, 'Notifications/complaintNotification.html', {"complaint":complaint,"staff":staff,})

	if notification.notification_type == 'TTC':
		pass
	

	return redirect("main:notification")

	
	# # jisne notification receice kro + jo leave mei substitute hai vooo	
	# notification_receiver = Staff.objects.get(id=reciever_id)

	# if notification.notification_type == "LEAVE":
	# 	if request.method == 'POST':
	# 		leaveRequest = UserLeaveStatus.objects.get(staff=notification_receiver, substitute=notification.sender, id=notification.taskId)
	# 		print(leaveRequest.substitute_approval)
	# 		# leaveRequest.status = " waiting for admin to respond"
	# 		# print(leaveRequest)
	# 		return HttpResponse(200)
	# 	else:
	# 		if notification_receiver==notification.sender:
	# 			# if same person gets notification
	# 			leaveRequest = UserLeaveStatus.objects.get(staff=notification_receiver, id=notification.taskId)
	# 			context= {
	# 				"staff": staff,
	# 				"notification" : notification, 
	# 				"leaves": leaveRequest,
	# 				"substitute": notification_receiver,
	# 			}
	# 			return render(request, "notificationConfirm.html", context)
	# 		else:
	# 			leaveRequest = UserLeaveStatus.objects.get(substitute=notification_receiver, id=notification.taskId)
	# 			context = {
	# 				"staff": staff,
	# 				"notification" : notification, 
	# 				"leaves": leaveRequest,
	# 				"substitute": notification_receiver,
	# 				}
	# 			return render(request, "notificationConfirm.html", context)
	
	# if notification.notification_type == "TECH":
	# 	return HttpResponse(202)



@login_required
def add_computer(request, pk):
	lab=Lab.objects.get(id=pk)
	staff=Staff.objects.get(email=request.user.email)
	print(lab)
	if request.method == 'POST':
		form = NewComputerForm(request.POST)
		if form.is_valid():
			labid=lab
			compid=form.cleaned_data['computer_id']
			fid=form.cleaned_data['floor_id']
			computer, was_created=Devices.get_or_create(computer_id=compid,lab_id=labid,floor_id=fid)
			computer.save()
			
		return redirect("main:home")
	else:
		form = NewComputerForm()

		context={
			'staff': staff,
			'form': form,
			'labid':lab,
		}
		return render(request, 'Labs/add_computer.html', context)
	
	
def register_request(request):
	if request.method == "POST":
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save(commit=False)
				# check for @thapar.edu			
			email=form.data.get('email')
			res=email.split('@')[1]
			if res!='thapar.edu':
				messages.error(request, "Please enter you thapar email id")
				return redirect("main:register")

			password = form.data.get('password1')
			confirmPassword = form.data.get('password2')
			if password != confirmPassword:
				messages.error(request, "Passwords not same")
				return redirect("main:register")

			# user = User.objects.
			name=form.cleaned_data['name']
			category1=request.POST['category']
			designation=request.POST['designation']
			agency=request.POST['agency']
			mobile_number=request.POST['mobile_number']
			# print(name, category1, designation, agency, mobile_number)
			Cat=Category.objects.get(category=category1)
			Des=Designation.objects.get(designation=designation)
			Agen=Agency.objects.get(agency=agency)
			
			if designation == 'System Analyst' or designation == 'Lab Supervisor':
				User.objects.create_superuser(email, password)
			else:
				user = User.objects.create_user(email, password)
				send_email(user)
			
			staff,was_created=Staff.objects.get_or_create(name=name,email=email,mobile_number= mobile_number,category=Cat,designation=Des,agency=Agen)
			staff.save()

			year = datetime.datetime.now().year 
			totalLeavesCurrYear = TotalLeaves.objects.filter(year=year).all()

			for leave in totalLeavesCurrYear:
				userLeavesTaken, was_created = UserLeavesTaken.objects.get_or_create(
					staff=staff,
					leave_taken=leave
				)
				userLeavesTaken.save()
			return redirect("main:login")
		else:
			print("invalid credentials")
			return HttpResponse(404)
	else:
		form = SignupForm()
		return render(request, "accounts/register.html", {"form": form})


# def register_request(request):
# 	if request.method == "POST":
# 		form = SignupForm(request.POST)
# 		if form.is_valid():
			
# 			email=form.data.get('email') # check for @thapar.edu
			
# 			res=email.split('@')[1]
# 			if res!='thapar.edu':
# 				messages.error(request, "Please enter you thapar email id")
# 				return redirect("main:register")
			
# 			password=form.data.get('password1')
# 			confirmation = form.data.get("password2")
# 			if not form.is_valid() or password != confirmation:
# 				messages.error(request, "Enter valid credentials")
# 				return redirect("main:register")				


			# name=form.cleaned_data['name']
			# category1=request.POST['category']
			# designation=request.POST['designation']
			# agency=request.POST['agency']
			# mobile_number=request.POST['mobile_number']
			# # print(name, category1, designation, agency, mobile_number)
			# Cat=Category.objects.get(category=category1)
			# Des=Designation.objects.get(designation=designation)
			# Agen=Agency.objects.get(agency=agency)


# 			user = User.objects.create_user(email, password, is_active=False)
# 			if designation == 'System Analyst' or designation == 'Lab Supervisor':
# 				print('okayy')
# 				user.objects.create_superuser(email, password)
# 				user.save()
# 				print(user)
# 			else:
# 				print('okayy2')
# 				print(user)
# 				user.save()

			
# 			# staff,was_created=Staff.objects.get_or_create(name=name,email=email,mobile_number= mobile_number,category=Cat,designation=Des,agency=Agen)
# 			# staff.save()
# 			# # get all leaves create leave taken objects
# 			# year = datetime.datetime.now().year 
# 			# totalLeavesCurrYear = TotalLeaves.objects.filter(year=year).all()

			# for leave in totalLeavesCurrYear:
			# 	userLeavesTaken, was_created = UserLeavesTaken.objects.get_or_create(
			# 		staff=staff,
			# 		leave_taken=leave
			# 	)
			# 	userLeavesTaken.save()
				
			

# 			# return render(request, "Users/confirmation.html", { "message": "Confirm your email", "verifiedUser": user})

# 		# else:
# 		# 	messages.error(request, "some error")
# 		# 	return redirect("main:register")
# 	else:
# 		form = SignupForm()
# 		return render (request=request, template_name="accounts/register.html", context={"form": form})


def login_request(request):
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			res=email.split('@')[1]
			if res!='thapar.edu':
				messages.error(request, "Please enter you thapar email id")
				return HttpResponse(400)
				
			UserModel = get_user_model()
			try:
				user = UserModel.objects.get(email=email)
			except UserModel.DoesNotExist:
				user=None
			else:
				if user.check_password(password):
					#print("passes")
					pass
				else :
					messages.error(request, "Please enter a correct password")
					return redirect("main:login")

			if user is not None:
				login(request,user)
			#	print("logged in") 
				messages.success(request, f"You are successfully logged in as {email}")
				return redirect("main:user_profile")
				
	form = LoginForm()
	return render(request, "accounts/login.html", {"login_form":form, 'messages': messages.get_messages(request)})


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.")
   
	return redirect("main:login")


@login_required
def lab(request, pk):
	# listof all devices
	
	lab = Lab.objects.filter(lab=pk).order_by('id').all()
	lab_id=Lab.objects.get(id=pk)

	devices=Devices.objects.filter(lab=pk).order_by("id").all()
	print(devices)
	return render(request, "Labs/lab.html", {
				'devices': devices,
				'labid': pk,
				'labname': lab
				})

@login_required
def resolveConflict(request, pk):
	complaint = Complaint.objects.get(id=pk)
	resolver=Staff.objects.get(email=request.user.email)
	if request.method == 'POST':
		complaint.work_Done=request.POST['workdone']
		complaint.isActive=False
		complaint.who_resolved=resolver
		complaint.save()
		notification = Notification.objects.get(taskId=complaint.id, reciever='Lab Technician')
		notification.isActive = False
		notification.save()
		if request.user.is_staff:
			return redirect("main:adminComplaints")

		else:
			return redirect("main:user_profile")
		
	else:   
		admin_status = request.user.is_staff
		context={
			'complaint':complaint,
			'admin_status': admin_status
		}
		return render(request, 'admin/adminResolveComplaint.html', context)


def adminStaff(request):
	if request.user.is_staff:
		staffs = Staff.objects.all()
		return render(request, "admin/adminStaffs.html", {"staffs":staffs})
	else:
		return render(request, "pagenotfound.html")

def adminLabs(request):
	if request.user.is_staff:
		labs=Lab.objects.all()
		return render(request, "admin/adminLabs.html", {"labs": labs})
	else:
		return render(request, "pagenotfound.html")

def adminComplaints(request):
	if request.user.is_staff:
		complaints = Complaint.objects.all().order_by('id')
		return render(request, "admin/adminComplaints.html", {"complaints":complaints})
	else:
		return render(request, "pagenotfound.html")

@login_required
def adminLeaves(request):
	if request.user.is_staff:
		year = datetime.datetime.now().year
		leavesThisYear = TotalLeaves.objects.filter(year=year).all()

		context = {
			"leavesThisYear": leavesThisYear
		}

		return render(request, "admin/adminLeaves.html", context)
	else:
		return render(request, "pagenotfound.html")

@login_required
def newLeave(request):
	staff=Staff.objects.get(email=request.user.email)
	if request.method == "POST":
		# create a new leave type and assign it to all the users with their initial count = 0
		form = AddNewLeave(request.POST)
		if form.is_valid():
			leaveName = form.cleaned_data['LeaveName']
			count = form.cleaned_data['count']
			year = form.cleaned_data['year']
			newLeave, was_created = TotalLeaves.objects.get_or_create(
				LeaveName=leaveName, 
				count=count, 
				year=year
			)
			newLeave.save()

			staffs = Staff.objects.all()
			for staff in staffs:
				userLeaveTaken, was_created = UserLeavesTaken.objects.get_or_create(
					staff=staff,
					leave_taken=newLeave,
				)
				userLeaveTaken.save()
			
			return redirect('main:adminLeaves')

	else:
		form = AddNewLeave()
		return render(request, "admin/addLeaveForm.html", {"form":form, "staff":staff})

@login_required
def adminEditLeave(request, pk):
	staff=Staff.objects.get(email=request.user.email)
	if request.user.is_staff:
		leave = TotalLeaves.objects.get(id=pk)
		if request.method == "POST":
			count = request.POST['leaveCount']
			leave.count = count
			leave.save()
			return redirect('main:adminLeaves')
		else:
			return render(request, "admin/adminEditLeaveForm.html", {"staff":staff, "leave":leave})
	else:
		return render(request, "pagenotfound.html")

@login_required
def removeLeave(request, pk):
	if request.user.is_staff:
		leave = TotalLeaves.objects.get(id=pk)
		leave.delete()
		return redirect('main:adminLeaves')
		
	else:
		return render(request, "pagenotfound.html")




# def register_request(request):
# 	if request.method == "POST":
# 		form = SignupForm(request.POST)
# 		if form.is_valid():
# 			email=form.cleaned_data['email'] # check for @thapar.edu
# 			res=email.split('@')[1]
# 			if res!='thapar.edu':
# 				messages.error(request, "Please enter you thapar email id")
# 				return redirect("main:register")
# 			else:

# 				name=form.cleaned_data['name']
# 				category1=request.POST['category']
# 				designation=request.POST['designation']
# 				agency=request.POST['agency']
# 				mobile_number=form.cleaned_data['mobile_number']
# 				Cat=Category.objects.get(category=category1)
# 				Des=Designation.objects.get(designation=designation)
				
# 				Agen=Agency.objects.get(agency=agency)
# 				staff,was_created=Staff.objects.get_or_create(name=name,email=email,mobile_number= mobile_number,category=Cat,designation=Des,agency=Agen)

# 				inactive_user = send_verification_email(request, form)
# 				if designation == 'System Analyst' or designation == 'Lab Supervisor':
					
# 					user = User.objects.get(email=email)
# 					user.is_staff = True
# 					user.is_admin = True
# 					user.is_superuser=True
# 					user.save()

# 				staff.save()

# 				# get all leaves create leave taken objects
# 				year = datetime.datetime.now().year 
# 				totalLeavesCurrYear = TotalLeaves.objects.filter(year=year).all()

# 				for leave in totalLeavesCurrYear:
# 					userLeavesTaken, was_created = UserLeavesTaken.objects.get_or_create(
# 						staff=staff,
# 						leave_taken=leave
# 					)
# 					userLeavesTaken.save()
					
				
# 				return redirect("main:login")
# 		else:
# 			messages.error(request, "some error")
# 			return redirect("main:register")
# 	else:
# 		form = SignupForm()
# 		return render (request=request, template_name="accounts/register.html", context={"form": form})


			# verifiedUser = form.save(commit=False)
			# # verifiedUser.user = user
			# # verifiedUser.save()
			# current_site = get_current_site(request)
			# send_email(current_site, user, verifiedUser.Name)
			# # # logout(request)
			
			# # yi hua isse :-(
			# # inactive_user = send_verification_email(request, form)
			# # inactive_user.cleaned_data['email']