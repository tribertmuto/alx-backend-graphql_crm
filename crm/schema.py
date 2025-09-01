import graphene
from graphene_django import DjangoObjectType
from crm.models import Product, Order, Customer
from django.db.models import Q

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class Query(graphene.ObjectType):
    orders = graphene.List(OrderType, order_date_gte=graphene.String())
    hello = graphene.String()

    def resolve_orders(self, info, order_date_gte=None):
        if order_date_gte:
            return Order.objects.filter(order_date__gte=order_date_gte)
        return Order.objects.all()

    def resolve_hello(self, info):
        return "Hello from GraphQL!"

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in products:
            product.stock += 10
            product.save()
            updated.append(product)
        return UpdateLowStockProducts(
            success=True,
            message=f"Updated {len(updated)} products",
            updated_products=updated
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
