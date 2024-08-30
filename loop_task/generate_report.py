import csv
from datetime import datetime, timedelta, timezone,time
from .models import StoreStatus, StoreHours, StoreTimezones
from .uptime_calculation import convert_to_local, calculate_uptime_downtime_per_period, calculate_uptime_downtime_last_hour
import pytz



def get_store_timezone(db, store_id):
    # Query the StoreTimezones table to fetch the timezone for the given store_id
    store_timezone = db.query(StoreTimezones).filter_by(store_id=store_id).first()
    
    if store_timezone:
        return store_timezone.timezone_str
    else:
        return "America/Chicago"  # or handle the case where the store_id doesn't exist
    
def get_store_hours(db, store_id, current_day):
    # Query the database for store hours
    store_hours = db.query(StoreHours).filter_by(store_id=store_id, day=current_day).first()
    
    if store_hours:
        # Return the store hours if found
        return store_hours.start_time_local, store_hours.end_time_local
    
    else:
        # Return default times if no store hours found
        current_date = datetime.now().date()

        # Construct datetime objects for the start and end of the current day
        start_time_local = datetime(current_date.year, current_date.month, current_date.day, 0, 0, 0)
        end_time_local = datetime(current_date.year, current_date.month, current_date.day, 23, 59, 59, 999999)
        return start_time_local, end_time_local

def generate_reports_for_all_stores(db):
    # Fetch all unique store_ids from StoreStatus
    store_ids = db.query(StoreStatus.store_id).distinct().all()
    
    dt = datetime.now(timezone.utc) 
  
    utc_time = dt.replace(tzinfo=timezone.utc) 
    current_utc_timestamp = utc_time.timestamp() 

    # Open the CSV file to write the report
    with open('C:\loop_task_new\loop_task\csv\store_uptime_report.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['store_id', 'uptime_last_hour', 'uptime_last_day', 'uptime_last_week'])

        for store_id_tuple in store_ids:
            store_id = store_id_tuple[0]
            
            timezone_str = get_store_timezone(db,store_id)

            current_local_timestamp = convert_to_local(current_utc_timestamp, timezone_str)
            
            # Fetch store-specific data
            store_statuses = db.query(StoreStatus).filter_by(store_id=store_id).all()
            store_timezone = get_store_timezone(db, store_id)
            
            
            current_day =datetime.today().weekday()

            # Convert timestamps to local time
            local_timestamps = [
                (convert_to_local(status.timestamp_utc, store_timezone), status.status)
                for status in store_statuses
            ]

            # Sort the timestamps by time
            local_timestamps.sort(key=lambda x: x[0])

            # Calculate uptime and downtime for the last hour
            start_time_last_hour = current_local_timestamp
            uptime_last_hour, _ = calculate_uptime_downtime_last_hour(local_timestamps, start_time_last_hour)

            # Calculate uptime and downtime for the last day
            
            store_hours = get_store_hours(db, store_id, current_day)
            start_time_last_day = store_hours[0]
            end_time = store_hours[1]
            
            if(isinstance(start_time_last_day,str)):
                utc_format = '%H:%M:%S'
                start_time_last_day=datetime.strptime(start_time_last_day,utc_format)
                end_time=datetime.strptime(end_time,utc_format)
            
            uptime_last_day, _ = calculate_uptime_downtime_per_period(local_timestamps, start_time_last_day, end_time)

            # Calculate uptime and downtime for the last week
            uptime_last_week = 0
            
            for i in range(7):
                day_of_week = (current_day - i) % 7  # Get the correct day of the week
                start_time, end_time = get_store_hours(db, store_id, day_of_week)
                
                if(isinstance(start_time,str)):
                    
                    time_format = "%H:%M:%S"
                    start_time = datetime.strptime(start_time, time_format).time()
                    end_time = datetime.strptime(end_time, time_format).time()
                else:
                    start_time=start_time.time()
                    end_time=end_time.time()
                
                day_start_time = datetime.combine(datetime.today() - timedelta(days=i), start_time).astimezone(pytz.timezone(timezone_str))
                day_end_time = datetime.combine(datetime.today() - timedelta(days=i), end_time).astimezone(pytz.timezone(timezone_str))

                day_uptime= calculate_uptime_downtime_per_period(local_timestamps, day_start_time, day_end_time)[0]
                uptime_last_week += day_uptime
                
            # Write the store's uptime data to the CSV
            writer.writerow([store_id, uptime_last_hour, uptime_last_day, uptime_last_week])

    print("CSV report generated successfully.")

