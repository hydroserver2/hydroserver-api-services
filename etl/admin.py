from django.contrib import admin
from etl.models import (
    OrchestrationSystem,
    DataConnector,
    LinkedDatastream,
)


admin.site.register(OrchestrationSystem)
admin.site.register(DataConnector)
admin.site.register(LinkedDatastream)
