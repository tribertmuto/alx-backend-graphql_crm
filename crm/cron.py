import datetime
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from crm.models import Product

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive"
    
    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
        f.write(message + '\n')
    
    # Optionally query GraphQL hello
    try:
        transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("query { hello }")
        result = client.execute(query)
        print("GraphQL endpoint is responsive")
    except Exception as e:
        print(f"GraphQL query failed: {e}")

def update_low_stock():
    mutation = gql("""
    mutation {
      updateLowStockProducts {
        success
        message
        updatedProducts {
          name
          stock
        }
      }
    }
    """)
    
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql')
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    result = client.execute(mutation)
    updated = result['updateLowStockProducts']['updatedProducts']
    
    with open('/tmp/low_stock_updates_log.txt', 'a') as f:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for product in updated:
            f.write(f"{timestamp} - Product: {product['name']}, New Stock: {product['stock']}\n")
