from collections import defaultdict
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import DateField, IntegerField, Sum, Count, F
from django.db.models.fields import TimeField
from django.db.models.functions import TruncDay, TruncMonth, TruncHour, ExtractWeek, TruncWeek
from django.utils import timezone
from django_countries.fields import Country
import locale

from coreservice.models import Payment, Ticket, Invoice, Exhibitor, Badge, Booking, Event, EventStand, BookingDetail

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


# New Report View
class EventReportHelper:
    def __init__(self, event):
        self.event = Event.objects.get(pk=event.id)

    def invoice_income_summary(self):

        invoices = Invoice.objects.filter(booking__exhibitor__is_sponsored=False, booking__event=self.event)

        amount_ttc = invoices.aggregate(total=Sum('amount_total'))['total'] or 0
        amount_paid = invoices.filter(status__in=['Partially Paid', 'Paid']).aggregate(total=Sum('amount_paid'))[
                          'total'] or 0
        amount_due = amount_ttc - amount_paid

        data = {
            "amount_ttc": f"{intcomma(int(amount_ttc))} FCFA",
            "amount_paid": f"{intcomma(int(amount_paid))} FCFA",
            "amount_due": f"{intcomma(int(amount_due))} FCFA",
        }

        return data

    def tickets_income_summary(self):

        tickets = Payment.objects.filter(
            booking__event=self.event,
            category__in=["Achat de Ticket"],
            status=1
        ).aggregate(total=Sum('amount'))['total'] or 0

        return f"{intcomma(int(tickets))} FCFA"

    def event_total_income_summary(self):

        invoices = Invoice.objects.filter(booking__exhibitor__is_sponsored=False, booking__event=self.event)
        amount_paid = invoices.filter(status__in=['Partially Paid', 'Paid']).aggregate(total=Sum('amount_paid'))[
                          'total'] or 0
        tickets = Payment.objects.filter(
            booking__event=self.event,
            category__in=["Achat de Ticket"],
            status=1
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_income = amount_paid + tickets

        return f"{intcomma(int(total_income))} FCFA"

    def exhibitors_summary(self):

        active_statuses = ['Pending Confirmation', 'Pending Payment', 'Partially Paid', 'Reserved']

        total_exhibitors = Exhibitor.objects.filter(
            booking__event_id=self.event.id,
            booking__booking_status__in=active_statuses
        ).count()

        return total_exhibitors

    def weekly_badge(self, **kwargs):

        start_date = kwargs.get('start_date', '').strip()
        end_date = kwargs.get('end_date', '').strip()

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            end_date = end_date - timedelta(minutes=1)
        else:
            start_date = self.event.registration_start_date
            end_date = self.event.end_date

        badges_qs = Badge.objects.filter(
            event=self.event.id,
            created_at__range=[start_date, end_date]
        ).annotate(week=F("created_at__week")).values("week").annotate(count=Count("id")).order_by("week")

        return [{"x": f"Semaine {b['week']}", "y": b["count"]} for b in badges_qs]

    def event_sponsors(self):

        sponsor_count = Exhibitor.objects.filter(
            is_sponsored=True,
            booking__event_id=self.event.id
        ).distinct().count()

        return sponsor_count

    def total_booking(self):

        total_bookings = Booking.objects.filter(event=self.event, exhibitor__is_sponsored=False).count()

        return total_bookings

    def event_income_chart(self, **kwargs):

        start_date = kwargs.get('start_date', '').strip()
        end_date = kwargs.get('end_date', '').strip()
        group_by = kwargs.get('group_by', 'month').strip()

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            end_date = end_date - timedelta(minutes=1)

        else:
            start_date = self.event.registration_start_date
            end_date = self.event.end_date

        if group_by == "day":
            trunc_func = TruncDay
        else:
            trunc_func = TruncMonth

        revenue_qs = Payment.objects.filter(
            category__in=["Paiement de Facture", "Achat de Badge"], status=1,
            booking__event=self.event,
            created_at__range=[start_date, end_date]
        ).annotate(
            period=trunc_func("created_at")
        ).values("period").annotate(
            total=Sum("amount")
        ).order_by("period")

        revenue_data = [
            {"labels": f'{str(entry["period"].strftime("%Y-%m-%d" if group_by == "day" else "%b")).title() or 0}',
             "value": (int(entry["total"]) or 0)}
            for entry in revenue_qs
        ]

        return revenue_data

    def ticket_sold_chart(self, **kwargs):

        start_date = self.event.start_date
        end_date = self.event.end_date

        revenue_qs = Payment.objects.filter(
            event_id=self.event.id,
            category="Achat de Ticket", status=1,
        ).annotate(
            week=TruncWeek("created_at")
        ).values("week").annotate(
            count=Count("id")
        ).order_by("week")

        tickets_data = [
            {
                "labels": f"{entry['week'].date()}",
                "value": entry["count"]
            }
            for entry in revenue_qs
        ]

        return tickets_data

    def exhibitor_country_chart(self, **kwargs):

        active_statuses = ['Pending Confirmation', 'Pending Payment', 'Partially Paid', 'Reserved']

        country_data_qs = Exhibitor.objects.filter(
            is_sponsored=False,
            booking__event_id=self.event.id,
            booking__booking_status__in=active_statuses
        ).values("country").annotate(
            count=Count("id")
        ).order_by("-count")

        country_data = {
            "labels": [Country(entry["country"]).name for entry in country_data_qs],
            "series": [entry["count"] for entry in country_data_qs],
        }

        return country_data

    def stand_utilisation_chart(self, **kwargs):

        event_stands_qs = EventStand.objects.filter(event=self.event)
        total_event_stands = event_stands_qs.count()

        occupied_stand_ids = BookingDetail.objects.filter(
            booking__event=self.event
        ).values_list("booth_id", flat=True).distinct()

        occupied_stands = occupied_stand_ids.count()
        available_stands = total_event_stands - occupied_stands

        stand_occupancy_pie = {
            "labels": ["Occupé", "Disponible"],
            "series": [occupied_stands, available_stands]
        }

        return stand_occupancy_pie

    def global_stand_visualization_chart(self, **kwargs):
        event_stands = EventStand.objects.filter(
            event=self.event,
        ).select_related("stand")

        # Prepare dict to hold counts per stand type
        stand_type_counts = defaultdict(lambda: {"total": 0, "occupied": 0})

        # Get all occupied booth IDs
        occupied_booth_ids = set(
            BookingDetail.objects.filter(
                booking__event=self.event,
            ).values_list("booth_id", flat=True)
        )

        # Iterate over EventStands
        for es in event_stands:
            stand = es.stand
            if not stand:
                stand_type_name = "Unknown Stand"
            elif stand.stand_type:
                stand_type_name = stand.stand_type.name
            else:
                stand_type_name = "Uncategorized"

            stand_type_counts[stand_type_name]["total"] += 1

            if stand and stand.id in occupied_booth_ids:
                stand_type_counts[stand_type_name]["occupied"] += 1

        # Final formatted list for chart
        stand_type_occupancy = []
        for st_name, counts in stand_type_counts.items():
            available = counts["total"] - counts["occupied"]
            stand_type_occupancy.append({
                "type": st_name,
                "occupied": counts["occupied"],
                "available": available
            })
        return stand_type_occupancy

    def standtype_distribution_chart(self, **kwargs):

        event_stands = EventStand.objects.filter(event=self.event).select_related('stand__stand_type')

        # Track all StandTypes related to the Event via EventStand
        standtype_counts = {}

        for event_stand in event_stands:
            stand = event_stand.stand
            if not stand or not stand.stand_type:
                continue

            stand_type_name = stand.stand_type.name

            if stand_type_name not in standtype_counts:
                standtype_counts[stand_type_name] = {"booked": 0, "available": 0}

            # Is this stand booked?
            if BookingDetail.objects.filter(booth=stand).exists():
                standtype_counts[stand_type_name]["booked"] += 1
            else:
                standtype_counts[stand_type_name]["available"] += 1

        # Prepare ApexChart format
        categories = list(standtype_counts.keys())
        available_data = [standtype_counts[name]["available"] for name in categories]
        booked_data = [standtype_counts[name]["booked"] for name in categories]

        data = {
            "categories": categories,
            "series": [
                {"name": "Disponible", "data": available_data},
                {"name": "Occupé", "data": booked_data},
            ]
        }

        return data

    def badge_type_donut_chart(self):

        data = (
            Badge.objects
            .filter(event=self.event)
            .values('badge_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        labels = [entry['badge_type'] or 'Unknown' for entry in data]
        series = [entry['count'] for entry in data]

        badge_type = {
            "labels": labels,
            "series": series
        }

        return badge_type
