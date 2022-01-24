from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name='main'

urlpatterns = [

    # auth paths
    # add account/ in front of these urls
    path("register/", views.register_request, name="register"),
    path("login/", views.login_request, name="login"),
    path("logout/", views.logout_request, name= "logout"),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="password-reset"),
    path('password-reset-sent/', auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), name="password-reset-done"),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), name="password-reset-confirm"),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), name="password-reset-complete"),

    
    # user paths
    path('', views.home, name='home'),
    path('profile/user-profile/',views.user_profile, name='user_profile'),
    path('profile/user-profile-details/',views.user_profile_details, name='userProfileDetails'),
    path('profile/edit-profile/<pk>',views.editProfile, name='editProfile'),
    path('complaint/<pk>',views.complaint, name='complaint'),
    path("lab/<pk>", views.lab, name='lab'),
    path("add/<pk>",views.add_devices,name='add_devices'),
    path('complaint-resolve/<pk>', views.resolveConflict, name='resolveConflict'),
    path('profile/leaves/', views.userLeaves, name="userLeaves"),
    path('profile/leaves/request-leaves', views.requestleave, name="requestleave"),
    path('profile/notifications/', views.notifications, name='notification'),
    path('profile/notification/<pk>', views.handleNotification, name="handleNotification"),
    path('profile/leaves/check-leave-status/', views.checkLeaveStatus, name='checkLeaveStatus'),
    path('profile/leaves/check-leave-status/<pk>' , views.checkLeaveStatusId, name="currleaveStatus"),
    path('profile/leaves/check-leave-status/cancel/<pk>', views.cancelLeaveRequest, name='cancelLeaveRequest'),
    path('profile/leaves/approve-leaves/', views.approveLeaves, name='approveLeaves'),
    path('profile/leaves/approve-leaves/approve/<pk>', views.approveRequest, name='approveRequest'),
    path('profile/leaves/approve-leaves/decline/<pk>', views.declineRequest, name='declineRequest'),
    path('profile/view_complaints/' , views.view_complaints, name="viewcomplaints"),
    path('profile/viewprevleaves/',views.viewprevleaves,name='viewprevleaves'),
    path('profile/viewcourses/',views.viewcourses,name='viewcourses'),
    path('profile/viewgroups/',views.viewgroups,name='viewgroups'),
    path('profile/viewclasses/',views.viewfacultyclasses,name='viewfacultyclasses'),
    path('profile/viewfacultytimetable/',views.viewfacultytimetable,name='viewfacultytimetable'),

    # admin paths
    path('admin-dashboard/staff-members-list/', views.adminStaff, name='adminStaff'),
    path('admin-dashboard/current-year-leaves/', views.adminLeaves, name='adminLeaves'),
    path('admin-dashboard/current-year-leaves/new-leave-form', views.newLeave, name='newLeave'),
    path('admin-dashboard/current-year-leaves/leave/<pk>', views.adminEditLeave, name='adminEditLeave'),
    path('admin-dashboard/current-year-leaves/remove-leave/<pk>', views.removeLeave, name='removeLeave'),
    path('admin-dashboard/labs-list/', views.adminLabs, name='adminLabs'),
    path('admin-dashboard/complaints-list/', views.adminComplaints, name='adminComplaints'),
    path('admin-dashboard/faculty-details',views.ViewFacultyDetails,name='adminfacultydetails'),
    path('admin-dashboard/faculty-details/admin-view-groups/<id>',views.adminviewgroups,name='adminviewgroups'),
    path('admin-dashboard/faculty-details/admin-view-courses/<id>',views.adminviewcourses,name='adminviewcourses'),
    path('admin-dashboard/faculty-details/admin-view-classes/<id>',views.adminviewclasses,name='adminviewclasses'),
    path('admin-dashboard/faculty-details/admin-view-groups/delete-group/<id>',views.admindeletegroup,name='admindeletegroup'),
    path('admin-dashboard/faculty-details/admin-view-courses/delete-courses/<id>',views.admindeletecourses,name='admindeletecourses'),
    path('admin-dashboard/faculty-details/admin-view-courses/add-course/<id>',views.adminaddcourses,name='adminaddcourses'),
    path('admin-dashboard/faculty-details/admin-view-courses/add-group/<id>',views.adminaddgroup,name='adminaddgroup'),
    path('admin-dashboard/faculty-details/admin-view-courses/add-faculty-class/<id>',views.adminaddfacultyclass,name='adminaddfacultyclass'),
    path('admin-dashboard/faculty-details/admin-view-courses/update-faculty-class/<id><pk>',views.adminupdatefacultyclass,name='adminupdatefacultyclass'),



    #timetable paths
    path('viewlabtimetable/<id>',views.viewtimetable_wrtlab,name='viewtimetable_wrtlab'),
    path('viewlabclasses/<id>',views.viewLabClasses,name='viewLabClasses'),
    path('add_class/<id>',views.add_classes,name = 'add_classes'),
    path('ajax/load-courses/', views.load_courses, name='ajax_load_courses'), # AJAX
    path('ajax/load-groups/', views.load_groups, name='ajax_load_groups'), # AJAX
    path('updateclass/<pk>_<id>/', views.update_class, name='update_class'),

]
