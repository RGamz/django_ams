from django.db import models
from django.db.models import TextField
from django.db.models.functions import Greatest


class TicketManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_removed=0)

    def with_last_action_dates(self):
        from api.models import Log, Discussion, EXCLUDED_LOG_TYPES

        last_log = Log.objects.filter(id_ticket=models.OuterRef('id')).exclude(log_type__in=EXCLUDED_LOG_TYPES).order_by('-ts')
        last_message = Discussion.objects.filter(id_discussion=models.OuterRef('id_discussion')).filter(~models.Q(id_entite=0)).order_by('-ts_creation')

        first_message_content = Discussion.objects.filter(id_discussion=models.OuterRef('id_discussion')).filter(~models.Q(id_entite=0)).order_by('ts_creation')
        last_invisible_message = Discussion.objects.filter(id_discussion=models.OuterRef('id_discussion')).filter(~models.Q(id_entite=0)).filter(models.Q(for_particulier=0), models.Q(for_station=0), models.Q(for_distributeur=0)).order_by('-ts_creation')

        return self.get_queryset() \
            .annotate(last_log_timestamp=models.functions.Coalesce(models.Subquery(last_log.values('ts')[:1]), 0))   \
            .annotate(last_message_timestamp=models.functions.Coalesce(models.Subquery(last_message.values('ts_creation')[:1]), 0)) \
            .annotate(first_message_text=models.functions.Coalesce(models.Subquery(first_message_content.values('message')[:1]), models.Value(''), output_field=TextField())) \
            .annotate(last_invisible_message_text=models.functions.Coalesce(models.Subquery(last_invisible_message.values('message')[:1]), models.Value(''), output_field=TextField())) \
            .annotate(last_action_date=Greatest('last_log_timestamp', 'last_message_timestamp'))
