import uuid, hashlib
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Software(models.Model):
    
    SOFTWARE_HOSTING_CHOICES = [
        ('INT', 'Internally'),
        ('EXT', 'Externally'),
    ]
    YES_NO_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No'),
    ]
    OPERATIONAL_STATUS_CHOICES = [
        ('A', 'Active'),
        ('I', 'Inactive'),
    ]

    def json_field_default():
        return {"": ""}
    
    id = models.AutoField(primary_key=True)
    software_name = models.CharField(max_length=255)
    software_description = models.TextField()
    software_department = models.ManyToManyField('Department', related_name='software_deparments')
    software_version = models.CharField(max_length=50, blank=True, default="1.0.0")
    software_years_of_use = models.PositiveIntegerField(null=True, default=1)
    software_last_updated = models.DateField(null=True, blank=True)
    software_expiration_date = models.DateField(null=True, blank=True)
    software_operational_status = models.CharField(max_length=1, choices=OPERATIONAL_STATUS_CHOICES, default='A')
    software_is_hosted = models.CharField(max_length=3, choices=SOFTWARE_HOSTING_CHOICES, default="INT")
    software_is_tech_supported = models.CharField(max_length=3, choices=YES_NO_CHOICES, default="NO")
    software_is_cloud_based = models.CharField(max_length=3, choices=YES_NO_CHOICES, null=True, default="NO")
    software_maintenance_support = models.CharField(max_length=3, choices=YES_NO_CHOICES, default="NO")
    software_vendor = models.ManyToManyField('Vendor', related_name='software_vendors')
    software_department_contact_people = models.ManyToManyField('ContactPerson', related_name='software_contact_people', blank=True)
    software_divisions_using = models.ManyToManyField('Division', related_name="software_divisions", blank=True)
    software_number_of_licenses = models.PositiveIntegerField(blank=True)
    software_to_operate = models.ManyToManyField('SoftwareToOperate', related_name='software_to_operate', blank=True)
    hardware_to_operate = models.ManyToManyField('HardwareToOperate', related_name='hardware_to_operate', blank=True)
    software_annual_amount = models.FloatField(null=True, blank=True, max_length=10)
    software_gl_accounts = models.ManyToManyField('GlAccount', related_name="software_gl_accounts", blank=True)

    def __str__(self):
        return self.software_name

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    software = models.ForeignKey(Software, on_delete=models.CASCADE, related_name='comment_software')
    content = models.TextField()
    satisfaction_rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.software.software_name}'

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name

class Vendor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
   
    def __str__(self):
        return self.name

class ContactPerson(models.Model):
    id = models.AutoField(primary_key=True)
    contact_name = models.CharField(max_length=100)
    contact_lastname = models.CharField(max_length=100)
    contact_email = models.EmailField(null=True)
    contact_phone_number = models.PositiveBigIntegerField(null=True, blank=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=False, null=True)

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = self.generate_uuid()
        super().save(*args, **kwargs)

    def generate_uuid(self):
        # Combine fields to create a unique string
        combined = f"{self.contact_name} {self.contact_lastname} {self.contact_phone_number} {self.contact_email}"
        # Generate a SHA-1 hash of the combined string
        hash_object = hashlib.sha1(combined.encode())
        hash_hex = hash_object.hexdigest()
        # Create a UUID from the first 32 bits of the hash
        return uuid.UUID(hash_hex[:32])

    def __str__(self):
        return f"{self.contact_name} {self.contact_lastname} {self.contact_email}"

class Division(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    code = models.IntegerField(blank=True, null=True, unique=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name

class GlAccount(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class SoftwareToOperate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class HardwareToOperate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class BlacklistedToken(models.Model):
    token = models.CharField(max_length=500, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def is_blacklisted(cls, token):
        """Check if a token is blacklisted"""
        # Optionally, clean up old blacklisted tokens
        cls.objects.filter(blacklisted_at__lt=timezone.now() - timedelta(days=1)).delete()
        return cls.objects.filter(token=token).exists()
    
    class Meta:
        app_label = 'api'
        indexes = [
            models.Index(fields=['token']),
        ]
        