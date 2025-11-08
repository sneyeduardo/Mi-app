#!/usr/bin/env python3
"""
Script para verificar y mostrar credenciales de administrador actuales
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=== VERIFICACIÓN DE CREDENCIALES DE ADMINISTRADOR ===\n")
    
    try:
        # Importar componentes
        from models import db, Usuario, TipoUsuario
        from flask import Flask
        from werkzeug.security import generate_password_hash
        
        # Configurar Flask app context
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'tu-clave-secreta-super-segura-aqui'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_prestamos.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Verificar/crear tablas
            db.create_all()
            
            # Buscar administradores
            admins = Usuario.query.filter_by(tipo_usuario=TipoUsuario.ADMIN).all()
            
            if not admins:
                print("⚠️  No se encontraron administradores.")
                print("\nCreando administrador por defecto...")
                
                admin = Usuario(
                    cedula='admin',
                    nombre='Administrador',
                    apellido='Sistema',
                    email='admin@sistema.com',
                    password_hash=generate_password_hash('admin123'),
                    tipo_usuario=TipoUsuario.ADMIN,
                    activo=True,
                    fecha_registro=datetime.utcnow()
                )
                db.session.add(admin)
                db.session.commit()
                
                print("✅ Usuario administrador creado:")
                print("   Cédula: admin")
                print("   Contraseña: admin123")
                print("   Estado: Activo")
                
            else:
                print(f"✅ Se encontraron {len(admins)} administrador(es):")
                print("=" * 50)
                
                for i, admin in enumerate(admins, 1):
                    status = "🟢 Activo" if admin.activo else "🔴 Inactivo"
                    print(f"{i}. {admin.nombre_completo}")
                    print(f"   Cédula: {admin.cedula}")
                    print(f"   Email: {admin.email}")
                    print(f"   Estado: {status}")
                    print(f"   Registrado: {admin.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Intentar determinar la contraseña (para info únicamente)
                    if admin.cedula == 'admin':
                        print(f"   🔑 Contraseña conocida: admin123")
                    else:
                        print(f"   ⚠️  Contraseña desconocida (requiere reset)")
                    
                    print("-" * 30)
                
                print("\n🔐 CREDENCIALES PARA ACCESO:")
                admin_por_defecto = next((a for a in admins if a.cedula == 'admin'), admins[0])
                print(f"URL de login: http://localhost:5000/login")
                print(f"Usuario: {admin_por_defecto.cedula}")
                print(f"Contraseña: {'admin123' if admin_por_defecto.cedula == 'admin' else 'DESCONOCIDA'}")
                
            print(f"\n💡 SIGUIENTE PASO:")
            print("1. Ve a http://localhost:5000/login")
            print("2. Usa las credenciales mostradas arriba")
            print("3. Una vez dentro, usa /admin/token/generar para crear tokens únicos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()