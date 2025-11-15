# fleur/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Distributor, Slot, Order, OrderStatus
from hardware.bill_acceptor import start_reader_thread
from hardware.doors import open_door
from django.views.decorators.http import require_http_methods


def home(request):
    distributor = Distributor.objects.first()  # simple: une seule machine
    return render(request, "fleur/home.html", {"distributor": distributor})


def bouquets_list(request):
    distributor = Distributor.objects.first()
    slots = distributor.slots.filter(quantity__gt=0, bouquet__isnull=False)
    return render(request, "fleur/bouquets.html", {"slots": slots})


def create_order(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    order = Order.objects.create(
        distributor=slot.distributor,
        slot=slot,
        amount=slot.bouquet.price,
        inserted_amount=0,
        status=OrderStatus.PENDING_PAYMENT,
    )
    # démarrer la lecture du monnayeur pour cette commande (option simple)
    start_reader_thread(order.id)
    return redirect("payment_page", order_id=order.id)


def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "fleur/payment.html", {"order": order})


@require_http_methods(["GET", "POST"])
def test_doors_view(request):
    """
    Page technique pour tester l'ouverture des portes.
    URL: /test-doors/
    """
    distributor = Distributor.objects.first()
    slots = []
    message = None
    response_raw = None

    if distributor:
        slots = distributor.slots.order_by("index")

    if request.method == "POST":
        slot_index_str = request.POST.get("slot_index")
        try:
            slot_index = int(slot_index_str)
        except (TypeError, ValueError):
            message = "Invalid slot index"
        else:
            # appel au module hardware
            resp = open_door(slot_index)
            response_raw = repr(resp)
            message = f"Door {slot_index} command sent."

    context = {
        "distributor": distributor,
        "slots": slots,
        "message": message,
        "response_raw": response_raw,
    }
    return render(request, "fleur/test_doors.html", context)
