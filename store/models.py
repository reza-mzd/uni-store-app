from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    
class Comment(models.Model):
        date = models.DateTimeField(auto_now_add=True)
        body = models.TextField()
        product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='comments')
        reply_to = models.ForeignKey('self', on_delete=models.PROTECT, null=True)