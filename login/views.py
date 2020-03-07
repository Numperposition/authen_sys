from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from login.models import userInfo
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.conf import settings
import random, socket, sys, json
from login.cert_analyzer import cert_analysis

# Create your views here.

def cert_upload(request):
    user = request.user
    if request.method == 'GET':
        if user.is_authenticated is False:
            return render(request, 'login/file_upload.html')
        else:
            return HttpResponse("You have alreadly login!")
    elif request.method == 'POST':
        file_obj = request.FILES.get('file', None)
        if file_obj == None:
            return render(request, 'login/file_upload.html')
        str = settings.BASE_DIR + "\\download\\" + file_obj.name
        with open(str, 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)
        f.close()
        if cert_analysis(str) == True:
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    #return HttpResponseRedirect('/send_request')
                    return HttpResponse('login successfully')
                # return HttpResponse('login success.')
                else:
                    return HttpResponse('login fail')
            except:
                return render(request, 'login/file_upload.html')
        return HttpResponse("login fail")




def redirect_to_login(request):
    return HttpResponseRedirect('/login')

def handle_redirect(request):
    user = request.user
    if user.is_authenticated is True:
        if request.method == 'GET':
            username = user.username  # request.POST['username']
            context = {'username': username}
            return render(request, 'login/second_authen.html', context)
        elif request.method == 'POST':
            pass
    else:
        return HttpResponseRedirect('/login')



def send_req_to_gw(request):
    user = request.user
    if user.is_authenticated is True:
        username = user.username
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('192.168.1.1', 9906))  # router IP
        except socket.error as msg:
            print(msg)
            print(sys.exit(1))
        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        data = {"ip": ip, "user": username}
        data = json.dumps(data)  # convert dict object to json string

        s.send(data.encode())
        print(data)
        msg = s.recv(1024)
        msg = msg.decode()
        dict_msg = json.loads(msg)
        print(msg)
        status = dict_msg['status']
        if msg is not None:
            s.close()
        context = {'username': username, 'status': status}
        return render(request, 'login/send_req.html', context)
    else:
        return HttpResponseRedirect('/login')

def test(request):
    # return HttpResponse('login page test.')
    if request.method == 'GET':
        context = {}
        context['previous_page'] = request.GET.get('from_page')
        if "HTTP_X_FORWARDED_FOR" in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        print("user ip = ", ip)
        return render(request, 'login/login.html', context)
    else:
        if 'submit_code' in request.POST:
            username = request.POST['username']
            # handle send email to the email address of that user\
            user = userInfo.objects.filter(user_name=username)
            if user.count() == 0:
                 #return HttpResponse('username not found.')
                 return HttpResponseRedirect('/login')
            else: # 1. fetch user's email,
                  # 2. generate 4-digit random number,
                  # 3. store number in db and send email to corresponding email address.
                rand_num = random.randint(10000, 100000)
                user.update(token=rand_num)
                res = send_mail('authentication code',
                                  str(rand_num),
                                  'xhxxbob@163.com',
                                  [user[0].user_email])
                if res == 1:
                    return HttpResponse("email sent successfully")
                else:
                    return HttpResponse("email sent failed")
        else:
            username = request.POST['username']
            password = request.POST['password']
            token = request.POST['code']
            user_token = str(userInfo.objects.filter(user_name=username)[0].token)
            try:
                user = authenticate(request, username=username, password=password)
                if user is not None and token == user_token:
                    login(request, user)
                    return HttpResponseRedirect('/send_request')
                    #return HttpResponse('login successfully')
                # return HttpResponse('login success.')
                else:
                    return HttpResponse('login fail')
                #return HttpResponseRedirect(request.GET.get('from_page'))
             #
            except:
                context = {}
                context['login_info'] = True
                context['previous_page'] = request.GET.get('from_page')
                return render(request, 'login/login.html', context)
