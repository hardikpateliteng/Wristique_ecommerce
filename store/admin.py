from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview, Cart, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_featured', 'is_new_arrival', 'is_best_seller']
    list_filter = ['category', 'gender', 'is_featured', 'is_new_arrival', 'is_best_seller', 'is_active']
    list_editable = ['price', 'discount_price', 'stock', 'is_featured', 'is_new_arrival', 'is_best_seller']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'sku']
    inlines = [ProductImageInline]


@admin.register(ProductReview)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved']
    list_filter = ['rating', 'is_approved']
    list_editable = ['is_approved']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'get_total']
    list_filter = ['created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'created_at']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'user', 'subtotal', 'tax', 'shipping_cost', 'total']