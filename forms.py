from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateTimeField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo, Optional
from wtforms.widgets import TextArea
from datetime import datetime, timedelta
from models import Usuario, Equipo, TipoUsuario, CategoriaEquipo, EstadoPrestamo

class LoginForm(FlaskForm):
    cedula = StringField('Cédula', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    cedula = StringField('Cédula', validators=[DataRequired(), Length(min=5, max=20)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=100)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    password = PasswordField('Contraseña', validators=[
        DataRequired(), 
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(), 
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    tipo_usuario = SelectField('Tipo de Usuario', choices=[
        (TipoUsuario.ESTUDIANTE.value, 'Estudiante'),
        (TipoUsuario.PROFESOR.value, 'Profesor')
    ], default=TipoUsuario.ESTUDIANTE.value)

    def validate_cedula(self, cedula):
        usuario = Usuario.query.filter_by(cedula=cedula.data).first()
        if usuario:
            raise ValidationError('Esta cédula ya está registrada. Use una cédula diferente.')
    
    submit = SubmitField('Registrarse')


class EquipoForm(FlaskForm):
    codigo = StringField('Código del Equipo', validators=[DataRequired(), Length(min=1, max=50)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional()], widget=TextArea())
    categoria = SelectField('Categoría', choices=[
        (CategoriaEquipo.COMPUTADORA.value, 'Computadora'),
        (CategoriaEquipo.PROYECTOR.value, 'Proyector'),
        (CategoriaEquipo.LABORATORIO.value, 'Equipo de Laboratorio'),
        (CategoriaEquipo.AUDIOVISUAL.value, 'Audiovisual'),
        (CategoriaEquipo.HERRAMIENTAS.value, 'Herramientas'),
        (CategoriaEquipo.OTROS.value, 'Otros')
    ], validators=[DataRequired()])
    marca = StringField('Marca', validators=[Optional(), Length(max=50)])
    modelo = StringField('Modelo', validators=[Optional(), Length(max=50)])
    numero_serie = StringField('Número de Serie', validators=[Optional(), Length(max=100)])
    estado = SelectField('Estado', choices=[
        ('disponible', 'Disponible'),
        ('mantenimiento', 'En Mantenimiento'),
        ('dañado', 'Dañado')
    ], default='disponible')
    disponible = BooleanField('Disponible para préstamo', default=True)
    fecha_adquisicion = DateField('Fecha de Adquisición', validators=[Optional()])
    observaciones = TextAreaField('Observaciones', validators=[Optional()], widget=TextArea())

    def __init__(self, equipo_original=None, *args, **kwargs):
        super(EquipoForm, self).__init__(*args, **kwargs)
        self.equipo_original = equipo_original

    def validate_codigo(self, codigo):
        equipo = Equipo.query.filter_by(codigo=codigo.data).first()
        if equipo and (not self.equipo_original or equipo.id != self.equipo_original.id):
            raise ValidationError('Este código ya está en uso. Use un código diferente.')
    
    submit = SubmitField('Guardar Equipo')


class PrestamoForm(FlaskForm):
    equipo_id = SelectField('Equipo', coerce=int, validators=[DataRequired()])
    fecha_inicio = DateTimeField('Fecha y Hora de Inicio', 
                                validators=[DataRequired()], 
                                format='%Y-%m-%d %H:%M')
    fecha_fin_programada = DateTimeField('Fecha y Hora de Fin', 
                                        validators=[DataRequired()], 
                                        format='%Y-%m-%d %H:%M')
    motivo = TextAreaField('Motivo del Préstamo', 
                          validators=[DataRequired(), Length(min=10, max=500)], 
                          widget=TextArea())
    observaciones_usuario = TextAreaField('Observaciones Adicionales', 
                                         validators=[Optional()], 
                                         widget=TextArea())

    def __init__(self, *args, **kwargs):
        super(PrestamoForm, self).__init__(*args, **kwargs)
        # Cargar solo equipos disponibles
        self.equipo_id.choices = [
            (equipo.id, f"{equipo.codigo} - {equipo.nombre}")
            for equipo in Equipo.query.filter_by(disponible=True, estado='disponible').all()
        ]
        if not self.equipo_id.choices:
            self.equipo_id.choices = [(0, 'No hay equipos disponibles')]

    def validate_fecha_inicio(self, fecha_inicio):
        if fecha_inicio.data <= datetime.now():
            raise ValidationError('La fecha de inicio debe ser posterior a la fecha actual.')

    def validate_fecha_fin_programada(self, fecha_fin_programada):
        if hasattr(self, 'fecha_inicio') and self.fecha_inicio.data:
            if fecha_fin_programada.data <= self.fecha_inicio.data:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
            # Validar que el préstamo no sea mayor a 30 días
            duracion = fecha_fin_programada.data - self.fecha_inicio.data
            if duracion.days > 30:
                raise ValidationError('El préstamo no puede ser mayor a 30 días.')
    
    submit = SubmitField('Solicitar Préstamo')


class AprobarPrestamoForm(FlaskForm):
    accion = SelectField('Acción', choices=[
        ('aprobar', 'Aprobar'),
        ('rechazar', 'Rechazar')
    ], validators=[DataRequired()])
    observaciones_admin = TextAreaField('Observaciones del Administrador', 
                                       validators=[Optional()], 
                                       widget=TextArea())
    estado_equipo_entrega = TextAreaField('Estado del Equipo al Entregarlo', 
                                         validators=[Optional()], 
                                         widget=TextArea())
    
    submit = SubmitField('Procesar Solicitud')


class DevolverEquipoForm(FlaskForm):
    estado_equipo_devolucion = TextAreaField('Estado del Equipo al Devolverlo', 
                                            validators=[DataRequired(), Length(min=5, max=500)], 
                                            widget=TextArea())
    observaciones_devolucion = TextAreaField('Observaciones de la Devolución', 
                                            validators=[Optional()], 
                                            widget=TextArea())
    
    submit = SubmitField('Registrar Devolución')


class BuscarEquipoForm(FlaskForm):
    termino = StringField('Buscar equipo', validators=[Optional()])
    categoria = SelectField('Categoría', choices=[
        ('', 'Todas las categorías'),
        (CategoriaEquipo.COMPUTADORA.value, 'Computadora'),
        (CategoriaEquipo.PROYECTOR.value, 'Proyector'),
        (CategoriaEquipo.LABORATORIO.value, 'Equipo de Laboratorio'),
        (CategoriaEquipo.AUDIOVISUAL.value, 'Audiovisual'),
        (CategoriaEquipo.HERRAMIENTAS.value, 'Herramientas'),
        (CategoriaEquipo.OTROS.value, 'Otros')
    ], default='')
    estado = SelectField('Estado', choices=[
        ('', 'Todos los estados'),
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('mantenimiento', 'En Mantenimiento'),
        ('dañado', 'Dañado')
    ], default='')
    
    submit = SubmitField('Buscar')


class FiltrarPrestamosForm(FlaskForm):
    estado = SelectField('Estado', choices=[
        ('', 'Todos los estados'),
        (EstadoPrestamo.SOLICITADO.value, 'Solicitado'),
        (EstadoPrestamo.APROBADO.value, 'Aprobado'),
        (EstadoPrestamo.RECHAZADO.value, 'Rechazado'),
        (EstadoPrestamo.DEVUELTO.value, 'Devuelto'),
        (EstadoPrestamo.VENCIDO.value, 'Vencido')
    ], default='')
    fecha_desde = DateField('Desde', validators=[Optional()])
    fecha_hasta = DateField('Hasta', validators=[Optional()])
    usuario = StringField('Usuario (nombre o cédula)', validators=[Optional()])
    
    submit = SubmitField('Filtrar')


class EditarUsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    tipo_usuario = SelectField('Tipo de Usuario', choices=[
        (TipoUsuario.ESTUDIANTE.value, 'Estudiante'),
        (TipoUsuario.PROFESOR.value, 'Profesor'),
        (TipoUsuario.ADMIN.value, 'Administrador')
    ])
    activo = BooleanField('Usuario Activo', default=True)

    def __init__(self, usuario_original=None, *args, **kwargs):
        super(EditarUsuarioForm, self).__init__(*args, **kwargs)
        self.usuario_original = usuario_original

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario and (not self.usuario_original or usuario.id != self.usuario_original.id):
            raise ValidationError('Este email ya está registrado. Use un email diferente.')
    
    submit = SubmitField('Guardar Cambios')


class CambiarPasswordForm(FlaskForm):
    password_actual = PasswordField('Contraseña Actual', validators=[DataRequired()])
    password_nueva = PasswordField('Nueva Contraseña', validators=[
        DataRequired(), 
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password_nueva2 = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(), 
        EqualTo('password_nueva', message='Las contraseñas deben coincidir')
    ])
    
    submit = SubmitField('Cambiar Contraseña')


class ReporteForm(FlaskForm):
    tipo_reporte = SelectField('Tipo de Reporte', choices=[
        ('equipos', 'Equipos'),
        ('prestamos', 'Préstamos'),
        ('usuarios', 'Usuarios'),
        ('estadisticas', 'Estadísticas Generales')
    ], validators=[DataRequired()])
    fecha_desde = DateField('Desde', validators=[Optional()])
    fecha_hasta = DateField('Hasta', validators=[Optional()])
    formato = SelectField('Formato', choices=[
        ('html', 'Ver en Pantalla'),
        ('pdf', 'Descargar PDF'),
        ('excel', 'Descargar Excel')
    ], default='html')
    
    submit = SubmitField('Generar Reporte')


class ContactoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    asunto = StringField('Asunto', validators=[DataRequired(), Length(min=5, max=200)])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10, max=1000)], widget=TextArea())
    
    submit = SubmitField('Enviar Mensaje')
