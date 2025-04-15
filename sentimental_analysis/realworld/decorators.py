from django.http import HttpResponse
from functools import wraps
from .models import ApiCache
from .utils import get_request_hash

def cache_response(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Decide which methods to cache: for example, GET and POST.
        if request.method.lower() in ('get', 'post'):
            req_hash = get_request_hash(request)
            try:
                cache_obj = ApiCache.objects.get(request_hash=req_hash)
                # Return the cached response.
                return HttpResponse(cache_obj.response_data)
            except ApiCache.DoesNotExist:
                # No cache found; call the view function.
                response = view_func(request, *args, **kwargs)
                if response.status_code == 200:
                    try:
                        # Cache the response data.
                        ApiCache.objects.create(
                            request_hash=req_hash,
                            response_data=response.content.decode('utf-8')
                        )
                    except Exception as e:
                        print("Error caching response:", e)
                return response
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view
