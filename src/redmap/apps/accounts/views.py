from redmap.apps.accounts.forms import Person as PersonForm
from redmap.common.generic_views import AuthMixin
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django_facebook import signals
from redmap.apps.redmapdb.models import FBGroup, PersonInGroup, Person, Sighting, User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from zinnia.models import Entry
from haystack.query import SearchQuerySet
from redmap.apps.cms.models import Page


@login_required
def Profile(request):

    context = {
        'user': request.user,
        'sightings': Sighting.objects.filter(user=request.user).\
            order_by('-sighting_date'),
        'count': Sighting.objects.filter(user=request.user).count(),
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def EditProfile(request, template_name='accounts/edit_profile.html'):

    profile = request.user.get_profile()

    form = PersonForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if request.POST and form.is_valid():

        form.save()
        messages.success(request, "Your profile was successfully updated.")
        return redirect(reverse('acct_profile'))

    context = {
        'form': form,
        'profile': profile
    }

    return render(request, template_name, context)


def ViewProfile(request, username=None, template_name='accounts/view_profile.html'):

    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = user.get_profile()

    sightings = Sighting.objects.filter(user=user).get_verified_or_valid()
    photo_sightings = sightings.get_public_photo()

    context = {
        'user': user,
        'sightings': sightings,
        'photo_sightings': photo_sightings,
    }

    if profile.is_scientist:
        template_name = 'accounts/scientist_profile.html'
        sightings_verified = Sighting.objects.get_valid_sightings_verified_by_scientist(user)

        # get a few articles and links
        context.update({
            'sightings_verified': sightings_verified,
            'published_articles': Entry.published.filter(author=user.username),
            'related_links': SearchQuerySet().more_like_this(profile).models(Page, Entry)
        })

    return render(request, template_name, context)


class MyGroups(ListView):

    context_object_name = 'groups'
    template_name = 'accounts/my_groups.html'

    def get_queryset(self):
        return PersonInGroup.objects.filter(person=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(MyGroups, self).get_context_data(**kwargs)

        for group in context['groups']:
            group.members = FBGroup.objects.count_members(group.group)

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyGroups, self).dispatch(*args, **kwargs)
