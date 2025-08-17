import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
import re


class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter


class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


def validate_phone(phone):
    if phone:
        pattern = r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$'
        if not re.match(pattern, phone):
            raise ValidationError("Phone number must be in format '+1234567890' or '123-456-7890'")


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        try:
            validate_phone(input.phone)
            
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(
                    customer=None,
                    message="Email already exists",
                    success=False
                )
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True
            )
        except ValidationError as e:
            return CreateCustomer(
                customer=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message=f"Error creating customer: {str(e)}",
                success=False
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        customers = []
        errors = []
        
        for i, customer_data in enumerate(input):
            try:
                validate_phone(customer_data.phone)
                
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(f"Customer {i+1}: Email already exists")
                    continue
                
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
                
            except ValidationError as e:
                errors.append(f"Customer {i+1}: {str(e)}")
            except Exception as e:
                errors.append(f"Customer {i+1}: Error creating customer - {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        try:
            if input.price <= 0:
                return CreateProduct(
                    product=None,
                    message="Price must be positive",
                    success=False
                )
            
            if input.stock is not None and input.stock < 0:
                return CreateProduct(
                    product=None,
                    message="Stock cannot be negative",
                    success=False
                )
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            
            return CreateProduct(
                product=product,
                message="Product created successfully",
                success=True
            )
        except ValidationError as e:
            return CreateProduct(
                product=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateProduct(
                product=None,
                message=f"Error creating product: {str(e)}",
                success=False
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(
                order=None,
                message="Customer not found",
                success=False
            )
        
        if not input.product_ids:
            return CreateOrder(
                order=None,
                message="At least one product must be selected",
                success=False
            )
        
        try:
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                return CreateOrder(
                    order=None,
                    message="One or more products not found",
                    success=False
                )
            
            with transaction.atomic():
                order = Order(customer=customer)
                if input.order_date:
                    order.order_date = input.order_date
                order.save()
                
                order.products.set(products)
                total = sum(product.price for product in products)
                order.total_amount = total
                order.save()
            
            return CreateOrder(
                order=order,
                message="Order created successfully",
                success=True
            )
        except Exception as e:
            return CreateOrder(
                order=None,
                message=f"Error creating order: {str(e)}",
                success=False
            )


class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
    
    customers_list = graphene.List(CustomerType)
    products_list = graphene.List(ProductType)
    orders_list = graphene.List(OrderType)
    
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_customers_list(self, info):
        return Customer.objects.all()
    
    def resolve_products_list(self, info):
        return Product.objects.all()
    
    def resolve_orders_list(self, info):
        return Order.objects.all()
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        try:
            validate_phone(input.phone)
            
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(
                    customer=None,
                    message="Email already exists",
                    success=False
                )
            
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True
            )
        except ValidationError as e:
            return CreateCustomer(
                customer=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message=f"Error creating customer: {str(e)}",
                success=False
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        customers = []
        errors = []
        
        for i, customer_data in enumerate(input):
            try:
                validate_phone(customer_data.phone)
                
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(f"Customer {i+1}: Email already exists")
                    continue
                
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
                
            except ValidationError as e:
                errors.append(f"Customer {i+1}: {str(e)}")
            except Exception as e:
                errors.append(f"Customer {i+1}: Error creating customer - {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        try:
            if input.price <= 0:
                return CreateProduct(
                    product=None,
                    message="Price must be positive",
                    success=False
                )
            
            if input.stock is not None and input.stock < 0:
                return CreateProduct(
                    product=None,
                    message="Stock cannot be negative",
                    success=False
                )
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            
            return CreateProduct(
                product=product,
                message="Product created successfully",
                success=True
            )
        except ValidationError as e:
            return CreateProduct(
                product=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateProduct(
                product=None,
                message=f"Error creating product: {str(e)}",
                success=False
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    
    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(
                order=None,
                message="Customer not found",
                success=False
            )
        
        if not input.product_ids:
            return CreateOrder(
                order=None,
                message="At least one product must be selected",
                success=False
            )
        
        try:
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                return CreateOrder(
                    order=None,
                    message="One or more products not found",
                    success=False
                )
            
            with transaction.atomic():
                order = Order(customer=customer)
                if input.order_date:
                    order.order_date = input.order_date
                order.save()
                
                order.products.set(products)
                total = sum(product.price for product in products)
                order.total_amount = total
                order.save()
            
            return CreateOrder(
                order=order,
                message="Order created successfully",
                success=True
            )
        except Exception as e:
            return CreateOrder(
                order=None,
                message=f"Error creating order: {str(e)}",
                success=False
            )
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()