# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse

def formularioa_erakutsi(request):
    # Solo muestra la página con el formulario
    return render(request, 'donazioaKudeatu/index.html')

def donazioa_bidali_Redsysera(request):
    # Envía la información necesaria a Redsys
    if request.method == 'POST':
        amount = request.POST.get('amount')

        


def erantzuna_jaso_Redsysetik(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            return JsonResponse({'mensaje': f'¡Hola, {nombre}!'})
    return JsonResponse({'error': 'No se recibió nombre'}, status=400)
