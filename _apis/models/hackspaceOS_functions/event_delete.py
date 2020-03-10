class EventDelete():
    def __init__(self, request=None):
        from _database.models import Event
        from _apis.models import Notify
        from _setup.models import Config
        from django.http import JsonResponse

        if not request or request.user.is_authenticated == False:
            response = JsonResponse(
                {'success': False, 'error': '--> Failed: User not logged in'})
            response.status_code = 403
        elif not request.GET.get('str_slug', None) or Event.objects.filter(str_slug=request.GET.get('str_slug', None)).exists() == False:
            response = JsonResponse(
                {'success': False, 'error': '--> Failed: Result not found'})
            response.status_code = 404
        else:

            # approve event and all upcoming ones
            event = Event.objects.filter(
                str_slug=request.GET.get('str_slug', None)).first()

            print('--> Delete all upcoming events')
            event.delete_series()

            # notify via slack that event was deleted and by who
            if 'HTTP_HOST' in request.META and request.META['HTTP_HOST'] == Config('WEBSITE.DOMAIN').value:
                Notify().send('🚫'+str(request.user)+' deleted the event "' +
                              event.str_name_en_US+'"')

            response = JsonResponse({'success': True})
            response.status_code = 200

        self.value = response
