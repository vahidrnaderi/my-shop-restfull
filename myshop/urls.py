from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.http import HttpResponse
from cms.sitemaps import CMSSitemap
# from myshop.sitemap import ProductSitemap

# sitemaps = {'cmspages': CMSSitemap,
#             'products': ProductSitemap}


def render_robots(request):
    permission = 'noindex' in settings.ROBOTS_META_TAGS and 'Disallow' or 'Allow'
    return HttpResponse('User-Agent: *\n%s: /\n' % permission, content_type='text/plain')


schema_view = get_schema_view(
    openapi.Info(
        title="Shop",
        default_version="v1",
        description="Django Shop",
        terms_of_service="",
        contact=openapi.Contact(email="info@blarebit.com"),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

i18n_urls = (
    url(r'^admin/', admin.site.urls),
    url(r'^', include('cms.urls')),
)
urlpatterns = [
    url(r'^robots\.txt$', render_robots),
    # url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    url(r'^shop/', include('shop.urls')),
    # Swagger.
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
if settings.USE_I18N:
    urlpatterns.extend(i18n_patterns(*i18n_urls))
else:
    urlpatterns.extend(i18n_urls)
urlpatterns.extend(
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
