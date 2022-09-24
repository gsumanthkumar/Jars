from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from .models import *
from rest_framework.views import APIView
from django.db.models import F
from rest_framework.pagination import LimitOffsetPagination
from .serializers import ApplicationSerializer
from rest_framework import status

# Create your views here.
@csrf_exempt
def signup(request):
    if not request.method == "POST":
        return JsonResponse({"status" : 400, "error": "Send a post request with valid parameters only."})
        
    username = request.POST["username"]
    password = request.POST["password"]
    usertype = request.POST["usertype"]

    usernames = list(User.objects.values_list('username', flat=True))
    if username in usernames:
        return JsonResponse({"status" : 400, "error": "Username is already taken by others!"})
    if len(password)>4:
        if len(username)>4:
            if usertype == "jobseeker":
                userdata = User(username=username,is_jobseeker=1)
            if usertype == "recruiter":
                userdata = User(username=username,is_recruiter=1)
            userdata.set_password(password)
            userdata.save()
            return JsonResponse({"status" : 200, "data": "Account Created Succesfully!"})
            
        else:
            return JsonResponse({"status" : 400, "error": "Username can't be less than 4 characters"})
    else:
        return JsonResponse({"status" : 400, "error": "Password length must be more than 4 characters"})

def get_user_token(user):
    token_instance,  created = Token.objects.get_or_create(user=user)
    return token_instance.key


@csrf_exempt
def signin(request):
    if not request.method == "POST":
        return JsonResponse({"status" : 400, "error": "Send a post request with valid parameters only."})
        
    username = request.POST["username"]
    password = request.POST["password"]
    try:
        user = User.objects.get(username=username)
        if user is None:
            return JsonResponse({ "status" : 400, "error": "There is no account with this email!"})
        if( user.check_password(password)):
            usr_dict = User.objects.filter(username=username).values().first()
            usr_dict.pop("password")
            if user != request.user:
                login(request, user)
                token = get_user_token(user)
                return JsonResponse({"status" : 200,"token": token,"status":"Logged in"})
            else:
                return JsonResponse({"status":200,"message":"User already logged in!"})
        else:
            return JsonResponse({"status":400,"message":"Invalid Login!"})
    except Exception as e:
        return JsonResponse({"status":500,"message":"Something went wrong!"})

@csrf_exempt   
def signout(request):
    try:
        request.user.auth_token.delete()
        logout(request)
        return JsonResponse({ "status" : 200, "success" : "logout successful"})
    except Exception as e:
        return JsonResponse({ "status" : 400, "error": "Something Went wrong! Please try again later."})

class JobView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        user = request.user
        if user.is_recruiter:
            role = request.POST["role"]
            company = request.POST["company"]
            salary = request.POST["salary"]
            try:
                job = Job(role=role,company=company,salary=salary,recruiter=user)
                job.save()
                return Response({"status":200,"Message":"Question posted!","jid": job.id})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})
            

    def get(self,request):
        user = request.user
        if user.is_recruiter:
            try:
                jobs = Job.objects.filter(recruiter=user).values('id','role','company','salary','posted_on')
                return Response({"status":200,"data":jobs})
            except Exception as e:
                return Response({"status":500,"Message":"There was an error on the server and the request could not be completed!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})

    def put(self,request,jid):
        user = request.user
        role = request.POST["role"]
        company = request.POST["company"]
        salary = request.POST["salary"]
        if user.is_recruiter:
            try:
                if Job.objects.get(id=jid,recruiter=user):
                    Job.objects.filter(id=jid).update(role=role,company=company,salary=salary)
                return Response({"status":204})
            except Exception as e:
                return Response({"status":500,"Message":"There was an error on the server and the request could not be completed!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})
    
    def delete(self,request,jid):
        user = request.user
        if user.is_recruiter:
            try:
                if Job.objects.get(id=jid,recruiter=user):
                    Job.objects.filter(id=jid).delete()
                return Response({"status":204})
            except Exception as e:
                return Response({"status":500,"Message":"There was an error on the server and the request could not be completed!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})

class JobseekerApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user
        if user.is_jobseeker:
            jid = request.POST["jid"]
            name = request.POST["fullname"]
            resume = request.FILES["resume"]
            applicant = user
            try:
                job = Job.objects.get(id=jid)
                application = Application(job=job,name=name,applicant=applicant,resume=resume)
                application.save()
                return Response({"status":200,"Message":"Applied Successfully!","Aid": application.id})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})
    
    def get(self,request,aid):
        user = request.user
        if user.is_jobseeker:
            try:
                application = Application.objects.filter(id=aid,applicant=user).values('id','name','resume','status','applied_on')
                return Response({"status":200,"data":application})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})
            
    def put(self,request,aid):
        user = request.user
        if user.is_jobseeker:
            name = request.POST["fullname"]
            resume = request.FILES["resume"]
            try:
                if Application.objects.get(id=aid,applicant=user):
                    Application.objects.update(name=name,resume=resume)
                return Response({"status":200,"Message":"Updated Successfully!"})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})

    def delete(self,request,aid):
        user = request.user
        if user.is_jobseeker:
            try:
                if Application.objects.get(id=aid,applicant=user):
                    Application.objects.filter(id=aid).delete()
                return Response({"status":204})
            except Exception as e:
                return Response({"status":500,"Message":"There was an error on the server and the request could not be completed!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})
            
class RecruiterApplicationView(APIView,LimitOffsetPagination):
    permission_classes = [IsAuthenticated]

    def get(self,request,jid):
        user = request.user
        sort = request.query_params["sort"]
        if user.is_recruiter:
            try:
                if sort == "latest":
                    applicants = Application.objects.filter(job__id=jid,job__recruiter=user).order_by('-applied_on').values('id','name','resume','applicant__username','applied_on')
                elif sort == "oldest":
                    applicants = Application.objects.filter(job__id=jid,job__recruiter=user).order_by('applied_on').values('id','name','resume','applicant__username','applied_on')
                results = self.paginate_queryset(applicants, request, view=self)
                serializer = ApplicationSerializer(results, many=True)
                return self.get_paginated_response(serializer.data)
            except Exception as e:
                return Response({"status":500,"Message":"There was an error on the server and the request could not be completed!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})

    def put(self,request,aid):
        user = request.user
        jid = request.POST["jid"]
        status = request.POST["status"]

        if user.is_recruiter:
            try:
                if Job.objects.get(id=jid,recruiter=user):
                    Application.objects.filter(id=aid).update(status=status)
                return Response({"status":204})
            except Exception as e:
                return Response({"status":500,"Message":"There was an error on the server and the request could not be completed!"})
        else:
            return Response({"status":401,"Message":"Unauthorized Request!"})
    
