# Integración Webpay - Instrucciones de Prueba

## 📋 Configuración Completada

### Archivos Modificados:
1. ✅ `settings.py` - Configuración de Webpay
2. ✅ `views.py` - Vistas de pago (iniciar_pago, confirmar_pago, resultado_pago)
3. ✅ `urls.py` - URLs de las vistas de pago
4. ✅ `carrito.html` - Botón "Pagar con Webpay"
5. ✅ `resultado_pago.html` - Template para resultado del pago
6. ✅ `error_pago.html` - Template para errores

## 🔧 Configuración en settings.py

```python
WEBPAY_COMMERCE_CODE = '597055555532'  # Código de comercio de integración
WEBPAY_API_KEY = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
WEBPAY_ENVIRONMENT = 'INTEGRACION'  # Cambiar a 'PRODUCCION' cuando vayas a producción
WEBPAY_RETURN_URL = 'http://127.0.0.1:8000/pago/confirmar/'
```

## 🧪 Tarjetas de Prueba (Ambiente de Integración)

### ✅ Transacción Aprobada
- **Tarjeta**: 4051 8842 3993 7763
- **CVV**: 123
- **Fecha vencimiento**: Cualquier fecha futura (ej: 12/25)
- **RUT**: 11.111.111-1
- **Clave**: 123

### ❌ Transacción Rechazada
- **Tarjeta**: 4051 8860 0005 6623
- **CVV**: 123
- **Fecha vencimiento**: Cualquier fecha futura
- **RUT**: 11.111.111-1
- **Clave**: 123

### 📝 Notas Importantes:
- Después de ingresar los datos, Webpay mostrará una pantalla de confirmación
- Ingresa la clave: **123**
- El sitio rojo de Transbank es normal en el ambiente de integración
- Lo importante es que después te redirija correctamente de vuelta a tu aplicación

## 🚀 Flujo de Pago

1. **Usuario agrega servicios al carrito**
2. **Usuario va a `/carrito/`**
3. **Usuario hace clic en "Pagar con Webpay"**
4. **Sistema crea una Venta y un Pago (estado PENDIENTE)**
5. **Sistema redirige a Webpay**
6. **Usuario ingresa datos de tarjeta en Webpay**
7. **Webpay redirige de vuelta a `/pago/confirmar/`**
8. **Sistema valida la transacción**
9. **Si es exitoso:**
   - Actualiza Venta a CONFIRMADA
   - Actualiza Pago a APROBADO
   - Actualiza Reservas a estado 'C' (Confirmada)
   - Vacía el carrito
   - Redirige a `/pago/resultado/exito/{venta_id}/`
10. **Si es rechazado:**
    - Actualiza Pago a RECHAZADO
    - Actualiza Venta a ANULADA
    - Redirige a `/pago/resultado/rechazado/`

## 📝 URLs Creadas

- `/pago/iniciar/` - Inicia el proceso de pago
- `/pago/confirmar/` - Callback de Webpay (POST)
- `/pago/resultado/exito/{venta_id}/` - Muestra resultado exitoso
- `/pago/resultado/rechazado/` - Muestra pago rechazado
- `/pago/resultado/error/` - Muestra error general

## 🧪 Cómo Probar

1. **Asegúrate de tener transbank-sdk instalado:**
   ```bash
   pip install transbank-sdk
   ```

2. **Ejecuta las migraciones (si agregaste campos nuevos):**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Inicia el servidor:**
   ```bash
   python manage.py runserver
   ```

4. **Prueba el flujo completo:**
   - Inicia sesión
   - Reserva un servicio (esto lo agrega al carrito)
   - Ve al carrito
   - Haz clic en "Pagar con Webpay"
   - Usa una de las tarjetas de prueba
   - Verifica que se actualice correctamente

## ⚠️ Importante

### Para Producción:
1. Cambia `WEBPAY_ENVIRONMENT` a `'PRODUCCION'`
2. Obtén tus credenciales reales de Transbank
3. Actualiza `WEBPAY_COMMERCE_CODE` y `WEBPAY_API_KEY`
4. Cambia `WEBPAY_RETURN_URL` a tu dominio real

### CSRF Token:
- La vista `confirmar_pago` usa `@csrf_exempt` porque Webpay hace un POST externo
- Esto es necesario para que funcione el callback

## 🔍 Debug

Si hay problemas, revisa:
1. **Consola del servidor** - Los errores se imprimen con `print(f"Error: {e}")`
2. **Base de datos** - Verifica el estado de las tablas Venta y Pagos
3. **Token** - Asegúrate de que el token_ws se guarde correctamente
4. **Ambiente** - Verifica que estés usando las credenciales correctas

## 📊 Estados

### Venta:
- PENDIENTE - Esperando pago
- CONFIRMADA - Pago exitoso
- ANULADA - Pago rechazado o error

### Pago:
- PENDIENTE - Esperando confirmación
- APROBADO - Transacción exitosa
- RECHAZADO - Transacción rechazada

### Reserva:
- P - Pendiente de Pago (en carrito)
- C - Confirmada (Pagada)
- X - Cancelada/Expirada
