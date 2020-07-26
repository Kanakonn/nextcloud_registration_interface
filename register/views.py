from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView

from register.forms import RegisterForm, GenerateInvitesForm
from register.models import InviteCode


class RegisterView(FormView):
    template_name = "register/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy('register')

    def get_context_data(self, **kwargs):
        context = super(RegisterView, self).get_context_data(**kwargs)
        context['server_name'] = settings.NEXTCLOUD_NAME
        return context

    def form_valid(self, form):
        # success, msg = form.dum_create_account()
        success, msg = form.create_account()
        if success and msg != "":
            messages.warning(self.request, "Account was created, but some error(s) occurred:\n{}".format(msg))
        elif success:
            messages.success(self.request, "Account created, you should now be able to log in on <a href=\"{}\">{}</a>".format(settings.NEXTCLOUD_URL, settings.NEXTCLOUD_NAME))
        else:
            messages.error(self.request, "Could not create your account!\n{}".format(msg))
        return super(RegisterView, self).form_valid(form)


class GenerateInvitesView(LoginRequiredMixin, FormView):
    template_name = "register/generate.html"
    form_class = GenerateInvitesForm
    success_url = reverse_lazy('generate')

    def get_context_data(self, **kwargs):
        context = super(GenerateInvitesView, self).get_context_data(**kwargs)
        context['default_group'] = settings.NEXTCLOUD_GROUP_NAME
        context['available_codes'] = InviteCode.objects.filter(used=False).order_by('group')
        context['used_codes'] = InviteCode.objects.filter(used=True).order_by('group')
        context['server_name'] = settings.NEXTCLOUD_NAME
        return context

    def form_valid(self, form):
        num, codes = form.generate_codes()
        codes_html = "<ul>"
        if len(codes) == 0:
            codes_html += "<li>No codes have been generated.</li>"
        for code in codes:
            codes_html += "<li>{}</li>".format(code.code)
        codes_html += "</ul>"
        messages.success(self.request, "{} new invite codes generated, see below:<br />{}".format(num, codes_html))
        return super(GenerateInvitesView, self).form_valid(form)

