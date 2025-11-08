#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 SCRIPT DE INICIO AUTOMÁTICO - SISTEMA PRÉSTAMOS IUNP
Este script verifica e inicia automáticamente todo el sistema
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def imprimir_banner():
    print("="*80)
    print("🎓 SISTEMA DE PRÉSTAMOS - INSTITUTO UNIVERSITARIO DE VENEZUELA (IUNP)")
    print("="*80)
    print()

def verificar_python():
    """Verifica que Python esté instalado y sea la versión correcta"""
    print("🐍 Verificando Python...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        return False
    
    print("✅ Versión de Python correcta")
    return True

def verificar_directorio():
    """Verifica que estemos en el directorio correcto"""
    print("\\n📁 Verificando directorio...")
    archivos_necesarios = ['app.py', 'models.py', 'forms.py', 'templates']
    
    for archivo in archivos_necesarios:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} no encontrado")
            return False
    
    print("✅ Directorio correcto - todos los archivos presentes")
    return True

def instalar_dependencias():
    """Instala las dependencias de Flask si no están instaladas"""
    print("\\n📦 Verificando e instalando dependencias...")
    
    dependencias = ['flask', 'flask-sqlalchemy', 'flask-login', 'werkzeug']
    
    for dep in dependencias:
        print(f"   Verificando {dep}...")
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✅ {dep} ya instalado")
        except ImportError:
            print(f"   📥 Instalando {dep}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep], 
                                    stdout=subprocess.DEVNULL, 
                                    stderr=subprocess.DEVNULL)
                print(f"   ✅ {dep} instalado correctamente")
            except subprocess.CalledProcessError:
                print(f"   ❌ Error instalando {dep}")
                return False
    
    return True

def verificar_sintaxis():
    """Verifica que no haya errores de sintaxis"""
    print("\\n🔍 Verificando sintaxis de archivos...")
    
    archivos_py = ['app.py', 'models.py', 'forms.py']
    
    for archivo in archivos_py:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                compile(f.read(), archivo, 'exec')
            print(f"   ✅ {archivo}")
        except SyntaxError as e:
            print(f"   ❌ Error en {archivo}: {e}")
            return False
        except FileNotFoundError:
            print(f"   ❌ {archivo} no encontrado")
            return False
    
    print("✅ Todos los archivos Python son correctos")
    return True

def iniciar_servidor():
    """Inicia el servidor Flask"""
    print("\\n🚀 Iniciando servidor Flask...")
    print("   📍 URL: http://localhost:5000")
    print("   ⏹️  Para detener: Ctrl+C")
    print("   🔄 Iniciando en 3 segundos...")
    
    time.sleep(3)
    
    try:
        # Abrir navegador automáticamente
        print("   🌐 Abriendo navegador...")
        webbrowser.open('http://localhost:5000')
        
        # Iniciar servidor
        print("   🟢 Servidor iniciado - ¡Listo!")
        subprocess.call([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\\n   🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\\n   ❌ Error iniciando servidor: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    imprimir_banner()
    
    # Lista de verificaciones
    pasos = [
        ("Python", verificar_python),
        ("Directorio", verificar_directorio),
        ("Dependencias", instalar_dependencias),
        ("Sintaxis", verificar_sintaxis)
    ]
    
    # Ejecutar verificaciones
    for nombre, funcion in pasos:
        print(f"\\n{'='*60}")
        print(f"PASO: {nombre}")
        print('='*60)
        
        if not funcion():
            print(f"\\n❌ FALLO EN: {nombre}")
            print("\\n📋 SOLUCIÓN MANUAL:")
            print("1. Asegúrate de estar en: C:\\Users\\olmedo\\Documents\\Sistema_completo_prestamos\\")
            print("2. Ejecuta: pip install flask flask-sqlalchemy flask-login werkzeug")
            print("3. Ejecuta manualmente: python app.py")
            return False
    
    print("\\n" + "="*60)
    print("🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
    print("="*60)
    
    # Iniciar servidor
    if iniciar_servidor():
        print("\\n✅ ¡SISTEMA CERRADO CORRECTAMENTE!")
    else:
        print("\\n❌ ERROR INICIANDO EL SISTEMA")
    
    return True

if __name__ == "__main__":
    print("\\n🎯 Presiona Enter para continuar o Ctrl+C para cancelar...")
    input()
    main()