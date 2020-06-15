from datetime import datetime
import time

def pretty_date(given_date=None, format='default'):
    # Select date
    if type(given_date) is int:
        ## timestamp
        dt = datetime.fromtimestamp(given_date)
    
    elif isinstance(given_date, datetime):
        ## datetime object
        print('datetime')
        dt = given_date
    
    elif not given_date:
        ## current date
        dt = datetime.now()
    
    # Select format
    if (format == 'default'):
        # 11/05 23h28
        out = '{day}/{month} {hour}h{minute}'.format( \
                day    = str(dt.day).zfill(2), \
                month  = str(dt.month).zfill(2), \
                hour   = str(dt.hour).zfill(2), \
                minute = str(dt.minute).zfill(2))
    
    elif (format == 'long'):
        # 11/05/2020 23h28
        out = '{day}/{month}/{year} {hour}h{minute}'.format( \
                day    = str(dt.day).zfill(2), \
                month  = str(dt.month).zfill(2), \
                year   = str(dt.year).zfill(4), \
                hour   = str(dt.hour).zfill(2), \
                minute = str(dt.minute).zfill(2))
    
    elif (format == 'filename'):
        # 11-05-2020_23h28
        out = '{day}-{month}-{year}_{hour}h{minute}'.format( \
                day    = str(dt.day).zfill(2), \
                month  = str(dt.month).zfill(2), \
                year   = str(dt.year).zfill(4), \
                hour   = str(dt.hour).zfill(2), \
                minute = str(dt.minute).zfill(2))
    
    return(out)

# print(pretty_date())
# print(pretty_date(format='long'))
# print(pretty_date(format='filename'))
