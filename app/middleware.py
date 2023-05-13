from .models import Notification

class MyMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        user = request.user
        if user.is_authenticated:
            notifications = Notification.objects.filter(customer=user).order_by('-create_at')[:5]
            response.set_cookie('notifications', notifications)
        return response