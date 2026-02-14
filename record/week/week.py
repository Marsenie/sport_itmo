from datetime import datetime, timedelta
 

def get_this_week_num():
    """1 - чёт, 0 -нечёт"""
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
     
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())
     
    parity = ((d2 - d1).days // 7 + 1) % 2
    return parity
