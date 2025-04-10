from django.db import models
from django.utils.timezone import datetime

class AuditableMixin(models.Model):
	created_at = models.DateTimeField(default=datetime.now())
	updated_at = models.DateTimeField(auto_now=True)
	# created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created_by', on_delete=models.CASCADE)
	# updated_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_updated_by', on_delete=models.CASCADE)
	class Meta:
		abstract = True