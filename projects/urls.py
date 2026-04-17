from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # add by sakhawat
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.subscription.urls')),
    path('api/v1/', include('apps.chats.urls')),
    path('api/v1/', include('apps.smartcase.urls')),
    path('api/v1/', include('apps.contact_support.urls')),
    path('api/v1/', include('apps.cms.urls')),
    path('api/v1/', include('apps.resources.urls')),
    
    # path('api/v1/', include('apps.prisons.urls')),

    path('api/v1/', include('apps.newsletter.urls')),
]


urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)