from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView

from .forms import EditApplication
from .models import JobApplication


class Applications(LoginRequiredMixin, TemplateView):
    """
    Return the DataTables scaffolding which will be used to request the job application data via the API.
    """
    http_method_names = ["get"]
    template_name = "ApplicationList.html"


class ApplicationDetails(LoginRequiredMixin, UpdateView):
    """
    Handle the adding and updating of the details for a job application.
    """
    http_method_names = ["get", "post"]
    model = JobApplication
    form_class = EditApplication
    pk_url_kwarg = "appid"
    template_name = "ApplicationDetails.html"
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
        app = form.save(commit=False)
        if app.pk or app.id:
            if not app.user_id == self.request.user.id:
                raise PermissionDenied("You cannot change an application owned by another user")
        else:
            app.user_id = self.request.user

        app.save()
        return super().form_valid(form)
