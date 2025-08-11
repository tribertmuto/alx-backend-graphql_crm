import os
import django
from graphene.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from alx_backend_graphql_crm.schema import schema

def test_graphql():
    client = Client(schema)
    
    print("Testing GraphQL Queries and Mutations")
    print("=" * 50)
    
    # Test hello query
    print("\n1. Testing hello query:")
    hello_query = '''
        query {
            hello
        }
    '''
    result = client.execute(hello_query)
    print(f"Result: {result}")
    
    # Test customers list
    print("\n2. Testing customers list:")
    customers_query = '''
        query {
            customersList {
                id
                name
                email
                phone
            }
        }
    '''
    result = client.execute(customers_query)
    print(f"Result: {result}")
    
    # Test products list
    print("\n3. Testing products list:")
    products_query = '''
        query {
            productsList {
                id
                name
                price
                stock
            }
        }
    '''
    result = client.execute(products_query)
    print(f"Result: {result}")
    
    # Test orders list
    print("\n4. Testing orders list:")
    orders_query = '''
        query {
            ordersList {
                id
                customer {
                    name
                }
                totalAmount
            }
        }
    '''
    result = client.execute(orders_query)
    print(f"Result: {result}")
    
    # Test create customer mutation
    print("\n5. Testing create customer mutation:")
    create_customer_mutation = '''
        mutation {
            createCustomer(input: {
                name: "Test User",
                email: "test@example.com",
                phone: "+1111111111"
            }) {
                customer {
                    id
                    name
                    email
                }
                message
                success
            }
        }
    '''
    result = client.execute(create_customer_mutation)
    print(f"Result: {result}")
    
    # Test create product mutation
    print("\n6. Testing create product mutation:")
    create_product_mutation = '''
        mutation {
            createProduct(input: {
                name: "Test Product",
                price: "99.99",
                stock: 5
            }) {
                product {
                    id
                    name
                    price
                    stock
                }
                message
                success
            }
        }
    '''
    result = client.execute(create_product_mutation)
    print(f"Result: {result}")
    
    print("\n" + "=" * 50)
    print("GraphQL tests completed!")

if __name__ == "__main__":
    test_graphql()