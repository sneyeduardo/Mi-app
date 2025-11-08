#!/usr/bin/env python3
"""
Script para generar tokens de acceso único de administrador
Uso: python admin_token_generator.py
"""

import os
import sys
import secrets
import string
from datetime import datetime, timedelta

# Agregar el directorio actual al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=== GENERADOR DE TOKEN DE ACCESO ÚNICO DE ADMINISTRADOR ===\n")
    
    try:
        # Importar componentes del sistema
        from models import db, Usuario, TokenAcceso, generar_token_acceso, TipoUsuario
        from werkzeug.security import generate_password_hash
        
        # Configurar Flask app context
        from flask import Flask
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'tu-clave-secreta-super-segura-aqui'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_prestamos.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Verificar conexión a base de datos
            db.create_all()
            
            # Buscar usuario administrador
            admin = Usuario.query.filter_by(tipo_usuario=TipoUsuario.ADMIN).first()
            
            if not admin:
                print("❌ No se encontró ningún usuario administrador en el sistema.")
                print("\nCargando credenciales de administrador por defecto...")
                
                # Crear administrador por defecto
                admin = Usuario(
                    cedula='admin',
                    nombre='Administrador',
                    apellido='Sistema',
                    email='admin@sistema.com',
                    password_hash=generate_password_hash('admin123'),
                    tipo_usuario=TipoUsuario.ADMIN,
                    activo=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario administrador creado exitosamente.")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
            
            print(f"\n👤 Usuario administrador encontrado: {admin.nombre_completo} (ID: {admin.id})")
            
            # Generar token de acceso único
            minutos_exp = 60  # 1 hora por defecto
            token = generar_token_acceso(
                usuario_id=admin.id,
                minutos_exp=minutos_exp,
                descripcion="Token de acceso único generado manualmente",
                ip_origen="127.0.0.1"
            )
            
            # Construir URLs
            base_url = "http://localhost:5000"  # Ajustar según el servidor
            url_acceso = f"{base_url}/admin/acceso-unico/{token}"
            url_login_normal = f"{base_url}/login"
            
            print(f"\n🔑 TOKEN DE ACCESO ÚNICO GENERADO EXITOSAMENTE:")
            print("=" * 60)
            print(f"Token: {token}")
            print(f"Expira en: {minutos_exp} minutos")
            print(f"URL de acceso directo: {url_acceso}")
            print("=" * 60)
            
            print(f"\n📋 INSTRUCCIONES:")
            print(f"1. Copia la URL: {url_acceso}")
            print(f"2. Ábrela en tu navegador para acceso directo")
            print(f"3. El token se desactivará automáticamente después del primer uso")
            print(f"4. Tiempo disponible: {minutos_exp} minutos desde su generación")
            
            print(f"\n🔐 ACCESO ALTERNATIVO:")
            print(f"URL de login normal: {url_login_normal}")
            print(f"Usuario: admin")
            print(f"Contraseña: admin123")
            
            print(f"\n✅ ¡Token generado! Úsalo antes de que expire.")
            
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Asegúrate de estar ejecutando el script desde el directorio correcto.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()