# donazioakKudeatu/redsys_utils.py
import base64
import hmac
import hashlib
import json
import logging
from django.conf import settings

# Configuración del logger
logger = logging.getLogger(__name__)

def verify_signature(params_base64: str, received_signature: str) -> bool:
    """
    Verifica la firma HMAC-SHA256 de Redsys.
    
    Args:
        params_base64: Cadena Base64 con los parámetros
        received_signature: Firma recibida de Redsys
    
    Returns:
        bool: True si la firma es válida
    """
    try:
        # Decodifica la clave secreta (debe estar en Base64 en settings.py)
        key = base64.b64decode(settings.REDSYS_SECRET_KEY)
        
        # Calcula la firma esperada
        expected_signature = hmac.new(
            key,
            params_base64.encode() + key,  # ¡Clave concatenada dos veces!
            hashlib.sha256
        ).digest()
        
        # Compara con la firma recibida
        return base64.b64encode(expected_signature).decode() == received_signature
        
    except Exception as e:
        logger.error(f"Error al verificar firma: {str(e)}")
        return False

def decode_parameters(params_base64: str) -> dict:
    """
    Decodifica los parámetros de Redsys desde Base64.
    
    Args:
        params_base64: Cadena Base64 con los parámetros
    
    Returns:
        dict: Diccionario con los parámetros decodificados
    """
    try:
        params_json = base64.b64decode(params_base64).decode('utf-8')
        return json.loads(params_json)
    except Exception as e:
        logger.error(f"Error al decodificar parámetros: {str(e)}")
        raise ValueError("Parámetros Redsys inválidos")

def get_error_message(code: str) -> str:
    """
    Devuelve un mensaje legible para los códigos de error de Redsys.
    
    Args:
        code: Código de respuesta (ej: '0184')
    
    Returns:
        str: Mensaje descriptivo del error
    """
    error_codes = {
        '0000': 'Pago aceptado',
        '0101': 'Tarjeta caducada',
        '0102': 'Tarjeta en excepción temporal',
        '0106': 'Intentos de PIN excedidos',
        '0180': 'Tarjeta no válida',
        '0184': 'Autenticación requerida (3DSecure)',
        '0190': 'Rechazo genérico',
        '0191': 'Saldo insuficiente',
        '0195': 'Error en comunicación con el emisor',
        '0202': 'Tarjeta en lista negra',
        '0909': 'Error inesperado en TPV',
        '0913': 'Pedido repetido',
        '0944': 'Sesión inválida',
        '0950': 'Operación no permitida'
    }
    return error_codes.get(code, f'Error desconocido (código: {code})')