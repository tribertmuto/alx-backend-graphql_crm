#!/usr/bin/env python3

import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# Calculate date 7 days ago
seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')

# GraphQL query
query = gql("""
query GetRecentOrders($date: String!) {
  orders(orderDateGte: $date) {
    id
    customer {
      email
    }
  }
}
""")

# Transport
transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')

# Client
client = Client(transport=transport, fetch_schema_from_transport=True)

# Execute query
result = client.execute(query, variable_values={'date': seven_days_ago})

# Log to file
with open('/tmp/order_reminders_log.txt', 'a') as f:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for order in result['orders']:
        f.write(f"{timestamp} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n")

print("Order reminders processed!")
