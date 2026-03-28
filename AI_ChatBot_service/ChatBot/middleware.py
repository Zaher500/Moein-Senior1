from django.http import JsonResponse
from django.conf import settings

class GatewaySecretMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        gateway_secret = request.headers.get('X-GATEWAY-SECRET')

        if gateway_secret != getattr(settings, 'GATEWAY_SECRET', None):
            return JsonResponse(
                {'error': 'Direct access forbidden, use API Gateway'},
                status=403
            )

        return self.get_response(request)