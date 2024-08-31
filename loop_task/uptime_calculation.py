from datetime import datetime, timedelta
import pytz

def convert_to_local(utc_time_input, timezone_str):
    if isinstance(utc_time_input, float):
        # If input is a float (Unix timestamp), convert it to a datetime object
        utc_time = datetime.fromtimestamp(utc_time_input, tz=pytz.utc)
    elif isinstance(utc_time_input, str):
        # If input is a string, parse it using the known format
        utc_format = '%Y-%m-%d %H:%M:%S.%f %Z'
        utc_time = datetime.strptime(utc_time_input, utc_format)
        utc_time = utc_time.replace(tzinfo=pytz.utc)
    else:
        raise ValueError("Unsupported input type for utc_time_input")
    
    # Convert the UTC datetime object to the target timezone
    local_timezone = pytz.timezone(timezone_str)
    local_time = utc_time.astimezone(local_timezone)
    
    return local_time

def piecewise_linear_interpolation(timestamps, interval_start, interval_end):
    uptime_minutes = 0
    downtime_minutes = 0
    
    for i in range(len(timestamps) - 1):
        start_time = timestamps[i][0]
        end_time = timestamps[i + 1][0]
        status = timestamps[i][1]
        
        # Calculate overlap with the interval
        overlap_start = max(start_time, interval_start)
        overlap_end = min(end_time, interval_end)
        
        if overlap_start < overlap_end:
            # Time interval
            interval_duration = (overlap_end - overlap_start).total_seconds() / 60
            
            if status == "active":
                uptime_minutes += interval_duration
            else:
                downtime_minutes += interval_duration
    
    return uptime_minutes, downtime_minutes

def calculate_uptime_downtime_per_period(timestamps, start_time, end_time):
    uptime = {}
    downtime = {}
    current_time = start_time
    
    while current_time < end_time:
        interval_start = current_time
        interval_end = current_time + timedelta(hours=1)
        
        uptime_minutes, downtime_minutes = piecewise_linear_interpolation(
            timestamps,
            interval_start,
            interval_end
        )
        
        hour_key = current_time.strftime('%Y-%m-%d %H:%M')
        uptime[hour_key] = uptime_minutes
        downtime[hour_key] = downtime_minutes
        
        current_time += timedelta(hours=1)
    
    uptime=sum(uptime.values())/60
    downtime=sum(downtime.values())/60
    
    return uptime, downtime

def calculate_uptime_downtime_last_hour(timestamps, start_time):
    uptime = {}
    downtime = {}
    current_time = start_time
    
    interval_start = current_time
    interval_end = current_time + timedelta(hours=1)
        
    uptime_minutes, downtime_minutes = piecewise_linear_interpolation(
            timestamps,
            interval_start,
            interval_end
        )
        
    hour_key = current_time.strftime('%Y-%m-%d %H:%M')
    uptime[hour_key] = uptime_minutes
    downtime[hour_key] = downtime_minutes
        
    
    return uptime, downtime