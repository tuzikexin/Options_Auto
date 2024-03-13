import logging
from pytz import timezone
import argparse
from datetime import datetime


def str2bool(v):
    # Convert string inputs to boolean values
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')



class CETFormatter(logging.Formatter):
    # Custom log formatter to include CET timezone
    cet = timezone('America/New_York')

    def converter(self, timestamp):
        return datetime.fromtimestamp(timestamp, self.cet)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()
