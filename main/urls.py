from unicodedata import name
from django.urls import path
from . import views

urlpatterns = [
    #Register
    path('signup/',views.signup,name='signup'),

    #Login
    path('signin/',views.signin,name='signin'),

    #Logout
    path('signout/',views.signout,name='signout'),

    #Recruiter

    #post a job or get jobs 
    path('job/',views.JobView.as_view(),name='job'),

    #update or delete a job
    path('job/<int:jid>/',views.JobView.as_view(),name='job'),

    #get applications for particular job or update the status of application (selected or rejected)
    path('jobapplication/<int:jid>/',views.RecruiterApplicationView.as_view(),name='jobapplication'),

    #jobseeker
    
    #apply to job
    path('application/',views.JobseekerApplicationView.as_view(),name='application'),
    
    #get, update or delete the application
    path('application/<int:aid>/',views.JobseekerApplicationView.as_view(),name='application'),



    

]
