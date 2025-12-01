from django.db import models
import uuid
import os
from datetime import datetime

def _get_product_file_upload_path(instance, filename):
    prefix = datetime.now().strftime('product_images/%Y%m')
    ext = os.path.splitext(filename)[1]
    new_name = f"{uuid.uuid4()!s}{ext}"
    path = os.path.join(prefix, new_name)
    return path

class Product(models.Model):
    class ProductType(models.TextChoices):
        NEW = 'new'
        USED = 'used'
        REFURBISHED = 'refurbished'
        REPAIRED = 'repaired'

        
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    picture = models.ImageField(upload_to=_get_product_file_upload_path, null=True, blank=True)
    #comments
    # New , Used , Refurbished and Repaired
    type_of_product = models.CharField(max_length=100, choices=ProductType.choices)
    
    
    def calculate_discounted_prices(self):
        res = int(self.price - (self.price * self.discount / 100))
        if res < 0:
            raise ValueError("Bad discount value")
        else:
            return res
    
    def __str__(self):
        return self.name
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['price', 'discount']),
        ]

# from django.contrib.auth.models import User   # explain : Instead of using the User class directly, use the following two lines
from django.contrib.auth import get_user_model
User = get_user_model()
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comments')
    date = models.DateTimeField(auto_now_add=True) 
    body = models.TextField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='comments')
    reply_to = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.date.strftime("%Y-%m-%d")}'


class Invoice(models.Model):
    
    class STATE(models.TextChoices):
        STATE_PENDING = 'pending', "Pending"
        STATE_COMPLETED = "completed", "Completed"
        STATE_CANCELED = "canceled", "Canceled"
        
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    total = models.PositiveIntegerField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    number = models.CharField(max_length=20, default=None, null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATE.choices, default=STATE.STATE_PENDING)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    total = models.PositiveBigIntegerField()
    
    def save(self, *args, **kwargs):
        self.total = (self.price - self.discount*self.price/100) * self.count
        super().save(*args, **kwargs)


class Payment(models.Model):
    
    class STATE(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ERROR = 'error', 'ERROR'
        COMPLETE = 'complete', 'Completed'

    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    description = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    authority = models.CharField(max_length=50)
    refid = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATE.choices, default=STATE.PENDING)
        