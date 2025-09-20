from django.core.management.base import BaseCommand
from coreservice.models import Stand  # Adjust 'stand' to your app name

class Command(BaseCommand):
    help = 'Insert multiple Stand records with given parameters'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=int, required=True, help='Start number')
        parser.add_argument('--end', type=int, required=True, help='End number')
        parser.add_argument('--label', type=str, required=True, help='Label prefix (e.g., OE)')
        parser.add_argument('--price', type=float, required=True, help='Price of the stand')
        parser.add_argument('--surface', type=float, required=True, help='Surface of the stand')
        parser.add_argument('--stand_type', type=int, required=True, help='Stand type ID')

    def handle(self, *args, **options):
        start_number = options['start']
        end_number = options['end']
        label_prefix = options['label']
        price = options['price']
        surface = options['surface']
        stand_type_id = options['stand_type']

        stands = []
        for number in range(start_number, end_number + 1):
            booth_label = f"{label_prefix}{number:03}"
            stands.append(
                Stand(
                    label=booth_label,
                    stand_type_id=stand_type_id,
                    price=price,
                    surface=surface
                )
            )


        Stand.objects.bulk_create(stands)
        self.stdout.write(self.style.SUCCESS(f'Successfully inserted {len(stands)} stands!'))
