from rest_framework.routers import DefaultRouter
from . import views

app_name = "areas"

urlpatterns = [

]

router = DefaultRouter()
router.register("areas", views.AreaViewSet, base_name="areas")
urlpatterns += router.urls

