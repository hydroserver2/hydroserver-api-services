from django.db import models
from solo.models import SingletonModel


MAP_LAYER_TYPE_CHOICES = (
    ("basemap", "Basemap"),
    ("overlay", "Overlay"),
)

ELEVATION_SERVICE_CHOICES = (
    ("openElevation", "Open Elevation"),
    ("google", "Google"),
)

GEO_SERVICE_CHOICES = (
    ("nominatim", "Nominatim"),
    ("google", "Google"),
)


class InstanceConfiguration(SingletonModel):
    show_about_information = models.BooleanField(default=False)
    about_page_title = models.CharField(max_length=255, blank=True, null=True)
    about_page_text = models.TextField(blank=True, null=True)
    default_latitude = models.DecimalField(
        max_digits=22, decimal_places=16, default=39
    )
    default_longitude = models.DecimalField(
        max_digits=22, decimal_places=16, default=-100
    )
    default_zoom_level = models.IntegerField(default=4)
    default_base_layer = models.ForeignKey(
        "MapLayer",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="default_base_layer",
    )
    default_satellite_layer = models.ForeignKey(
        "MapLayer",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="default_satellite_layer",
    )
    elevation_service = models.CharField(max_length=255, choices=ELEVATION_SERVICE_CHOICES, default="openElevation")
    geo_service = models.CharField(max_length=255, choices=GEO_SERVICE_CHOICES, default="nominatim")
    terms_of_use_link = models.CharField(max_length=255, blank=True, null=True)
    privacy_policy_link = models.CharField(max_length=255, blank=True, null=True)
    copyright = models.CharField(max_length=255, blank=True, null=True)
    enable_clarity_analytics = models.BooleanField(default=False)
    clarity_project_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Instance Configuration"

    class Meta:
        verbose_name = "Instance Configuration"
        verbose_name_plural = "Instance Configuration"


class ContactInformation(models.Model):
    title = models.CharField(max_length=255, unique=True)
    text = models.TextField(blank=True, null=True)
    action = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"


class MapLayer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255, choices=MAP_LAYER_TYPE_CHOICES)
    priority = models.IntegerField(default=0)
    source = models.CharField(max_length=255)
    attribution = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Map Layer"
