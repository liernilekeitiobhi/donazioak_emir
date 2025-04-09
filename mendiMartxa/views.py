# Create your views here.
'''
sequenceDiagram
    participant Usuario
    participant TuServidor
    participant Redsys

    Usuario->>TuServidor: 1. Inicia pago (POST /donate/)
    TuServidor->>Redsys: 2. Redirección con formulario
    Redsys->>Usuario: 3. Interfaz de pago
    Usuario->>Redsys: 4. Completa pago
    Redsys->>TuServidor: 5. Notificación POST (actualiza BD)
    TuServidor->>Redsys: 6. Responde "OK"
    Redsys->>Usuario: 7. Redirección GET (/success/ o /error/)

'''

from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import base64
import hashlib
import hmac
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .redsys_utils import verify_signature, decode_parameters, get_error_message
import logging
from models import *
import uuid
from django.utils import timezone


logger = logging.getLogger(__name__)


#============================================
# Solo muestra la página con el formulario
#============================================
def formularioa_erakutsi(request):
    # Obtén la campaña activa (puedes ajustar esto según tu lógica)
    
    context = {
        Donation.get_progress_percentage(),
    }
    return render(request, 'mendiMartxa/mendi-martxa.html', context)



#============================================
# Envía la información necesaria a Redsys
#============================================
def donazioa_bidali_Redsysera(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        campaign = request.POST.get('campaign')
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            amount = 0

        if amount <= 0:
            return render(request, 'mendiMartxa/mendi-martxa.html', {
                'progress_percentage': Donation.get_progress_percentage(),
                'error_message': "Por favor, introduce una cantidad válida mayor a 0."
            })
        
        order_id = f"DON-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        # Nuestros parámetros
        redsys_params = {
            'Ds_Merchant_Amount': str(int(float(amount) * 100)),  # In cents
            'Ds_Merchant_Currency': settings.REDSYS_CURRENCY,
            'Ds_Merchant_MerchantCode': settings.REDSYS_MERCHANT_CODE,
            'Ds_Merchant_Terminal': settings.REDSYS_TERMINAL,
            'Ds_Merchant_TransactionType': settings.REDSYS_TRANSACTION_TYPE,
            'Ds_Merchant_Order': order_id,
            'Ds_Merchant_MerchantURL': settings.REDSYS_MERCHANT_URL,
            'Ds_Merchant_UrlOK': request.build_absolute_uri('/ordainketa-zuzena/'),
            'Ds_Merchant_UrlKO': request.build_absolute_uri('/errorea-ordainketan/')
        }
        
        # Codificar parámetros
        params_json = json.dumps(redsys_params)
        params_base64 = base64.b64encode(params_json.encode()).decode()
        
        # Calcular firma HMAC-SHA256
        key = base64.b64decode(settings.REDSYS_SECRET_KEY)
        message = params_base64.encode() + key
        signature = hmac.new(key, message, hashlib.sha256).digest()
        signature_base64 = base64.b64encode(signature).decode()

        # Crear donación en bd
        Donation.objects.create(
            transaction_id = order_id,
            amount = amount,
            status = 'pending',
            campaign = campaign
        )
        
        # Enviar los parámetros a la URL de Redsys redireccionado por un HTML con formulario oculto
        return render(request, 'mendiMartxa/redirect_to_redsys.html', {
            'redsys_url': settings.REDSYS_URL_TEST if settings.DEBUG else settings.REDSYS_URL,
            'Ds_MerchantParameters': params_base64,
            'Ds_SignatureVersion': 'HMAC_SHA256_V1',
            'Ds_Signature': signature_base64
        })

    return HttpResponse('Invalid request', status=400)


#==========================================================================
# Recibe la respuesta de Redsys después de la donación (en segundo plano)
#==========================================================================

# Ejemplo de lo que nos envia:
'''
{
    'Ds_Date': '01/01/2025',
    'Ds_Hour': '12:30',
    'Ds_Amount': '2000',  # En céntimos (ej: 20.00€)
    'Ds_Currency': '978',
    'Ds_Order': 'DON-202501011230',
    'Ds_Response': '0000',  # Código de estado
    'Ds_TransactionType': '0',
    'Ds_SecurePayment': '1',
    'Ds_MerchantParameters': 'eyJ...',  # Versión en Base64
    'Ds_Signature': 'ABC123...'  # Firma
}
'''


@csrf_exempt  # ¡Importante! Redsys no envía CSRF token

def erantzuna_jaso_Redsysetik(request):
    """
    Maneja las notificaciones POST de Redsys.
    """
    if request.method == 'POST':
        try:
            # 1. Obtener parámetros
            params_base64 = request.POST.get('Ds_MerchantParameters')
            signature = request.POST.get('Ds_Signature')
            
            if not params_base64 or not signature:
                return HttpResponse('Parámetros faltantes', status=400)

            # 2. Verificar firma
            if not verify_signature(params_base64, signature):
                logger.warning("Firma inválida recibida")
                return HttpResponse('Firma inválida', status=400)

            # 3. Decodificar parámetros
            params = decode_parameters(params_base64)
            
            # 4. Registrar/actualizar donación
            Donation.objects.update_or_create(
                transaction_id=params['Ds_Order'],
                defaults={
                    'amount': float(params['Ds_Amount'])/100,
                    'status': 'completed' if params['Ds_Response'] == '0000' else 'failed',
                    'response_code': params['Ds_Response'],
                    'error_message': get_error_message(params['Ds_Response']),
                    'merchant_parameters': params_base64,
                    'raw_response': params
                }
            )
            
            logger.info(f"Donación {params['Ds_Order']} procesada. Estado: {params['Ds_Response']}")
            return HttpResponse('OK')  # ¡Respuesta exacta requerida!
            
        except Exception as e:
            logger.error(f"Error procesando notificación: {str(e)}")
            return HttpResponse(f"Error: {str(e)}", status=500)
    return HttpResponse('Método no permitido', status=405)


# ==========================================================
# Si el pago ha sido exitoso mostraremos una pantalla verde
# ==========================================================

def ordainketa_zuzena(request):
    """Muestra pantalla de éxito con verificación de estado"""
    order_id = request.GET.get('Ds_Order')
    try:
        donation = Donation.objects.get(transaction_id=order_id)
        if donation.status != 'completed':
            logger.warning(f"Acceso a éxito pero estado es {donation.status}")
            return redirect('ordainketa_okerra')
            
        return render(request, 'mendiMartxa/ordainketa-zuzena.html', {
            'donation': donation,
        })
    except Donation.DoesNotExist:
        logger.error(f"Donación no encontrada para order_id: {order_id}")
        return redirect('formularioa_erakutsi')


# ==========================================================
# Si el pago ha sido erroneo mostraremos una pantalla roja
# ==========================================================

def ordainketa_okerra(request):
    """Muestra pantalla de error con detalles"""
    error_code = request.GET.get('Ds_Response')
    order_id = request.GET.get('Ds_Order')
    context = {
        'error_code': error_code,
        'error_message': get_error_message(error_code) if error_code else 'Errore ezezaguna'
    }
    
    if order_id:
        try:
            donation = Donation.objects.get(transaction_id=order_id)
            context['donation'] = donation
        except Donation.DoesNotExist:
            logger.warning(f"Orden no encontrada en error: {order_id}")
    
    return render(request, 'mendiMartxa/errorea-ordainketan.html', context)

# =======================================================
# Para la barra de progreso
# =======================================================

def get_progress_data(request):
    return JsonResponse({
        'total_raised': float(Donation.get_total_raised()),
        'progress_percentage': Donation.get_progress_percentage(),
        'campaign_goal': settings.CAMPAIGN_GOAL
    })
    