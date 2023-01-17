from django.db.models import DecimalField
from django.db import models
import uuid

from accounts.models import CustomUser
from sensorthings.schema import Base, Thing
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class Site(models.Model):
    # This model should only contain the data related to how a Thing will be managed
    name = models.CharField(max_length=200)
    latitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    elevation = DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    # registration_date = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)


class ThingOwnership(Base):
    __tablename__ = 'thing_ownership'
    id = Column(Integer, primary_key=True)
    thing_id = Column(Integer, ForeignKey('thing.id'))
    person_id = Column(Integer, ForeignKey('custom_user.id'))
    thing = relationship(Thing, backref='thing_ownerships')
    person = relationship(CustomUser, backref='thing_ownerships')
