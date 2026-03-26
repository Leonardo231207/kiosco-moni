def calcular_digito_control_ean13(codigo_sin_digito):
    suma = 0
    for i, digito in enumerate(codigo_sin_digito):
        if i % 2 == 0:
            suma += int(digito) * 1
        else:
            suma += int(digito) * 3
    resto = suma % 10
    return 0 if resto == 0 else 10 - resto


def generar_codigo_interno():
    from models import Producto
    import random
    import time
    
    prefijo = '2'
    max_intentos = 100
    
    for _ in range(max_intentos):
        base = prefijo + str(int(time.time() * 1000))[-5:] + str(random.randint(0, 99999)).zfill(5)
        base = base[:12]
        digito = calcular_digito_control_ean13(base)
        codigo = base + str(digito)
        
        if not Producto.query.filter_by(codigo_barras=codigo).first():
            return codigo
    
    raise Exception("No se pudo generar un código único después de 100 intentos")


def validar_ean13(codigo):
    if len(codigo) != 13:
        return False
    if not codigo.isdigit():
        return False
    
    digito_correcto = calcular_digito_control_ean13(codigo[:-1])
    return int(codigo[-1]) == digito_correcto
