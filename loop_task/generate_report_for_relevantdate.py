import csv
from datetime import datetime, timedelta, timezone, time
from .models import StoreStatus, StoreHours, StoreTimezones
from .uptime_calculation import convert_to_local, calculate_uptime_downtime_per_period, calculate_uptime_downtime_last_hour
import pytz

# The provided reference UTC timestamp for the specific store ID
reference_timestamp_str = "2023-01-19 06:20:13.933947 UTC"
reference_timestamp = datetime.strptime(reference_timestamp_str, "%Y-%m-%d %H:%M:%S.%f %Z")

def get_store_timezone(db, store_id):
    store_timezone = db.query(StoreTimezones).filter_by(store_id=store_id).first()
    if store_timezone:
        return store_timezone.timezone_str
    else:
        return "America/Chicago"  # Default or fallback timezone
    
def get_store_hours(db, store_id, current_day):
    store_hours = db.query(StoreHours).filter_by(store_id=store_id, day=current_day).all()
    if store_hours:
        return [(sh.start_time_local, sh.end_time_local) for sh in store_hours]
    else:
        start_time_local = datetime.combine(reference_timestamp.date(), time(0, 0, 0))
        end_time_local = datetime.combine(reference_timestamp.date(), time(23, 59, 59, 999999))
        return [(start_time_local, end_time_local)]

def generate_report_for_specific_store(db):
    store_id = 3900231063921710249
    
    # Adjusted to use the provided reference timestamp
    utc_time = reference_timestamp.replace(tzinfo=timezone.utc)
    current_utc_timestamp = utc_time.timestamp()

    with open(f'C:\\loop_task_new\\loop_task\\csv\\store_uptime_report_{store_id}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week'])
        
        timezone_str = get_store_timezone(db, store_id)
        current_local_timestamp = convert_to_local(current_utc_timestamp, timezone_str)
        
        store_statuses = db.query(StoreStatus).filter_by(store_id=store_id).all()
        store_timezone = get_store_timezone(db, store_id)
        
        current_day = reference_timestamp.weekday()

        local_timestamps = [
            (convert_to_local(status.timestamp_utc, store_timezone), status.status)
            for status in store_statuses
        ]

        local_timestamps.sort(key=lambda x: x[0])

        # Adjusted to use the provided reference timestamp
        start_time_last_hour = current_local_timestamp
        uptime_last_hour, _ = calculate_uptime_downtime_last_hour(local_timestamps, start_time_last_hour)

        store_hours = get_store_hours(db, store_id, current_day)

        # Calculate uptime for the last day considering multiple periods
        uptime_last_day = 0
        for start_time_str, end_time_str in store_hours:
            # Convert strings to datetime.time objects
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
            end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

            start_time_local = datetime.combine(reference_timestamp.date(), start_time).astimezone(pytz.timezone(timezone_str))
            end_time_local = datetime.combine(reference_timestamp.date(), end_time).astimezone(pytz.timezone(timezone_str))

            period_uptime, _ = calculate_uptime_downtime_per_period(local_timestamps, start_time_local, end_time_local)
            uptime_last_day += period_uptime

        # Calculate uptime for the last week
        uptime_last_week = 0
        for i in range(7):
            day_of_week = (current_day - i) % 7
            daily_hours = get_store_hours(db, store_id, day_of_week)
            
            for start_time_str, end_time_str in daily_hours:
                # Convert strings to datetime.time objects
                start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
                end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
                
                day_start_time = datetime.combine(reference_timestamp.date() - timedelta(days=i), start_time).astimezone(pytz.timezone(timezone_str))
                day_end_time = datetime.combine(reference_timestamp.date() - timedelta(days=i), end_time).astimezone(pytz.timezone(timezone_str))

                day_uptime = calculate_uptime_downtime_per_period(local_timestamps, day_start_time, day_end_time)[0]
                uptime_last_week += day_uptime
            
        writer.writerow([store_id, uptime_last_hour, uptime_last_day, uptime_last_week])

    print(f"CSV report generated successfully for store_id {store_id}.")
