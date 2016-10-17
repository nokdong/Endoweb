"""procedure URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from procedure import views

urlpatterns = [
    url(r'^$', views.ExamCreateView.as_view(), name='basic'),
    url(r'^add/$', views.ExamCreateView.as_view(), name='add'),
    url(r'^search/$', views.ProcedureFormView.as_view(), name='search'),
    url(r'^reading/$', views.ReadingListView.as_view(), name="readinglist"),
    url(r'^(?P<pk>[0-9]+)/readingupdate/$', views.ReadingUpdateview.as_view(), name="readingupdate"),
    url(r'^biopsy/$', views.BxListView.as_view(), name="biopsy"),
    url(r'^(?P<pk>[0-9]+)/update/$', views.BxUpdateview.as_view(), name="update"),
    url(r'^phone/$', views.phone, name="phone"),
    url(r'^(?P<pk>[0-9]+)/phonecheck/$', views.PhoneCheck.as_view(), name="phonecheck"),
    url(r'^today/$', views.today, name="today"),
    url(r'^thismonth/$', views.thismonth, name="thismonth"),
    url(r'^thisyear/$', views.graph, name="thisyear"),
    url(r'^(?P<pk>[0-9]+)/revisit/$', views.ReVisit.as_view(), name='revisit'),
]
