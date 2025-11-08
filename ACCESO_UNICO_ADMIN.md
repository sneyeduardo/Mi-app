# Sistema de Acceso Único de Administrador

## Descripción
El sistema de acceso único permite a los administradores obtener acceso temporal al sistema sin necesidad de credenciales normales.

## Componentes Implementados

### 1. Modelo de Base de Datos (`models.py`)
- **TokenAcceso**: Tabla para almacenar tokens de acceso únicos
- Funciones para generar, validar y gestionar tokens

### 2. Rutas de API (`app.py`)
- `GET /admin/token/generar` - Genera un nuevo token (solo admins)
- `GET /admin/acceso-unico/<token>` - Usa un token para acceso directo
- `GET /admin/tokens` - Lista tokens generados
- `POST /admin/token/<id>/invalidar` - Invalida un token

### 3. Generador Manual (`admin_token_generator.py`)
Script independiente para crear tokens de acceso único.

## Uso

### Método 1: Script Generador (Recomendado)
```bash
python admin_token_generator.py
```
Este script:
- Verifica/crea usuario administrador
- Genera token con expiración de 1 hora
- Muestra URL directa de acceso
- Muestra instrucciones de uso

### Método 2: API REST
1. Inicia sesión como administrador
2. Haz GET a `/admin/token/generar`
3. Usa el token devuelto para acceder a `/admin/acceso-unico/<token>`

## Características de Seguridad

1. **Tokens de un solo uso**: Se invalidan automáticamente al usarlos
2. **Expiración automática**: Los tokens expiran según configuración
3. **Validación de IP**: Registra IP de origen del token
4. **Auditoría completa**: Registra todas las acciones en historial
5. **Solo administradores**: Solo usuarios tipo ADMIN pueden generar tokens

## Ejemplo de Respuesta JSON

```json
{
  "success": true,
  "token": "aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0uV1",
  "url": "http://localhost:5000/admin/acceso-unico/aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0uV1",
  "expires_in_minutes": 30,
  "message": "Token generado exitosamente. Expira en 30 minutos."
}
```

## Notas Técnicas

- Los tokens tienen 32 caracteres aleatorios
- Expiración configurable (5-1440 minutos)
- Almacenamiento seguro en base de datos
- Validación de integridad antes de cada uso
- Registro completo de auditoría

## Solución de Problemas

### "Token no encontrado"
- Verifica que el token sea correcto
- El token puede haber expirado

### "Token ya utilizado"
- Los tokens son de un solo uso
- Genera un nuevo token

### "Token expirado"
- Genera un nuevo token
- Verifica la hora del sistema

### "No tienes permisos"
- Solo usuarios ADMIN pueden generar tokens
- Verifica tu tipo de usuario en la base de datos