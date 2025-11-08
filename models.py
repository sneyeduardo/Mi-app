from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import secrets
import string

db = SQLAlchemy()

class TipoUsuario(Enum):
    ESTUDIANTE = "estudiante"
    PROFESOR = "profesor"
    ADMIN = "admin"

class EstadoPrestamo(Enum):
    SOLICITADO = "solicitado"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    DEVUELTO = "devuelto"
    VENCIDO = "vencido"

class CategoriaEquipo(Enum):
    COMPUTADORA = "computadora"
    PROYECTOR = "proyector"
    LABORATORIO = "laboratorio"
    AUDIOVISUAL = "audiovisual"
    HERRAMIENTAS = "herramientas"
    OTROS = "otros"

class TipoNotificacion(Enum):
    SOLICITUD_PRESTAMO = "solicitud_prestamo"
    APROBACION_PRESTAMO = "aprobacion_prestamo"
    RECHAZO_PRESTAMO = "rechazo_prestamo"
    VENCIMIENTO_PRESTAMO = "vencimiento_prestamo"
    DEVOLUCION_EQUIPO = "devolucion_equipo"
    EQUIPO_DISPONIBLE = "equipo_disponible"
    SISTEMA = "sistema"

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    telefono = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    tipo_usuario = db.Column(db.Enum(TipoUsuario), nullable=False, default=TipoUsuario.ESTUDIANTE)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    prestamos = db.relationship('Prestamo', foreign_keys='Prestamo.usuario_id', backref='usuario', lazy=True)
    prestamos_aprobados = db.relationship('Prestamo', foreign_keys='Prestamo.aprobado_por_id', backref='aprobado_por', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellido}>'
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def es_admin(self):
        return self.tipo_usuario == TipoUsuario.ADMIN
    
    def puede_aprobar_prestamos(self):
        return self.tipo_usuario in [TipoUsuario.ADMIN, TipoUsuario.PROFESOR]

class Equipo(db.Model):
    __tablename__ = 'equipos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.Enum(CategoriaEquipo), nullable=False)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    numero_serie = db.Column(db.String(100))
    estado = db.Column(db.String(20), default='disponible')  # disponible, prestado, mantenimiento, dañado
    disponible = db.Column(db.Boolean, default=True)
    fecha_adquisicion = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    prestamos = db.relationship('Prestamo', backref='equipo', lazy=True)
    
    def __repr__(self):
        return f'<Equipo {self.codigo} - {self.nombre}>'
    
    def esta_disponible(self):
        return self.disponible and self.estado == 'disponible'
    
    def tiene_prestamo_activo(self):
        return any(prestamo.estado in [EstadoPrestamo.APROBADO] 
                  for prestamo in self.prestamos)

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    
    # Fechas
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin_programada = db.Column(db.DateTime, nullable=False)
    fecha_devolucion = db.Column(db.DateTime)
    
    # Estado y aprobación
    estado = db.Column(db.Enum(EstadoPrestamo), default=EstadoPrestamo.SOLICITADO)
    aprobado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_aprobacion = db.Column(db.DateTime)
    
    # Detalles
    motivo = db.Column(db.Text, nullable=False)
    observaciones_usuario = db.Column(db.Text)
    observaciones_admin = db.Column(db.Text)
    
    # Estado del equipo
    estado_equipo_entrega = db.Column(db.Text)
    estado_equipo_devolucion = db.Column(db.Text)
    
    # Relaciones
    
    def __repr__(self):
        return f'<Prestamo {self.id} - {self.usuario.nombre} - {self.equipo.nombre}>'
    
    @property
    def duracion_dias(self):
        if self.fecha_inicio and self.fecha_fin_programada:
            return (self.fecha_fin_programada - self.fecha_inicio).days
        return 0
    
    @property
    def esta_vencido(self):
        if self.estado == EstadoPrestamo.APROBADO and self.fecha_fin_programada:
            return datetime.utcnow() > self.fecha_fin_programada
        return False
    
    @property
    def dias_restantes(self):
        if self.estado == EstadoPrestamo.APROBADO and self.fecha_fin_programada:
            delta = self.fecha_fin_programada - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    def puede_ser_devuelto(self):
        return self.estado == EstadoPrestamo.APROBADO
    
    def puede_ser_aprobado(self):
        return self.estado == EstadoPrestamo.SOLICITADO and self.equipo.esta_disponible()

class HistorialAcciones(db.Model):
    __tablename__ = 'historial_acciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.id'))
    accion = db.Column(db.String(50), nullable=False)  # solicitud, aprobacion, rechazo, devolucion, etc.
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='acciones_realizadas')
    prestamo = db.relationship('Prestamo', backref='historial')
    
    def __repr__(self):
        return f'<HistorialAcciones {self.accion} - {self.usuario.nombre}>'

class TokenAcceso(db.Model):
    __tablename__ = 'tokens_acceso'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), unique=True, nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    fecha_uso = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ip_origen = db.Column(db.String(45))  # Para IPv6 e IPv4
    descripcion = db.Column(db.String(200))
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='tokens_acceso')
    
    def __repr__(self):
        return f'<TokenAcceso {self.token[:8]}... - {self.usuario.nombre}>'
    
    def es_valido(self):
        """Verifica si el token es válido y no ha expirado"""
        return not self.usado and datetime.utcnow() < self.expira_en
    
    def marcar_usado(self):
        """Marca el token como usado"""
        self.usado = True
        self.fecha_uso = datetime.utcnow()
        db.session.commit()

# Funciones auxiliares para la inicialización de la base de datos
def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    db.create_all()

def create_admin_user():
    """Crea un usuario administrador por defecto si no existe"""
    from werkzeug.security import generate_password_hash
    
    admin = Usuario.query.filter_by(cedula='admin').first()
    if not admin:
        admin = Usuario(
            cedula='admin',
            nombre='Administrador',
            apellido='Sistema',
            email='admin@sistema.com',
            password_hash=generate_password_hash('admin123'),
            tipo_usuario=TipoUsuario.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuario administrador creado: cedula='admin', password='admin123'")

def crear_equipos_ejemplo():
    """Crea equipos de ejemplo para demostrar el sistema"""
    from datetime import date
    
    # Lista de equipos de ejemplo
    equipos_ejemplo = [
        {
            'codigo': 'LAP-001',
            'nombre': 'Laptop Dell Inspiron 15',
            'descripcion': 'Laptop para uso académico con procesador Intel i5, 8GB RAM, 256GB SSD',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Dell',
            'modelo': 'Inspiron 15 3000',
            'numero_serie': 'DL3000001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 9, 15)
        },
        {
            'codigo': 'LAP-002',
            'nombre': 'MacBook Air M2',
            'descripcion': 'Laptop Apple con chip M2, 8GB RAM, 256GB SSD para estudiantes de diseño',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Apple',
            'modelo': 'MacBook Air M2',
            'numero_serie': 'APL3000002',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 11, 20)
        },
        {
            'codigo': 'PROY-001',
            'nombre': 'Proyector Epson EB-X05',
            'descripcion': 'Proyector de 3300 lúmenes para presentaciones y clases',
            'categoria': CategoriaEquipo.AUDIOVISUAL,
            'marca': 'Epson',
            'modelo': 'EB-X05',
            'numero_serie': 'EPX05001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 8, 10)
        },
        {
            'codigo': 'CAMP-001',
            'nombre': 'Cámara Canon EOS Rebel T7',
            'descripcion': 'Cámara DSLR para proyectos fotográficos y videos académicos',
            'categoria': CategoriaEquipo.AUDIOVISUAL,
            'marca': 'Canon',
            'modelo': 'EOS Rebel T7',
            'numero_serie': 'CNR70001',
            'estado': 'prestado',
            'disponible': False,
            'fecha_adquisicion': date(2023, 7, 25)
        },
        {
            'codigo': 'MIC-001',
            'nombre': 'Micrófono USB Audio-Technica',
            'descripcion': 'Micrófono profesional USB para podcasts y grabaciones',
            'categoria': CategoriaEquipo.AUDIOVISUAL,
            'marca': 'Audio-Technica',
            'modelo': 'ATR2100x-USB',
            'numero_serie': 'ATU210001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 10, 5)
        },
        {
            'codigo': 'TAB-001',
            'nombre': 'iPad Air 5ta Generación',
            'descripcion': 'Tablet para uso académico, lectura digital y presentaciones',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Apple',
            'modelo': 'iPad Air 5',
            'numero_serie': 'IPA50001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 9, 30)
        },
        {
            'codigo': 'MON-001',
            'nombre': 'Monitor Samsung 24"',
            'descripcion': 'Monitor LED Full HD de 24 pulgadas para trabajo de oficina',
            'categoria': CategoriaEquipo.COMPUTADORA,
            'marca': 'Samsung',
            'modelo': 'F24T350FHC',
            'numero_serie': 'SAM24001',
            'estado': 'mantenimiento',
            'disponible': False,
            'fecha_adquisicion': date(2023, 6, 15)
        },
        {
            'codigo': 'LAB-001',
            'nombre': 'Microscopio Óptico Leica',
            'descripcion': 'Microscopio para laboratorio de biología con objetivos 4x, 10x, 40x',
            'categoria': CategoriaEquipo.LABORATORIO,
            'marca': 'Leica',
            'modelo': 'DM500',
            'numero_serie': 'LEI50001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 5, 20)
        },
        {
            'codigo': 'HERR-001',
            'nombre': 'Kit de Herramientas Básicas',
            'descripcion': 'Juego de herramientas básicas para reparaciones menores',
            'categoria': CategoriaEquipo.HERRAMIENTAS,
            'marca': 'Stanley',
            'modelo': 'Kit Básico 65 piezas',
            'numero_serie': 'STB65001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 4, 10)
        },
        {
            'codigo': 'AUD-001',
            'nombre': 'Auriculares Sony WH-1000XM4',
            'descripcion': 'Auriculares inalámbricos con cancelación de ruido',
            'categoria': CategoriaEquipo.AUDIOVISUAL,
            'marca': 'Sony',
            'modelo': 'WH-1000XM4',
            'numero_serie': 'SNY10001',
            'estado': 'disponible',
            'disponible': True,
            'fecha_adquisicion': date(2023, 12, 1)
        }
    ]
    
    equipos_creados = 0
    for equipo_data in equipos_ejemplo:
        # Verificar si el equipo ya existe
        equipo_existente = Equipo.query.filter_by(codigo=equipo_data['codigo']).first()
        if not equipo_existente:
            equipo = Equipo(**equipo_data)
            db.session.add(equipo)
            equipos_creados += 1
    
    if equipos_creados > 0:
        db.session.commit()
        print(f"Se crearon {equipos_creados} equipos de ejemplo exitosamente.")
    else:
        print("Los equipos de ejemplo ya existen en la base de datos.")
    
    return equipos_creados

def generar_token_acceso(usuario_id, minutos_exp=30, descripcion="Acceso único de administrador", ip_origen=None):
    """Genera un token de acceso único para un usuario específico"""
    
    # Generar token aleatorio
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    
    # Calcular fecha de expiración
    expira_en = datetime.utcnow() + timedelta(minutes=minutos_exp)
    
    # Crear token en la base de datos
    nuevo_token = TokenAcceso(
        token=token,
        usuario_id=usuario_id,
        expira_en=expira_en,
        ip_origen=ip_origen,
        descripcion=descripcion
    )
    
    db.session.add(nuevo_token)
    db.session.commit()
    
    return token

def validar_token_acceso(token):
    """Valida un token de acceso y retorna el usuario asociado si es válido"""
    token_obj = TokenAcceso.query.filter_by(token=token).first()
    
    if not token_obj:
        return None, "Token no encontrado"
    
    if not token_obj.es_valido():
        if token_obj.usado:
            return None, "Token ya utilizado"
        else:
            return None, "Token expirado"
    
    return token_obj.usuario, None

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    prestamo_id = db.Column(db.Integer, db.ForeignKey('prestamos.id'))
    
    # Contenido de la notificación
    tipo = db.Column(db.Enum(TipoNotificacion), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leida = db.Column(db.Boolean, default=False)
    
    # Metadatos
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_lectura = db.Column(db.DateTime)
    urgencia = db.Column(db.String(20), default='normal')  # baja, normal, alta, critica
    icono = db.Column(db.String(50), default='bell')  # para el ícono de Font Awesome
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='notificaciones')
    prestamo = db.relationship('Prestamo', backref='notificaciones')
    
    def __repr__(self):
        return f'<Notificacion {self.tipo.value} - {self.usuario.nombre}>'
    
    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        self.leida = True
        self.fecha_lectura = datetime.utcnow()
        db.session.commit()
    
    @property
    def tiempo_transcurrido(self):
        """Retorna el tiempo transcurrido desde la creación"""
        delta = datetime.utcnow() - self.fecha_creacion
        if delta.days > 0:
            return f"Hace {delta.days} día{'s' if delta.days != 1 else ''}"
        elif delta.seconds > 3600:
            horas = delta.seconds // 3600
            return f"Hace {horas} hora{'s' if horas != 1 else ''}"
        elif delta.seconds > 60:
            minutos = delta.seconds // 60
            return f"Hace {minutos} minuto{'s' if minutos != 1 else ''}"
        else:
            return "Ahora mismo"

def crear_notificacion(usuario_id, tipo, titulo, mensaje, prestamo_id=None, urgencia='normal', icono='bell'):
    """Crea una nueva notificación para un usuario"""
    
    notificacion = Notificacion(
        usuario_id=usuario_id,
        prestamo_id=prestamo_id,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        urgencia=urgencia,
        icono=icono
    )
    
    db.session.add(notificacion)
    db.session.commit()
    
    return notificacion

def obtener_notificaciones_pendientes(usuario_id):
    """Obtiene las notificaciones no leídas de un usuario"""
    return Notificacion.query.filter_by(
        usuario_id=usuario_id,
        leida=False
    ).order_by(
        Notificacion.fecha_creacion.desc(),
        Notificacion.urgencia.desc()
    ).all()

def contar_notificaciones_pendientes(usuario_id):
    """Cuenta las notificaciones no leídas de un usuario"""
    return Notificacion.query.filter_by(
        usuario_id=usuario_id,
        leida=False
    ).count()

def notificar_nueva_solicitud_prestamo(prestamo):
    """Envía notificaciones a todos los administradores sobre una nueva solicitud"""
    from sqlalchemy import or_
    
    # Obtener todos los administradores
    administradores = Usuario.query.filter(
        Usuario.tipo_usuario == TipoUsuario.ADMIN
    ).all()
    
    for admin in administradores:
        crear_notificacion(
            usuario_id=admin.id,
            tipo=TipoNotificacion.SOLICITUD_PRESTAMO,
            titulo="Nueva Solicitud de Préstamo",
            mensaje=f"{prestamo.usuario.nombre_completo} solicita el equipo '{prestamo.equipo.nombre}' del {prestamo.fecha_inicio.strftime('%d/%m/%Y %H:%M')} al {prestamo.fecha_fin_programada.strftime('%d/%m/%Y %H:%M')}",
            prestamo_id=prestamo.id,
            urgencia='alta',
            icono='handshake'
        )

def notificar_aprobacion_prestamo(prestamo):
    """Envía notificación de aprobación al usuario"""
    crear_notificacion(
        usuario_id=prestamo.usuario_id,
        tipo=TipoNotificacion.APROBACION_PRESTAMO,
        titulo="Solicitud de Préstamo Aprobada",
        mensaje=f"Tu solicitud para el equipo '{prestamo.equipo.nombre}' ha sido aprobada. Puedes recoger el equipo a partir del {prestamo.fecha_inicio.strftime('%d/%m/%Y %H:%M')}",
        prestamo_id=prestamo.id,
        urgencia='alta',
        icono='check-circle'
    )

def notificar_rechazo_prestamo(prestamo, razon=""):
    """Envía notificación de rechazo al usuario"""
    mensaje = f"Tu solicitud para el equipo '{prestamo.equipo.nombre}' ha sido rechazada."
    if razon:
        mensaje += f" Razón: {razon}"
    
    crear_notificacion(
        usuario_id=prestamo.usuario_id,
        tipo=TipoNotificacion.RECHAZO_PRESTAMO,
        titulo="Solicitud de Préstamo Rechazada",
        mensaje=mensaje,
        prestamo_id=prestamo.id,
        urgencia='normal',
        icono='times-circle'
    )