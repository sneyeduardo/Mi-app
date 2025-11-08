#!/usr/bin/env python3
"""
Script de inicio para el Sistema de Préstamos IUNP
Desarrollado por Sney Perez
"""

import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash

# Importar modelos y funciones
from models import db, init_db, create_admin_user
from demo_data import crear_datos_demo

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias = [
        'flask', 'flask_login', 'flask_wtf', 'flask_sqlalchemy',
        'werkzeug', 'wtforms', 'email_validator', 'sqlalchemy'
    ]
    
    faltantes = []
    for dep in dependencias:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            faltantes.append(dep)
    
    if faltantes:
        print("❌ Dependencias faltantes:")
        for dep in faltantes:
            print(f"   - {dep}")
        print("\n💡 Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def inicializar_sistema():
    """Inicializa el sistema completo"""
    print("🚀 Inicializando Sistema de Préstamos IUNP...")
    print("=" * 50)
    
    # Configurar aplicación Flask
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'sistema-prestamos-secreto-2025'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///sistema_prestamos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    
    with app.app_context():
        # Crear tablas
        print("📊 Creando base de datos...")
        init_db()
        
        # Crear usuario administrador
        print("👤 Creando usuario administrador...")
        create_admin_user()
        
        # Crear datos demo
        print("🎯 Creando datos de demostración...")
        crear_datos_demo()
        
        print("\n✅ Sistema inicializado correctamente!")
        print("=" * 50)
        
    return app

def main():
    """Función principal"""
    print("🏛️  SISTEMA DE PRÉSTAMOS IUNP")
    print("Instituto Universitario de Venezuela")
    print("Desarrollado por Sney Perez")
    print("=" * 50)
    
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    try:
        # Inicializar sistema
        app = inicializar_sistema()
        
        print("🌐 Iniciando servidor web...")
        print("📱 Accede al sistema en: http://localhost:5000")
        print("\n👥 Credenciales de prueba:")
        print("   Admin: admin / admin123")
        print("   Estudiante: 12345678 / password")
        print("   Profesor: 87654321 / password")
        print("\n🛑 Presiona Ctrl+C para detener el servidor")
        print("=" * 50)
        
        # Iniciar servidor
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el sistema: {e}")
        print("💡 Verifica que todas las dependencias estén instaladas")
        sys.exit(1)

if __name__ == '__main__':
    main()