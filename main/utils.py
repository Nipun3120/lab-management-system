# import moment
from asyncore import ExitNow
from audioop import tomono
from datetime import datetime
from django.conf import settings
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from geopy.distance import geodesic
from numpy import dtype

from lms.settings import EMAIL_HOST_USER
from .tokens import generate_token
from datetime import datetime
from .models import *


def send_email(current_site,user,name=None,mess="confirm your registration",link="activate",subj = "Activate your account."):
    mail_subject = subj
    if name is None:
        name=user.email
    message = render_to_string('Admin/active_email.html', {
        'message' : mess,
        'link' : link,
        'user': user,
        'name': name, 
        'domain': current_site.domain,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token':generate_token.make_token(user),
        })
    to_email = user.email
    email = EmailMessage(
        mail_subject, 
        message, 
        to=[to_email]
    )
    email.send()

def getNumberOfDays(fromDate, toDate):
    if not toDate:
        return 1

    # dateTo = datetime(toDate, '%Y-%m-%d')
    try:
        return (datetime.strptime(toDate, '%Y-%m-%d') - datetime.strptime(fromDate, '%Y-%m-%d')).days + 1
    # print(type(fromDate))
    # print(toDate-fromDate)
    except:
        return (toDate - fromDate).days + 1
    

def checkLeaveAvailability(leaveType, user, count):
    currLeave = UserLeavesTaken.objects.get(staff=user, leave_taken=leaveType)
    if leaveType.LeaveName=='Compensatory':
        available_leaves=len(CompensatoryLeave.objects.filter(staff=user))
        if count+currLeave.count > available_leaves:
            return False,available_leaves-currLeave.count,"leave count exceeded"
        else:
            return True,None,None
		
    print("currLeaveeeee ", currLeave)
    if count + currLeave.count > leaveType.count:
        # if count exceed
        return False, leaveType.count - currLeave.count, "leave count exceeded"
    else:
        return True, None, None

def comparedates(date):
    # d1 = datetime.datetime(2018, 5, 3)
    # d2 = datetime.datetime(2018, 6, 1)
    # d1 = datetime.now()
    # print("d1, d2 ", d1, date)
    return True