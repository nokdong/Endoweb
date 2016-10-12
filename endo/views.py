from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

class UserCreateView(CreateView):
    template_name= 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register_done')

class UserCreateDoneTV(TemplateView):
    template_name = 'registration/register_done.html'

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view=super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)