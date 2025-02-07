# from ninja import NinjaAPI
# from django.urls import path
# from django.views.decorators.csrf import ensure_csrf_cookie
# from core.views.thing import router as thing_router
# from core.views.sensor import router as sensor_router
# from core.views.observed_property import router as observed_property_router
# from core.views.processing_level import router as processing_level_router
# from core.views.unit import router as unit_router
# from core.views.photo import router as photo_router
# from core.views.tag import thing_tag_router as tag_router
# from core.views.tag import user_tag_router
# from core.views.archive import router as archive_router
# from core.views.datastream import router as datastream_router
# from core.views.result_qualifier import router as result_qualifier_router
# from core.views.data_loader import router as data_loader_router
# from core.views.data_source import router as data_source_router
#
# api = NinjaAPI(
#     title='HydroServer Data Management API',
#     version='0.10.0',
#     urls_namespace='data',
#     docs_decorator=ensure_csrf_cookie,
#     csrf=True
# )
#
# thing_router.add_router('/{thing_id}/photos', photo_router)
# thing_router.add_router('/{thing_id}/tags', tag_router)
# thing_router.add_router('/{thing_id}/archive', archive_router)
# api.add_router('/things', thing_router)
# api.add_router('/tags', user_tag_router)
# api.add_router('/datastreams', datastream_router)
# api.add_router('/observed-properties', observed_property_router)
# api.add_router('/processing-levels', processing_level_router)
# api.add_router('/sensors', sensor_router)
# api.add_router('/units', unit_router)
# api.add_router('/result-qualifiers', result_qualifier_router)
# api.add_router('/data-loaders', data_loader_router)
# api.add_router('/data-sources', data_source_router)
#
# urlpatterns = [
#     path('', api.urls),
# ]
