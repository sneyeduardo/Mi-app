#!/usr/bin/env python3
"""
Script de inicio para el Sistema de Préstamos IUNP
Este script verifica las dependencias e inicia el servidor
"""

import sys
import subprocess
import os

def verificar_python():
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    print("\n📦 Instalando dependencias...")
    
    dependencias = [
        'flask',
        'flask-sqlalchemy', 
        'flask-login',
        'werkzeug'
    ]
    
    for dep in dependencias:
        try:
            print(f"   Instalando {dep}...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', dep, '--user'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ⚠️  Error instalando {dep} (continuando...)")
    
    return True

def verificar_archivos():
    """Verifica que todos los archivos necesarios estén presentes"""
    print("\n📁 Verificando archivos...")
    
    archivos_requeridos = [
        'app.py',
        'models.py',
        'forms.py',
        'templates/base.html',
        'templates/solicitar.html'
    ]
    
    archivos_admin = [
        'templates/admin/admin_panel.html',
        'templates/admin/admin_usuarios.html',
        'templates/admin/admin_equipos.html',
        'templates/admin/admin_prestamos.html',
        'templates/admin/admin_reportes.html',
        'templates/admin/admin_configuracion.html'
    ]
    
    archivos_faltantes = []
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo}")
            archivos_faltantes.append(archivo)
    
    for archivo in archivos_admin:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ⚠️  {archivo} (opcional)")
    
    if archivos_faltantes:
        print(f"\n❌ Archivos faltantes: {', '.join(archivos_faltantes)}")
        return False
    
    return True

def main():
    print("🎓 Sistema de Préstamos IUNP")
    print("=" * 40)
    
    # Verificar Python
    if not verificar_python():
        return False
    
    # Verificar archivos
    if not verificar_archivos():
        print("\n💡 Asegúrate de tener todos los archivos en el directorio actual")
        return False
    
    # Instalar dependencias
    try:
        instalar_dependencias()
    except Exception as e:
        print(f"⚠️  Error instalando dependencias: {e}")
        print("   Intenta instalar manualmente: pip install flask flask-sqlalchemy flask-login werkzeug")
    
    print("\n🚀 Iniciando servidor...")
    print("   URL: http://localhost:5000")
    print("   Presiona Ctrl+C para detener\n")
    
    try:
        # Iniciar el servidor Flask
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("\n💡 Soluciones posibles:")
        print("   1. Verificar que todas las dependencias estén instaladas")
        print("   2. Ejecutar: pip install flask flask-sqlalchemy flask-login werkzeug")
        print("   3. Verificar que los archivos estén en el directorio correcto")
        return False
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("💡 Contacta al administrador del sistema")
