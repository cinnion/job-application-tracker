from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView

from core.views.mixins import Log404Mixin
from .forms import EditApplication
from .models import JobApplication


class Applications(LoginRequiredMixin, Log404Mixin, TemplateView):
    """
    Return the DataTables scaffolding which will be used to request the job application data via the API.
    """
    http_method_names = ["get"]
    template_name = "ApplicationList.html"
    login_url = reverse_lazy("login")


class ApplicationDetails(LoginRequiredMixin, Log404Mixin, UpdateView):
    """
    Handle the adding and updating of the details for a job application.
    """
    http_method_names = ["get", "post"]
    model = JobApplication
    form_class = EditApplication
    pk_url_kwarg = "appid"
    template_name = "ApplicationDetails.html"
    login_url = reverse_lazy("login")
    success_url = reverse_lazy("applications:application-list")

    def get_object(self, queryset=None) -> Model:
        """
        Get the desired job application, or an empty instance of the model if neither the primary key or slug are
        specified, which will call the supermethod to throw an AttributeError. If one of those two is specified
        and the record belongs to another user, our queryset will result in a 404 exception being thrown, which will
        go uncaught.
        """
        try:
            return super().get_object(queryset)
        except AttributeError:
            pass

        return self.model()

    def get_queryset(self):
        """
        Allow users only to access their own applications.
        """
        return super().get_queryset().filter(user_id=self.request.user.id)

    def form_valid(self, form):
        """
        Set the user field on new records so that Django sets user_id in the backend.

        NOTE: Protections against record hijacking is not needed, since Django will raise a Http404 error before we even
        get here.
        """
        app = form.save(commit=False)

        #  Only set the user on new records
        if not (app.pk or app.id):
            app.user = self.request.user

        app.save()
        return super().form_valid(form)
