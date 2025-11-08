#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 DIAGNÓSTICO PASO A PASO - MUY SIMPLE
Ejecuta cada verificación individualmente para identificar el problema
"""

import os
import sys

print("="*60)
print("🔧 DIAGNÓSTICO PASO A PASO - SISTEMA IUNP")
print("="*60)

print("\\n1️⃣ VERIFICANDO DIRECTORIO ACTUAL:")
print(f"   Directorio: {os.getcwd()}")
print(f"   Python: {sys.executable}")

print("\\n2️⃣ VERIFICANDO ARCHIVOS PRINCIPALES:")
archivos = ['app.py', 'models.py', 'forms.py']
for archivo in archivos:
    existe = os.path.exists(archivo)
    print(f"   {'✅' if existe else '❌'} {archivo}")

if not all(os.path.exists(arch) for arch in archivos):
    print("\\n❌ ARCHIVOS FALTANTES!")
    print("   Asegúrate de estar en: C:\\Users\\olmedo\\Documents\\Sistema_completo_prestamos\\")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)

print("\\n3️⃣ VERIFICANDO SINTÁXIS DE APP.PY:")
try:
    with open('app.py', 'r', encoding='utf-8') as f:
        codigo = f.read()
    compile(codigo, 'app.py', 'exec')
    print("   ✅ app.py compila correctamente")
except SyntaxError as e:
    print(f"   ❌ Error en app.py línea {e.lineno}: {e.msg}")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error leyendo app.py: {e}")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)

print("\\n4️⃣ VERIFICANDO INSTALACIÓN DE FLASK:")
try:
    import flask
    print(f"   ✅ Flask {flask.__version__} instalado")
except ImportError:
    print("   ❌ Flask NO está instalado")
    print("   💡 Ejecuta: pip install flask flask-sqlalchemy flask-login werkzeug")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)

print("\\n5️⃣ VERIFICANDO IMPORTACIÓN DE MÓDULOS:")
try:
    from models import db, Usuario, Equipo, Prestamo
    print("   ✅ models.py se importa")
except Exception as e:
    print(f"   ❌ Error importando models.py: {e}")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)

try:
    from forms import LoginForm, RegistrationForm
    print("   ✅ forms.py se importa")
except Exception as e:
    print(f"   ❌ Error importando forms.py: {e}")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)

print("\\n6️⃣ VERIFICANDO BASE.HTML:")
try:
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        base_content = f.read()
    
    # Contar bloques if/endif
    if_blocks = base_content.count('{% if')
    endif_blocks = base_content.count('{% endif')
    
    print(f"   📊 Bloques if: {if_blocks}, endif: {endif_blocks}")
    
    if if_blocks == endif_blocks:
        print("   ✅ base.html tiene sintaxis Jinja2 balanceada")
    else:
        print("   ❌ base.html tiene problemas de sintaxis Jinja2")
        input("\\n🔄 Presiona Enter para salir...")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error leyendo base.html: {e}")
    input("\\n🔄 Presiona Enter para salir...")
    sys.exit(1)

print("\\n" + "="*60)
print("🎉 ¡TODOS LOS DIAGNÓSTICOS PASARON!")
print("="*60)

print("\\n✅ EL SISTEMA ESTÁ LISTO PARA INICIAR")
print("\\n🚀 EJECUTA ESTE COMANDO:")
print("   python app.py")
print("\\n🌐 LUEGO VE A:")
print("   http://localhost:5000")

print("\\n🔧 SI PREFIERES QUE LO HAGA AUTOMÁTICAMENTE:")
print("   Responde 's' para iniciar ahora, cualquier otra cosa para salir")
respuesta = input("\\n¿Iniciar servidor automáticamente? (s/n): ")

if respuesta.lower() == 's':
    print("\\n🚀 Iniciando servidor Flask...")
    try:
        import subprocess
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\\n👋 Servidor detenido")
    except Exception as e:
        print(f"\\n❌ Error iniciando servidor: {e}")
else:
    print("\\n👋 Saliendo...")

input("\\n🔄 Presiona Enter para salir...")