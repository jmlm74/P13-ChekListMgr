import json

import requests
from django.conf import settings as conf_settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView

from app_user.forms import (UserCheckListMgrRegister,
                            Company)
from app_user.models import User
from app_utilities.models import Translation


class RegisterView(View):
    context = {'title': "Register"}
    template_name = 'app_user/register.html'
    form = UserCheckListMgrRegister

    def get(self, request):
        try:
            request.session['language']
        except KeyError:
            request.session['language'] = 'UK'
        self.context['form'] = self.form(None)
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        form = UserCheckListMgrRegister(request.POST, request.FILES)
        if form.is_valid():
            try:
                print(form.cleaned_data['picture'])
            except MultiValueDictKeyError:
                pass
            if request.POST['password'] == request.POST['confirm_password']:
                admin = request.POST.get('admin', 'False') == 'on'
                if 'company' not in request.POST:
                    company = None
                    pro = False
                else:
                    company = form.cleaned_data['company']
                    pro = True
                try:
                    new_user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        preferred_language=form.cleaned_data['preferred_language'],
                        phone=form.cleaned_data['phone'],
                        picture=form.cleaned_data['picture'],
                        admin=admin,
                        user_company=company
                    )
                except IntegrityError:
                    form.add_error(None, 'Errdupleuser')
                else:
                    if new_user:
                        if company is None:  # create society if None (name = userid)
                            company = new_user.id
                            new_company = Company(name=company)
                            new_company.save()
                            new_user.user_company = new_company
                            new_user.save()
                        self.context['user_created'] = form.cleaned_data['username']
                        messages.success(request, "RegisterOK")
                        form = UserCheckListMgrRegister()
                    else:
                        form.add_error(None, 'Errcreateuser')
            else:
                form.add_error(None, 'Errpswconfir')
        self.context['form'] = form
        return render(request, self.template_name, self.context)


@login_required
def user_logout(request):
    logout(request)
    print("logout")
    return HttpResponseRedirect(reverse('app_home:index'))


class ListUsersView(ListView):
    context = {'title': "Userlist"}
    context_object_name = "users"
    template_name = 'app_user/list.html'
    # model = User
    # queryset = User.objects.all().order_by('user_company')
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all().order_by('user_company')
        if self.request.user.user_company is None:
            return User.objects.all().order_by('user_company').filter(is_active=True).filter(user_company=None)
        else:
            return User.objects.filter(user_company=self.request.user.user_company).filter(is_active=True).\
                order_by('username')


class EditUserView(UpdateView):
    context = {'title': "Userupdate"}
    form = UserCheckListMgrRegister
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'picture', 'preferred_language']
    template_name = 'app_user/register.html'
    success_url = "/app_user/list/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Userupdate"
        return context

    #def get_queryset(self):
    #    print(self.request)
    #    print(self.request.GET)
    #    return User.objects.get(pk=35)


@csrf_exempt
def delete_user(request):
    if request.method == 'POST':
        request_data = json.loads(request.read().decode('utf-8'))
        print(request_data)
        id_user = request_data['id']
        try:
            user_to_delete = User.objects.get(pk=id_user)
            print(f'{user_to_delete.username} - {user_to_delete.is_active}')
            user_to_delete.is_active = False
            user_to_delete.save()
            print(f'{user_to_delete.username} - {user_to_delete.is_active}')
            data = {'data': 'OK'}
        except:
            data = {'data': 'Erreur'}
    return JsonResponse(data)


def reset_psw(request):
    """
    The reset password view (1st view)
    use the PasswordResetForm form (django view)
    The data validation is done by the standard view
    The mail is sent with the MAILGUN API
    """
    context = {'title': "Passwordreset"}
    language = request.session['language']
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            clean_mail = form.cleaned_data['email']
            # get the user
            users = User.objects.filter(Q(email=clean_mail))
            if users.exists():
                for user in users:
                    # build the mail
                    subject = Translation.get_translation("Password Reset Requested", language)
                    email_template_name = f"app_user/registration/reset_password_email_{language}.txt"
                    if not conf_settings.PRODUCTION:
                        domain = "127.0.0.1:8000"
                        protocol = "http"
                    else:
                        domain = "checklistmgr.jm-hayons74.fr"
                        protocol = "https"
                    c = {
                        "email": user.email,
                        'domain': domain,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': protocol,
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        # send mail
                        rc = requests.post("https://api.mailgun.net/v3/sandbox1f42285ff9e446fa9e90d34287cd8fee.mailgun.org/messages",
                                           auth=("api", conf_settings.MAILGUN_KEY),
                                           data={"from": "Checklist Manager <webmaster@jm-hayons74.fr>",
                                                 "to": clean_mail,
                                                 "subject": subject,
                                                 "text": email,
                                                 })
                        print(rc)
                    except:
                        context['error'] = Translation.get_translation("ErrorSendmail", language)

                    context['success'] = Translation.get_translation(
                        'A message with reset password instructions has been sent to your inbox.',language)

            # else: --> advice from my mentor --> no error msg because of the bots
            #     context['error'] = Translation.get_translation('An invalid email has been entered.', language)
        #else:
        #    context['error'] = Translation.get_translation('An invalid email has been entered.', language)
        #    return redirect('user_app:reset_password', error=context['error'])

    else:
        form = PasswordResetForm()
    context['form'] = form
    return render(request, 'app_user/registration/reset_password.html', context=context)



