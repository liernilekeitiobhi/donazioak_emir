from django.urls import path
from . import views

urlpatterns = [
    path('', views.formularioa_erakutsi, name='inicio'),  # Para mostrar el formulario
    path('donate/', views.donazioa_bidali_Redsysera, name='donazioa'),  # Para enviar los datos a Redsys
    path('notification/', views.erantzuna_jaso_Redsysetik, name='erantzuna'),  # Para recibir datos de Redsys - Verificar firma y añadir a la BD
    path('ordainketa-zuzena/', views.ordainketa_zuzena, name='payment-success'),
    path('errorea-ordainketan/', views.ordainketa_okerra, name='payment-failure'),
]