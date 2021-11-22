from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class CSRFTokenExemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        referer = request.META.get("HTTP_REFERER")
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE") and referer is not None:
            try:
                path = referer.split("//")[1].split("/")[0]
                if path in settings.AJAX_REFERER_WHITE_LIST:
                    setattr(request, "_dont_enforce_csrf_checks", True)
            except Exception:
                pass
        return None
