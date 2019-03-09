import posixpath

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views import View
from django.views.static import serve

from .utils import check_signature


class ServeSignedStorageMixin:
    def dispatch(self, request, path, *args, **kwargs):
        try:
            expires = int(self.request.GET['expires'])
            signature = self.request.GET['signature']
        except (ValueError, KeyError):
            raise PermissionDenied()
        is_ok = check_signature(path, signature, expires)
        if not is_ok:
            raise PermissionDenied()
        return super().dispatch(request, path=path, *args, **kwargs)


class ServeSignedStorageLocalView(ServeSignedStorageMixin, View):
    """
    this view should be associated with url
    urlpatterns += [
    re_path(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_SIGNED_URL.lstrip('/')),
            views.ServeSignedStorageLocalView.as_view()),
    ]
    """
    def get(self, request, path, *args, **kwargs):
        return serve(
            request,
            path,
            document_root=settings.MEDIA_SIGNED_ROOT)


class ServeSignedStorageNginxView(ServeSignedStorageMixin, View):
    """
    this view should be associated with url
    urlpatterns += [
    re_path(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_SIGNED_URL.lstrip('/')),
            views.ServeSignedStorageNginxView.as_view()),
    ]
    this view should be used when used with nginx
    """

    def get(self, request, path, *args, **kwargs):
        resp = HttpResponse()
        x_redirect = posixpath.join(settings.MEDIA_SIGNED_URL, path.lstrip("/"))
        resp['X-Accel-Redirect'] = x_redirect
        resp['Content-Type'] = ''
        return resp

