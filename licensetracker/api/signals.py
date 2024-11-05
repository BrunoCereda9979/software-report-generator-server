from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Software

# Invalidate cache after creating or updating a Software instance
@receiver(post_save, sender=Software)
def invalidate_software_cache_on_save(sender, instance, **kwargs):
    cache.delete("all_software")

# Invalidate cache after deleting a Software instance
@receiver(post_delete, sender=Software)
def invalidate_software_cache_on_delete(sender, instance, **kwargs):
    cache.delete("all_software")
