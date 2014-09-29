from django.conf.urls import patterns, include, url
import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'st.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'newstopics.views.index'),

    url(r'^simple_search/', 'newstopics.views.simple_search'),
    url(r'^advanced_search/', 'newstopics.views.advanced_search'),

    url(r'^submit_query/$', 'newstopics.views.process_query'),

    url(r'^vis_termclouds/$', 'newstopics.views.vis_termclouds'),

)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),)
