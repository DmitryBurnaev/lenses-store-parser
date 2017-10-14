from main.models import Product


def base_info(request):
    return {'product_types': dict(Product.TYPE_CHOICES)}
