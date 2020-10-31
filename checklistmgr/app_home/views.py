from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views import View
from django.views.generic.base import TemplateView
from sortable_listview import SortableListView

from app_checklist.models import CheckListDone
from app_user.forms import UserCheckListMgrFormLogin
from app_create_chklst.models import CheckList


class Index(View):
    context = {'title': "app_user-home-title"}
    template_name = 'app_home/home.html'
    form = UserCheckListMgrFormLogin

    def get(self, request):
        try:
            request.session['language']
        except KeyError:
            request.session['language'] = 'UK'
        self.context['form'] = self.form(None)
        return render(request, self.template_name, context=self.context)

    def post(self, request):
        form = self.form(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            bot = request.POST['bot_catcher']
            if len(bot):
                print("BOT-CATCHER !!!")
                self.context['form'] = self.form
                return render(request, 'bot-catcher.html')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    print(f"Connection of {username}")  # for the logs
                    request.session['language'] = str(user.preferred_language)
                    return HttpResponseRedirect(reverse('app_home:main'))  # return to the index
                else:
                    form.add_error(None, "Userdisabled")
            else:
                print(f"Someone try to login and failed ! user : {username} - psw : {password}")
                form.add_error(None, "Userpswinvalid")
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('app_home:main'))
        self.context['form'] = form
        return render(request, self.template_name, context=self.context)


class LegalView(TemplateView):
    template_name = "app_home/legal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Legal'
        return context


class ContactView(TemplateView):
    template_name = "app_home/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact'
        return context


class Main(View):
    context = {'title': 'Main'}
    template_name = "app_home/main.html"

    def get(self, request):
        return render(request, self.template_name, context=self.context)


class MainView(SortableListView):
    context = {'title': 'Main'}
    template_name = "app_home/main.html"
    context_object_name = "checklists"
    allowed_sort_fields = {"chk_key": {'default_direction': '', 'verbose_name': 'Key'},
                           "chk_title": {'default_direction': '', 'verbose_name': 'Wording'},
                           }
    default_sort_field = 'chk_key'  # mandatory
    paginate_by = 5

    def get_queryset(self):
        order = self.request.GET.get('sort', 'chk_key')
        if self.request.user.is_superuser:
            return CheckList.objects.all().order_by(order)
        else:
            return CheckList.objects.filter(Q(chk_company=self.request.user.user_company)).order_by(order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', 'chk_key')
        context['title'] = 'Main'
        checklistsdone = CheckListDone.objects.filter(cld_company=self.request.user.user_company).\
            order_by('modified_date')[:15]
        context['checklistsdone'] = checklistsdone
        return context
