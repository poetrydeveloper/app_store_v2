# main app store  views
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import RequestItem
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

def requests_view(request):
    status = request.GET.get('status', 'candidate')  # по умолчанию показываем кандидатов
    items = RequestItem.objects.filter(request__status=status).select_related('product', 'request')

    context = {
        'request_items': items,
        'status': status,
    }
    return render(request, 'store/requests.html', context)


@require_POST
def change_status(request):
    item_id = request.POST.get('item_id')
    new_status = request.POST.get('status')

    item = get_object_or_404(RequestItem, id=item_id)
    if new_status in ['candidate', 'in_request', 'extra']:
        item.request.status = new_status
        item.request.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})