from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'count', 'is_deleted', 'get_comments_count')
    # readonly_fields = ['price']
    def get_comments_count(self, obj: Product):
        return obj.comments.all().count()
    get_comments_count.short_description = 'Comments'
    class Meta:
        model = Product


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'product', 'is_approved')
    

admin.site.register(Comment, CommentAdmin) 
admin.site.register(Product, ProductAdmin)  