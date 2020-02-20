from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from login.models import userInfo
from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.conf import settings
import random

# Create your views here.
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



def send_code(request):

    pass

def test(request):
    # return HttpResponse('login page test.')
    if request.method == 'GET':
        context = {}
        context['previous_page'] = request.GET.get('from_page')
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
                    #return HttpResponseRedirect('/second_authen')
                    return HttpResponse('login successfully')
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
