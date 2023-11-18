from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework import status as http_status

from apps.readings.models import Reading


@csrf_exempt
@login_required
def set_deadline(request, reading_id: int):
    """
    TODO: Should use ReadingViewSet.set_deadline(), but calling that DRF endpoint instead
          of this plain Django one from JS would require handling of JWTs, and I am too
          lazy today.

    TODO: Also, should use DRF serializers to save data. Again, too lazy.
    TODO: use aware time.
    """
    reading = Reading.objects.get(pk=reading_id)

    deadline = request.POST.get("deadline")
    try:
        deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
    except ValueError:
        return HttpResponse(status=http_status.HTTP_400_BAD_REQUEST)

    try:
        deadline_percent = int(request.POST.get("percent", 0))
    except ValueError:
        deadline_percent = 100

    if not (0 <= deadline_percent <= 100):
        deadline_percent = 100

    reading.deadline = deadline
    reading.deadline_percent = deadline_percent
    reading.save()

    return JsonResponse({})
