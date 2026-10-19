from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    group_names = set(request.user.groups.values_list("name", flat=True))
    links = [link for link in settings.PORTAL_LINKS if link["group"] in group_names]
    return render(request, "home.html", {"links": links})
