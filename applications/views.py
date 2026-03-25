from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import JobApplication
from . import forms


@login_required
def applications_list(request):
    return render(request, 'ApplicationList.html')


@login_required
def application_details(request, appid=None):
    if appid:
        app = get_object_or_404(JobApplication, pk=appid)
    else:
        app = JobApplication()

    form = forms.EditApplication(request.POST or None, instance=app)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('applications:application-list')

    return render(request, 'ApplicationDetails.html', {'form': form})
