#!/bin/bash

# Get the current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Execute Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer
from datetime import datetime, timedelta
cutoff = datetime.now() - timedelta(days=365)
deleted = Customer.objects.exclude(orders__order_date__gte=cutoff).delete()
print(deleted[0])
")

# Log the number of deleted customers
echo "$TIMESTAMP - count: $DELETED_COUNT" >> /tmp/customer_cleanup_log.txt
