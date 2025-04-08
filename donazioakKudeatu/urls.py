from django.urls import path
from . import views

urlpatterns = [
    path('', views.formularioa_erakutsi, name='inicio'),  # Para mostrar el formulario
    path('donate/', views.donazioa_bidali_Redsysera, name='donazioa'),  # Para enviar los datos a Redsys
    path('response/', views.erantzuna_jaso_Redsysetik, name='erantzuna'),  # Para recibir datos de Redsys - Donación exitosa o error
]