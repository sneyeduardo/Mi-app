#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de demostración.
Ejecutar después de inicializar la base de datos.
"""

from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import (db, Usuario, Equipo, Prestamo, HistorialAcciones, 
                   TipoUsuario, EstadoPrestamo, CategoriaEquipo)

def crear_usuarios_demo():
    """Crear usuarios de demostración"""
    usuarios = [
        {
            'cedula': 'admin',
            'nombre': 'Administrador',
            'apellido': 'Sistema',
            'email': 'admin@sistema.com',
            'telefono': '555-0001',
            'password': 'admin123',
            'tipo_usuario': TipoUsuario.ADMIN
        },
        {
            'cedula': '12345678',
            'nombre': 'María',
            'apellido': 'González',
            'email': 'maria.gonzalez@email.com',
            'telefono': '555-0002',
            'password': 'profesor123',
            'tipo_usuario': TipoUsuario.PROFESOR
        },
        {
            'cedula': '87654321',
            'nombre': 'Carlos',
            'apellido': 'Rodríguez',
            'email': 'carlos.rodriguez@email.com',
            'telefono': '555-0003',
            'password': 'profesor123',
            'tipo_usuario': TipoUsuario.PROFESOR
        },
        {
            'cedula': '11111111',
            'nombre': 'Ana',
            'apellido': 'Martínez',
            'email': 'ana.martinez@estudiante.com',
            'telefono': '555-0004',
            'password': 'estudiante123',
            'tipo_usuario': TipoUsuario.ESTUDIANTE
        },
        {
            'cedula': '22222222',
            'nombre': 'Luis',
            'apellido': 'Pérez',
            'email': 'luis.perez@estudiante.com',
            'telefono': '555-0005',
            'password': 'estudiante123',
            'tipo_usuario': TipoUsuario.ESTUDIANTE
        },
        {
            'cedula': '33333333',
            'nombre': 'Carmen',
            'apellido': 'López',
            'email': 'carmen.lopez@estudiante.com',
            'telefono': '555-0006',
            'password': 'estudiante123',
            'tipo_usuario': TipoUsuario.ESTUDIANTE
        },
        {
            'cedula': '44444444',
            'nombre': 'Roberto',
            'apellido': 'Fernández',
            'email': 'roberto.fernandez@estudiante.com',
            'telefono': '555-0007',
            'password': 'estudiante123',
            'tipo_usuario': TipoUsuario.ESTUDIANTE
        }
    ]
    
    usuarios_creados = []
    for datos_usuario in usuarios:
        # Verificar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(cedula=datos_usuario['cedula']).first()
        if not usuario_existente:
            usuario = Usuario(
                cedula=datos_usuario['cedula'],
                nombre=datos_usuario['nombre'],
                apellido=datos_usuario['apellido'],
                email=datos_usuario['email'],
                telefono=datos_usuario['telefono'],
                password_hash=generate_password_hash(datos_usuario['password']),
                tipo_usuario=datos_usuario['tipo_usuario']
            )
            db.session.add(usuario)
            usuarios_creados.append(usuario)
    
    db.session.commit()
    print(f"✓ Creados {len(usuarios_creados)} usuarios de demostración")
    return usuarios_creados

def crear_equipos_demo():
    """Crear equipos de demostración"""
    equipos = [
        {
            'codigo': 'LAP-001',
            'nombre': 'Laptop Dell Inspiron 15',
            'descripcion': 'Laptop Dell Inspiron 15 con procesador Intel Core i5, 8GB RAM, 256GB SSD. Ideal para trabajo de oficina y desarrollo.',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Dell',
            'modelo': 'Inspiron 15 3000',
            'numero_serie': 'DL15-2023-001',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'LAP-002',
            'nombre': 'Laptop HP Pavilion',
            'descripcion': 'Laptop HP Pavilion con procesador AMD Ryzen 5, 16GB RAM, 512GB SSD. Excelente para diseño gráfico.',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'HP',
            'modelo': 'Pavilion 15-eh',
            'numero_serie': 'HP15-2023-002',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'LAP-003',
            'nombre': 'MacBook Air M1',
            'descripcion': 'MacBook Air con chip M1, 8GB RAM, 256GB SSD. Perfecto para desarrollo y aplicaciones creativas.',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Apple',
            'modelo': 'MacBook Air M1',
            'numero_serie': 'MBA-2023-003',
            'estado': 'prestado',
            'disponible': False
        },
        {
            'codigo': 'PROJ-001',
            'nombre': 'Proyector Epson PowerLite',
            'descripcion': 'Proyector Epson PowerLite con resolución Full HD, 3500 lúmenes. Incluye cables HDMI y VGA.',
            'categoria': CategoriaEquipo.PROYECTOR,
            'marca': 'Epson',
            'modelo': 'PowerLite 1795F',
            'numero_serie': 'EP-PROJ-001',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'PROJ-002',
            'nombre': 'Proyector BenQ MX531',
            'descripcion': 'Proyector DLP con alta luminosidad, ideal para aulas grandes. Resolución XGA.',
            'categoria': CategoriaEquipo.PROYECTOR,
            'marca': 'BenQ',
            'modelo': 'MX531',
            'numero_serie': 'BQ-PROJ-002',
            'estado': 'mantenimiento',
            'disponible': False
        },
        {
            'codigo': 'CAM-001',
            'nombre': 'Cámara Canon EOS Rebel',
            'descripcion': 'Cámara DSLR Canon EOS Rebel T7i con lente 18-55mm. Ideal para fotografía y video.',
            'categoria': CategoriaEquipo.AUDIOVISUAL,
            'marca': 'Canon',
            'modelo': 'EOS Rebel T7i',
            'numero_serie': 'CN-CAM-001',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'TAB-001',
            'nombre': 'Tablet iPad Air',
            'descripcion': 'iPad Air con pantalla de 10.9 pulgadas, chip A14 Bionic, 64GB. Incluye Apple Pencil.',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Apple',
            'modelo': 'iPad Air 4ta Gen',
            'numero_serie': 'IPAD-TAB-001',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'MIC-001',
            'nombre': 'Micrófono Blue Yeti',
            'descripcion': 'Micrófono de condensador USB profesional. Ideal para grabación de audio y streaming.',
            'categoria': CategoriaEquipo.AUDIOVISUAL,
            'marca': 'Blue',
            'modelo': 'Yeti USB',
            'numero_serie': 'BY-MIC-001',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'IMP-001',
            'nombre': 'Impresora 3D Ender 3',
            'descripcion': 'Impresora 3D Creality Ender 3 V2. Volumen de impresión 220x220x250mm. Incluye filamento PLA.',
            'categoria': CategoriaEquipo.HERRAMIENTAS,
            'marca': 'Creality',
            'modelo': 'Ender 3 V2',
            'numero_serie': 'CR-IMP-001',
            'estado': 'disponible',
            'disponible': True
        },
        {
            'codigo': 'OSC-001',
            'nombre': 'Osciloscopio Digital',
            'descripcion': 'Osciloscopio digital de 2 canales, 100MHz, para prácticas de electrónica.',
            'categoria': CategoriaEquipo.LABORATORIO,
            'marca': 'Rigol',
            'modelo': 'DS1054Z',
            'numero_serie': 'RG-OSC-001',
            'estado': 'disponible',
            'disponible': True
        }
    ]
    
    equipos_creados = []
    for datos_equipo in equipos:
        # Verificar si el equipo ya existe
        equipo_existente = Equipo.query.filter_by(codigo=datos_equipo['codigo']).first()
        if not equipo_existente:
            equipo = Equipo(
                codigo=datos_equipo['codigo'],
                nombre=datos_equipo['nombre'],
                descripcion=datos_equipo['descripcion'],
                categoria=datos_equipo['categoria'],
                marca=datos_equipo['marca'],
                modelo=datos_equipo['modelo'],
                numero_serie=datos_equipo['numero_serie'],
                estado=datos_equipo['estado'],
                disponible=datos_equipo['disponible'],
                fecha_adquisicion=datetime.now() - timedelta(days=30)  # 30 días atrás
            )
            db.session.add(equipo)
            equipos_creados.append(equipo)
    
    db.session.commit()
    print(f"✓ Creados {len(equipos_creados)} equipos de demostración")
    return equipos_creados

def crear_prestamos_demo():
    """Crear préstamos de demostración"""
    # Obtener usuarios y equipos existentes
    estudiantes = Usuario.query.filter_by(tipo_usuario=TipoUsuario.ESTUDIANTE).all()
    equipos = Equipo.query.all()
    admin = Usuario.query.filter_by(tipo_usuario=TipoUsuario.ADMIN).first()
    
    if not estudiantes or not equipos or not admin:
        print("⚠ No se pueden crear préstamos: faltan usuarios o equipos")
        return []
    
    prestamos = [
        {
            'usuario': estudiantes[0],  # Ana Martínez
            'equipo': equipos[0],       # Laptop Dell
            'fecha_inicio': datetime.now() + timedelta(days=1),
            'fecha_fin_programada': datetime.now() + timedelta(days=8),
            'motivo': 'Proyecto de fin de carrera - Desarrollo de aplicación web con base de datos',
            'estado': EstadoPrestamo.SOLICITADO,
            'observaciones_usuario': 'Necesito la laptop para trabajar en mi proyecto final'
        },
        {
            'usuario': estudiantes[1],  # Luis Pérez
            'equipo': equipos[2],       # MacBook Air
            'fecha_inicio': datetime.now() - timedelta(days=5),
            'fecha_fin_programada': datetime.now() + timedelta(days=2),
            'motivo': 'Curso de desarrollo móvil iOS - Necesito Xcode y simulador',
            'estado': EstadoPrestamo.APROBADO,
            'observaciones_usuario': 'Primera vez usando macOS',
            'aprobado_por': admin,
            'fecha_aprobacion': datetime.now() - timedelta(days=4)
        },
        {
            'usuario': estudiantes[2],  # Carmen López
            'equipo': equipos[3],       # Proyector Epson
            'fecha_inicio': datetime.now() - timedelta(days=10),
            'fecha_fin_programada': datetime.now() - timedelta(days=3),
            'motivo': 'Presentación de proyecto grupal de Sistemas Distribuidos',
            'estado': EstadoPrestamo.DEVUELTO,
            'observaciones_usuario': 'Presentación para 50 personas en el auditorio',
            'aprobado_por': admin,
            'fecha_aprobacion': datetime.now() - timedelta(days=9),
            'fecha_devolucion': datetime.now() - timedelta(days=3)
        },
        {
            'usuario': estudiantes[3],  # Roberto Fernández
            'equipo': equipos[1],       # HP Pavilion
            'fecha_inicio': datetime.now() + timedelta(days=3),
            'fecha_fin_programada': datetime.now() + timedelta(days=10),
            'motivo': 'Prácticas de laboratorio de Redes de Computadoras',
            'estado': EstadoPrestamo.SOLICITADO,
            'observaciones_usuario': 'Configuración de servidores virtuales'
        },
        {
            'usuario': estudiantes[0],  # Ana Martínez
            'equipo': equipos[5],       # Cámara Canon
            'fecha_inicio': datetime.now() - timedelta(days=15),
            'fecha_fin_programada': datetime.now() - timedelta(days=1),
            'motivo': 'Documentación fotográfica para tesis de Diseño Gráfico',
            'estado': EstadoPrestamo.VENCIDO,
            'observaciones_usuario': 'Sesión de fotos para portafolio de graduación',
            'aprobado_por': admin,
            'fecha_aprobacion': datetime.now() - timedelta(days=14)
        }
    ]
    
    prestamos_creados = []
    for datos_prestamo in prestamos:
        prestamo = Prestamo(
            usuario_id=datos_prestamo['usuario'].id,
            equipo_id=datos_prestamo['equipo'].id,
            fecha_inicio=datos_prestamo['fecha_inicio'],
            fecha_fin_programada=datos_prestamo['fecha_fin_programada'],
            motivo=datos_prestamo['motivo'],
            estado=datos_prestamo['estado'],
            observaciones_usuario=datos_prestamo.get('observaciones_usuario'),
            aprobado_por_id=datos_prestamo.get('aprobado_por').id if datos_prestamo.get('aprobado_por') else None,
            fecha_aprobacion=datos_prestamo.get('fecha_aprobacion'),
            fecha_devolucion=datos_prestamo.get('fecha_devolucion')
        )
        
        # Actualizar estado del equipo según el préstamo
        if datos_prestamo['estado'] == EstadoPrestamo.APROBADO or datos_prestamo['estado'] == EstadoPrestamo.VENCIDO:
            datos_prestamo['equipo'].estado = 'prestado'
            datos_prestamo['equipo'].disponible = False
        
        db.session.add(prestamo)
        prestamos_creados.append(prestamo)
    
    db.session.commit()
    print(f"✓ Creados {len(prestamos_creados)} préstamos de demostración")
    return prestamos_creados

def crear_historial_demo(usuarios):
    """Crear historial de acciones de demostración"""
    if not usuarios:
        return
    
    acciones = [
        {
            'usuario': usuarios[0],  # Admin
            'accion': 'inicializar_sistema',
            'descripcion': 'Sistema inicializado con datos de demostración',
            'fecha': datetime.now() - timedelta(hours=1)
        },
        {
            'usuario': usuarios[1],  # María González
            'accion': 'login',
            'descripcion': 'Primer acceso al sistema',
            'fecha': datetime.now() - timedelta(minutes=30)
        }
    ]
    
    for datos_accion in acciones:
        historial = HistorialAcciones(
            usuario_id=datos_accion['usuario'].id,
            accion=datos_accion['accion'],
            descripcion=datos_accion['descripcion'],
            fecha=datos_accion['fecha']
        )
        db.session.add(historial)
    
    db.session.commit()
    print(f"✓ Creado historial de acciones de demostración")

def main():
    """Función principal para crear todos los datos de demostración"""
    with app.app_context():
        print("🚀 Iniciando creación de datos de demostración...")
        print("=" * 50)
        
        # Crear usuarios
        usuarios = crear_usuarios_demo()
        
        # Crear equipos
        equipos = crear_equipos_demo()
        
        # Crear préstamos
        prestamos = crear_prestamos_demo()
        
        # Crear historial
        crear_historial_demo(usuarios)
        
        print("=" * 50)
        print("✅ Datos de demostración creados exitosamente!")
        print("\n📋 Resumen:")
        print(f"   👥 Usuarios: {len(usuarios)} creados")
        print(f"   💻 Equipos: {len(equipos)} creados")
        print(f"   📋 Préstamos: {len(prestamos) if prestamos else 0} creados")
        
        print("\n🔑 Credenciales de acceso:")
        print("   👤 Administrador:")
        print("      Cédula: admin")
        print("      Contraseña: admin123")
        print("   👨‍🏫 Profesores:")
        print("      Cédula: 12345678 | Contraseña: profesor123")
        print("      Cédula: 87654321 | Contraseña: profesor123")
        print("   🎓 Estudiantes:")
        print("      Cédula: 11111111 | Contraseña: estudiante123")
        print("      Cédula: 22222222 | Contraseña: estudiante123")
        print("      Cédula: 33333333 | Contraseña: estudiante123")
        print("      Cédula: 44444444 | Contraseña: estudiante123")
        
        print("\n🌐 Para acceder al sistema:")
        print("   http://localhost:5000")

if __name__ == "__main__":
    main()
