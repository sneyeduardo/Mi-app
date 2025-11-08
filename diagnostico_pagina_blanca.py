#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 DIAGNÓSTICO ESPECÍFICO - PÁGINA EN BLANCO
Script para diagnosticar problemas de página en blanco
"""

import os
import sys
import traceback
from pathlib import Path

def diagnosticar_base_html():
    """Diagnostica problemas específicos en base.html"""
    print("🔍 Diagnóstico de base.html...")
    
    try:
        with open('templates/base.html', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar bloques if/endif
        if_blocks = contenido.count('{% if')
        endif_blocks = contenido.count('{% endif')
        
        print(f"   📊 Bloques 'if': {if_blocks}")
        print(f"   📊 Bloques 'endif': {endif_blocks}")
        
        if if_blocks != endif_blocks:
            print("   ❌ DESBALANCE: Hay más 'if' que 'endif'")
            return False
        
        # Verificar duplicados endif
        lines = contenido.split('\\n')
        endif_duplicados = 0
        for i, line in enumerate(lines):
            if '{% endif %}' in line:
                # Verificar si la siguiente línea también tiene endif
                if i + 1 < len(lines) and '{% endif %}' in lines[i + 1]:
                    endif_duplicados += 1
                    print(f"   ⚠️  DUPLICADO endif en línea {i+2}: {lines[i+1].strip()}")
        
        if endif_duplicados > 0:
            print(f"   ❌ Encontrados {endif_duplicados} endif duplicados")
            return False
        
        print("   ✅ base.html tiene sintaxis correcta")
        return True
        
    except Exception as e:
        print(f"   ❌ Error leyendo base.html: {e}")
        return False

def diagnosticar_rutas():
    """Diagnostica problemas en las rutas de Flask"""
    print("\\n🛣️ Diagnóstico de rutas Flask...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar ruta principal
        if "@app.route('/')" in contenido or "@app.route('/index')" in contenido:
            print("   ✅ Ruta principal (/) definida")
        else:
            print("   ❌ Ruta principal (/) no encontrada")
            return False
        
        # Verificar función index
        if "def index():" in contenido:
            print("   ✅ Función index() definida")
        else:
            print("   ❌ Función index() no encontrada")
            return False
        
        # Verificar render_template para index
        if "render_template('index.html')" in contenido:
            print("   ✅ Renderizado de index.html configurado")
        else:
            print("   ⚠️  Renderizado de index.html no encontrado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error analizando rutas: {e}")
        return False

def diagnosticar_imports():
    """Diagnostica problemas de importación"""
    print("\\n📦 Diagnóstico de importaciones...")
    
    try:
        # Verificar que los módulos se puedan importar
        test_code = '''
import sys
sys.path.insert(0, ".")

try:
    from models import db, Usuario, Equipo, Prestamo
    print("✅ models.py se importa correctamente")
except Exception as e:
    print(f"❌ Error importando models.py: {e}")

try:
    from forms import LoginForm, RegistroForm
    print("✅ forms.py se importa correctamente")
except Exception as e:
    print(f"❌ Error importando forms.py: {e}")
'''
        
        exec(test_code)
        return True
        
    except Exception as e:
        print(f"   ❌ Error en diagnóstico de imports: {e}")
        return False

def diagnosticar_configuracion_flask():
    """Diagnostica la configuración de Flask"""
    print("\\n⚙️ Diagnóstico de configuración Flask...")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        checks = [
            ("SECRET_KEY", "app.config['SECRET_KEY']"),
            ("DATABASE_URI", "SQLALCHEMY_DATABASE_URI"),
            ("Flask app", "app = Flask(__name__)"),
            ("db.init_app", "db.init_app(app)"),
            ("login_manager", "LoginManager()")
        ]
        
        todo_correcto = True
        for nombre, patron in checks:
            if patron in contenido:
                print(f"   ✅ {nombre} configurado")
            else:
                print(f"   ❌ {nombre} NO configurado")
                todo_correcto = False
        
        return todo_correcto
        
    except Exception as e:
        print(f"   ❌ Error verificando configuración: {e}")
        return False

def generar_reporte():
    """Genera un reporte completo del diagnóstico"""
    print("="*70)
    print("📋 REPORTE COMPLETO DE DIAGNÓSTICO")
    print("="*70)
    
    diagnosticos = [
        ("Sintaxis base.html", diagnosticar_base_html),
        ("Rutas Flask", diagnosticar_rutas),
        ("Importaciones", diagnosticar_imports),
        ("Configuración Flask", diagnosticar_configuracion_flask)
    ]
    
    resultados = []
    for nombre, funcion in diagnosticos:
        print(f"\\n{'='*30} {nombre} {'='*30}")
        resultado = funcion()
        resultados.append((nombre, resultado))
    
    print("\\n" + "="*70)
    print("📊 RESUMEN FINAL")
    print("="*70)
    
    todos_ok = True
    for nombre, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"   {status} {nombre}")
        if not resultado:
            todos_ok = False
    
    print()
    if todos_ok:
        print("🎉 ¡SISTEMA COMPLETAMENTE CORRECTO!")
        print("\\nSi la página sigue en blanco:")
        print("1. Reinicia tu navegador (Ctrl+F5)")
        print("2. Limpia la caché del navegador")
        print("3. Verifica que el servidor esté ejecutándose en http://localhost:5000")
        print("4. Revisa la consola del navegador para errores JavaScript")
    else:
        print("❌ SE ENCONTRARON PROBLEMAS")
        print("\\nEjecuta las correcciones necesarias o contacta soporte técnico.")
    
    return todos_ok

def main():
    """Función principal"""
    print("🔧 DIAGNÓSTICO ESPECÍFICO - PÁGINA EN BLANCO")
    print("Sistema de Préstamos IUNP")
    print("="*50)
    
    return generar_reporte()

if __name__ == "__main__":
    main()