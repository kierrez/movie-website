from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^', include('movie.urls')),
    # url(r'^recommend/', include('recommend.urls')),
    # url(r'^charts/', include('chart.urls')),
    # url(r'^book/', include('book.urls')),
    # url(r'^search/', include('haystack.urls')),
    # url(r'^contact/', include('contact.urls')),

    # url(r'^api/', include('movie.api.urls', namespace='api-movie')),
    url(r'^api/', include('api.urls', namespace='api')),
    # url(r'^api/', include('api.urls')),

    # url(r'^school/', include('school.urls')),
    # url(r'^api-school/', include('school.api.urls', namespace='api-school')),


    url(r'^users/', include('users.urls')),
    # url(r'^user-api/', include('school.api.urls')),


]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)