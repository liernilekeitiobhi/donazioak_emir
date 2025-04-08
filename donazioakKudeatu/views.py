# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
from models import Donation

def formularioa_erakutsi(request):
    # Solo muestra la página con el formulario
    return render(request, 'donazioakKudeatu/index.html')


def donazioa_bidali_Redsysera(request):
    # Envía la información necesaria a Redsys
    if request.method == 'POST':
        amount = request.POST.get('amount')
        
        # 1. Genera un ID de orden único (ejemplo simple)
        transaction_id = 'coger de la base de datos' # tiene que ir sumando +1
        
        # 2. URL donde RedSys notificará el resultado (crea esta vista después)
        # merchant_url = request.build_absolute_uri('/redsys-notification/')
        
        # 3. Obtener parámetros
        redsys_params = {
            # take them from settings
            # take amount from the request
        }
        
        # 4. Renderizar formulario oculto que redirige a RedSys
        return render(request, 'donations/redirect_to_redsys.html', {
            'redsys_url': 'https://sis-t.redsys.es:25443/sis/realizarPago',
            'params': redsys_params
        })




def erantzuna_jaso_Redsysetik(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            return JsonResponse({'mensaje': f'¡Hola, {nombre}!'})
    return JsonResponse({'error': 'No se recibió nombre'}, status=400)
