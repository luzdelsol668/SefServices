from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import DateField, IntegerField, Sum, Count
from django.db.models.fields import TimeField
from django.db.models.functions import TruncDay, TruncMonth, TruncHour
from django.utils import timezone

from coreservice.models import Payment, Ticket


def get_today_payment():

    current_time = timezone.now().today()
    start_time = current_time.replace(hour=0, minute=0, second=0)

    payments = Payment.objects.filter(created_at__range=[start_time, current_time], status=1)
    tickets = Ticket.objects.filter(created_at__range=[start_time, current_time], is_paid=True)

    tickets_revenue =  (
        payments.filter(category="Achat de Ticket")
        .annotate(hour=TruncHour("created_at", output_field=TimeField()))
        .values("hour")
        .annotate(
            total=Sum("amount", output_field=IntegerField()),
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("hour")
    )

    total_tickets =  (
        tickets.annotate(hour=TruncHour("created_at", output_field=TimeField()))
        .values("hour")
        .annotate(
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("hour")
    )

    booking_revenue = (
        payments.filter(category="Paiement de Facture")
        .annotate(hour=TruncHour("created_at", output_field=TimeField()))
        .values("hour")
        .annotate(
            total=Sum("amount", output_field=IntegerField()),
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("hour")
    )

    ticket_dict = {entry["hour"].strftime("%H"): {"total": entry["total"], "count": entry["count"]} for entry in tickets_revenue}
    total_ticket_dict = {entry["hour"].strftime("%H"): {"count": entry["count"]} for entry in total_tickets}
    booking_dict =  {entry["hour"].strftime("%H"): {"total": entry["total"], "count": entry["count"]} for entry in booking_revenue}

    chart_data = []

    current_hour = start_time

    while current_hour <= current_time:
        day_str = current_hour.strftime("%H")
        chart_data.append({
            "labels": f"{day_str}H",
            "tickets_value": ticket_dict.get(day_str,{}).get("total", 0),
            "tickets_count": total_ticket_dict.get(day_str, {}).get("count", 0),
            "booking_value": booking_dict.get(day_str, {}).get("total", 0),
            "booking_count": booking_dict.get(day_str, {}).get("count", 0),

        })
        current_hour += timedelta(hours=1)  # Move to the next day

    return chart_data

def get_past_30_payment():

    current_month = timezone.now().today().replace(hour=23, minute=59, second=59)
    last_month = current_month.replace(day=1, hour=0, minute=0, second=0) - relativedelta(months=1)

    payments = Payment.objects.filter(created_at__range=[last_month, current_month], status=1)
    tickets = Ticket.objects.filter(created_at__range=[last_month, current_month], is_paid=True)


    tickets_revenue =  (
        payments.filter(category="Achat de Ticket")
        .annotate(day=TruncDay("created_at", output_field=DateField()))
        .values("day")
        .annotate(
            total=Sum("amount", output_field=IntegerField()),
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("day")
    )

    total_tickets = (
        tickets.annotate(day=TruncDay("created_at", output_field=DateField()))
        .values("day")
        .annotate(
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("day")
    )

    booking_revenue = (
        payments.filter(category="Paiement de Facture")
        .annotate(day=TruncDay("created_at", output_field=DateField()))
        .values("day")
        .annotate(
            total=Sum("amount", output_field=IntegerField()),
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("day")
    )

    ticket_dict = {entry["day"].strftime("%d-%m-%Y"): {"total": entry["total"], "count": entry["count"]} for entry in tickets_revenue}
    total_ticket_dict = {entry["day"].strftime("%d-%m-%Y"): {"count": entry["count"]} for entry in total_tickets}
    booking_dict =  {entry["day"].strftime("%d-%m-%Y"): {"total": entry["total"], "count": entry["count"]} for entry in booking_revenue}

    chart_data = []
    current_day = last_month

    while current_day <= current_month:
        day_str = current_day.strftime("%d-%m-%Y")
        chart_data.append({
            "labels": day_str,
            "tickets_value": ticket_dict.get(day_str,{}).get("total", 0),
            "tickets_count": total_ticket_dict.get(day_str, {}).get("count", 0),
            "booking_value": booking_dict.get(day_str, {}).get("total", 0),
            "booking_count": booking_dict.get(day_str, {}).get("count", 0),

        })
        current_day += timedelta(days=1)  # Move to the next day

    return chart_data

def get_past_annual_payment():

    current_year = timezone.now().today().replace(hour=23, minute=59, second=59)
    last_year = current_year.replace(day=1, hour=0, minute=0, second=0) - relativedelta(months=12)

    payments = Payment.objects.filter(created_at__range=[last_year, current_year], status=1)
    tickets = Ticket.objects.filter(created_at__range=[last_year, current_year], is_paid=True)


    tickets_revenue =  (
        payments.filter(category="Achat de Ticket")
        .annotate(month=TruncMonth("created_at", output_field=DateField()))
        .values("month")
        .annotate(
            total=Sum("amount", output_field=IntegerField()),
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("month")
    )

    total_tickets = (
        tickets.annotate(month=TruncMonth("created_at", output_field=DateField()))
        .values("month")
        .annotate(
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("month")
    )

    booking_revenue = (
        payments.filter(category="Paiement de Facture")
        .annotate(month=TruncMonth("created_at", output_field=DateField()))
        .values("month")
        .annotate(
            total=Sum("amount", output_field=IntegerField()),
            count=Count("id", output_field=IntegerField()),
        )
        .order_by("month")
    )

    year_ticket_dict = {entry["month"].strftime("%b %Y"): {"total": entry["total"], "count": entry["count"]} for entry in tickets_revenue}
    year_total_ticket_dict = {entry["month"].strftime("%b %Y"): {"count": entry["count"]} for entry in total_tickets}
    year_booking_dict =  {entry["month"].strftime("%b %Y"): {"total": entry["total"], "count": entry["count"]} for entry in booking_revenue}

    chart_data = []
    current_month = last_year

    while current_month <= current_year:
        day_str = current_month.strftime("%b %Y")

        chart_data.append({
            "labels": day_str,
            "tickets_value": year_ticket_dict.get(day_str,{}).get("total", 0),
            "tickets_count": year_total_ticket_dict.get(day_str, {}).get("count", 0),
            "booking_value": year_booking_dict.get(day_str, {}).get("total", 0),
            "booking_count": year_booking_dict.get(day_str, {}).get("count", 0),

        })
        current_month += relativedelta(months=1)  # Move to the next day

    return chart_data

def payment_category_chart():

    payments = Payment.objects.values('category').annotate(total_amount=Sum('amount'))

    labels = [payment['category'] for payment in payments]
    data = [int(payment['total_amount']) for payment in payments]  # Convert Decimal to float for JSON

    chart_data = [{
        "labels": labels,
        "data": data,
    }]

    return chart_data


def global_reports(event):
    # Optional: date filtering
    if start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        # fallback to event dates
        event = Event.objects.get(id=event_id)
        start_date = event.registration_start_date
        end_date = event.end_date

    # 1. Total Revenue (excluding sponsors & status != 1)
    total_revenue_qs = Payment.objects.filter(
        booking__event_id=event_id,
        booking__exhibitor__is_sponsored=False,
        paid_at__range=[start_date, end_date]
    ).values("paid_at").annotate(total=Sum("amount")).order_by("paid_at")

    revenue_data = [
        {"x": p["paid_at"].strftime("%Y-%m-%d"), "y": float(p["total"])} for p in total_revenue_qs
    ]

    # 2. Total Exhibitors (non-sponsors with active booking status)
    active_statuses = ['Pending Confirmation', 'Pending Payment', 'Partially Paid', 'Reserved']
    total_exhibitors = Exhibitor.objects.filter(
        is_sponsored=False,
        booking__event_id=event_id,
        booking__booking_status__in=active_statuses
    ).distinct().count()

    # 3. Badges Per Week
    badges_qs = Badge.objects.filter(
        event_id=event_id,
        created_at__range=[start_date, end_date]
    ).annotate(week=F("created_at__week")).values("week").annotate(count=Count("id")).order_by("week")

    badges_data = [{"x": f"Semaine {b['week']}", "y": b["count"]} for b in badges_qs]

    # 4. Stand Occupancy
    total_event_stands = EventStand.objects.filter(event_id=event_id).count()
    occupied_stands = BookingDetail.objects.filter(
        booking__event_id=event_id
    ).values("booth_id").distinct().count()

    # 5. Total Sponsors
    sponsor_count = Exhibitor.objects.filter(
        is_sponsored=True,
        booking__event_id=event_id
    ).distinct().count()

    # 6. Total Bookings
    total_bookings = Booking.objects.filter(event_id=event_id).count()

    return JsonResponse({
        "revenue_data": revenue_data,
        "total_exhibitors": total_exhibitors,
        "badges_data": badges_data,
        "total_event_stands": total_event_stands,
        "occupied_stands": occupied_stands,
        "sponsor_count": sponsor_count,
        "total_bookings": total_bookings,
    })















