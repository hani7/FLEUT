# fleur/management/commands/open_door.py
from django.core.management.base import BaseCommand
from hardware.doors import open_door

class Command(BaseCommand):
    help = "Ouvre une porte via RS485"

    def add_arguments(self, parser):
        parser.add_argument("slot_index", type=int, help="Numéro de porte à ouvrir")

    def handle(self, *args, **options):
        slot_index = options["slot_index"]
        self.stdout.write(f"Ouverture porte {slot_index}...")
        resp = open_door(slot_index)
        self.stdout.write(f"Réponse: {resp!r}")
