from django.db import models


class DataStoreDialect(models.Model):
    """
    Model for defining supported data store dialects.

    This model should include all supported data store dialects used by HydroServer. A dialect can represent a
    relational database, such as SQLite or PostgreSQL. It can also represent specific database setups using different
    types of extensions such as TimescaleDB, PostGIS, SpatiaLite, or a combination. Non-relational data stores such as
    InfluxDB or MongoDB could also be added.
    """

    name = models.CharField(max_length=255, unique=True)
    url_pattern = models.CharField(max_length=255)


class DataStoreInformationModel(models.Model):
    """
    Model for defining supported data store information model.

    This model should include all information models or subsets of information models used by HydroServer. An
    information model should be technology independent and detail how observations data should be organized. ODM2 is an
    example of an information model.
    """

    name = models.CharField(max_length=255, unique=True)


class DataStoreSchema(models.Model):
    """
    Model for defining supported data store information schemas, e.g. "ODM2"

    This model should include all supported data store schemas used by HydroServer. A data store schema should apply an
    information model such as ODM2 or some subset of it to a data store dialect. Data store schemas inform the
    HydroServer data management and data services layers how to interface with a specific data store instance.
    """

    name = models.CharField(max_length=255, unique=True)
    data_store_information_model = models.ForeignKey(DataStoreInformationModel, on_delete=models.PROTECT)
    data_store_dialect = models.ForeignKey(DataStoreDialect, on_delete=models.PROTECT)


class DataStore(models.Model):
    """
    Model for defining data stores connected to the HydroServer.

    This model should include all data stores this HydroServer instance can connect to. When using the data services or
    data management layers, a data store must be chosen to connect to.
    """

    # TODO: Each of these fields should be validated against the chosen schema dialect.
    # TODO: The password field should be encrypted or secured in some way.
    # TODO: This model should be linked to the Django User models. We'll need to build out some custom access rules.
    name = models.CharField(max_length=255, unique=True)
    data_store_schema = models.ForeignKey(DataStoreSchema, on_delete=models.PROTECT)
    host = models.CharField(max_length=255, null=True)
    port = models.IntegerField(null=True)
    db_name = models.CharField(max_length=255, null=True)
    path = models.CharField(max_length=255, null=True)
    username = models.IntegerField(null=True)
    password = models.IntegerField(null=True)

    def get_engine(self):
        """
        Generates a SQLAlchemy engine object.

        :return: SQLAlchemy engine object
        """

        return None


class Observation(models.Model):
    """
    Model for defining available observations in a data store.

    This model should include all observations from each data store that are accessible to HydroServer. Individual
    observations can be published or not published to the data services layer, editable by certain users, and assigned
    data archive schedules.
    """

    name = models.CharField(max_length=255, unique=True)
    data_store = models.ForeignKey(DataStore, on_delete=models.PROTECT)
