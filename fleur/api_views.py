# fleur/api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Order, OrderStatus
from hardware.doors import open_door


@csrf_exempt
def bill_credit_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        order_id = int(data["order_id"])
        amount = int(data["amount"])
    except Exception:
        return JsonResponse({"detail": "Bad request"}, status=400)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"detail": "Order not found"}, status=404)

    order.add_credit(amount)

    # quand payé, on ouvre la porte
    if order.status == OrderStatus.PAID:
        open_door(order.slot.index)
        order.status = OrderStatus.VENDING
        order.save()

    return JsonResponse({
        "ok": True,
        "order_id": order.id,
        "inserted_amount": float(order.inserted_amount),
        "status": order.status,
    })


def order_status_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"detail": "Order not found"}, status=404)

    return JsonResponse({
        "order_id": order.id,
        "amount": float(order.amount),
        "inserted_amount": float(order.inserted_amount),
        "status": order.status,
        "slot_index": order.slot.index,
    })
