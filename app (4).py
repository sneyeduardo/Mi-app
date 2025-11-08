from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os

# Importar modelos y formularios
from models import db, Usuario, Equipo, Prestamo, HistorialAcciones, TipoUsuario, EstadoPrestamo, CategoriaEquipo, init_db, create_admin_user, crear_equipos_ejemplo, generar_token_acceso, validar_token_acceso, TokenAcceso, Notificacion
from forms import (LoginForm, RegistrationForm, EquipoForm, PrestamoForm, AprobarPrestamoForm, 
                   DevolverEquipoForm, BuscarEquipoForm, FiltrarPrestamosForm, EditarUsuarioForm, 
                   CambiarPasswordForm, ReporteForm, ContactoForm)

# Configuración de la aplicación
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta-super-segura-aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_prestamos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db.init_app(app)
csrf = CSRFProtect(app)  # Configurar CSRF
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crear contexto de aplicación y base de datos
with app.app_context():
    init_db()
    create_admin_user()
    crear_equipos_ejemplo()

# Funciones auxiliares
def registrar_accion(accion, descripcion="", prestamo_id=None):
    """Registra una acción en el historial"""
    if current_user.is_authenticated:
        historial = HistorialAcciones(
            usuario_id=current_user.id,
            prestamo_id=prestamo_id,
            accion=accion,
            descripcion=descripcion
        )
        db.session.add(historial)

def actualizar_estados_prestamos():
    """Actualiza automáticamente el estado de préstamos vencidos"""
    prestamos_vencidos = Prestamo.query.filter(
        Prestamo.estado == EstadoPrestamo.APROBADO,
        Prestamo.fecha_fin_programada < datetime.utcnow()
    ).all()
    
    for prestamo in prestamos_vencidos:
        prestamo.estado = EstadoPrestamo.VENCIDO
        prestamo.equipo.estado = 'prestado'  # Mantener como prestado hasta devolución
    
    if prestamos_vencidos:
        db.session.commit()

# Rutas de autenticación
@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(cedula=form.cedula.data).first()
        if usuario and check_password_hash(usuario.password_hash, form.password.data):
            if usuario.activo:
                login_user(usuario, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('dashboard')
                registrar_accion('login', f'Inicio de sesión exitoso')
                db.session.commit()
                flash('¡Bienvenido al sistema!', 'success')
                return redirect(next_page)
            else:
                flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'error')
        else:
            flash('Cédula o contraseña incorrectos.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        usuario = Usuario(
            cedula=form.cedula.data,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            telefono=form.telefono.data,
            password_hash=generate_password_hash(form.password.data),
            tipo_usuario=TipoUsuario(form.tipo_usuario.data)
        )
        db.session.add(usuario)
        db.session.commit()
        
        flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    registrar_accion('logout', 'Cierre de sesión')
    db.session.commit()
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('index'))

# Rutas de acceso único de administrador
@app.route('/admin/token/generar')
@login_required
def generar_token_admin():
    """Ruta para generar tokens de acceso único (solo administradores)"""
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos para acceder a esta función"}), 403
    
    try:
        # Generar token para el administrador actual
        ip_origen = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        token = generar_token_acceso(current_user.id, 30, 'Acceso único de administrador', ip_origen)
        
        # URL completa para usar el token
        url_token = url_for('acceso_unico', token=token, _external=True)
        
        return jsonify({
            "success": True,
            "token": token,
            "url": url_token,
            "expires_in_minutes": 30,
            "message": "Token generado exitosamente. Expira en 30 minutos."
        })
        
    except Exception as e:
        return jsonify({"error": f"Error al generar token: {str(e)}"}), 500

@app.route('/admin/acceso-unico/<token>')
def acceso_unico(token):
    """Ruta para usar tokens de acceso único"""
    try:
        usuario, error = validar_token_acceso(token)
        
        if usuario:
            # Validar que sea admin
            if not usuario.es_admin():
                return f"<h1>Error</h1><p>El token no corresponde a un usuario administrador.</p>", 403
            
            # Buscar y marcar el token como usado
            token_obj = TokenAcceso.query.filter_by(token=token).first()
            if token_obj:
                token_obj.marcar_usado()
            
            # Registrar la acción
            ip_origen = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            historial = HistorialAcciones(
                usuario_id=usuario.id,
                accion='acceso_unico',
                descripcion=f'Acceso único usado desde IP: {ip_origen}'
            )
            db.session.add(historial)
            db.session.commit()
            
            # Iniciar sesión automáticamente
            login_user(usuario)
            
            # Redirigir al dashboard
            return redirect(url_for('dashboard'))
        else:
            return f"<h1>Token Inválido</h1><p>{error}</p>", 400
            
    except Exception as e:
        return f"<h1>Error</h1><p>Error interno: {str(e)}</p>", 500

@app.route('/admin/tokens')
@login_required
def listar_tokens():
    """Ruta para listar tokens de acceso únicos generados"""
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos para acceder a esta función"}), 403
    
    try:
        tokens = TokenAcceso.query.order_by(TokenAcceso.fecha_creacion.desc()).limit(50).all()
        
        tokens_data = []
        for token_obj in tokens:
            tokens_data.append({
                "id": token_obj.id,
                "token_preview": token_obj.token[:8] + "...",
                "usuario": token_obj.usuario.nombre_completo,
                "descripcion": token_obj.descripcion,
                "fecha_creacion": token_obj.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                "expira_en": token_obj.expira_en.strftime("%Y-%m-%d %H:%M:%S"),
                "usado": token_obj.usado,
                "fecha_uso": token_obj.fecha_uso.strftime("%Y-%m-%d %H:%M:%S") if token_obj.fecha_uso else None,
                "ip_origen": token_obj.ip_origen
            })
        
        return jsonify({"success": True, "tokens": tokens_data})
        
    except Exception as e:
        return jsonify({"error": f"Error al obtener tokens: {str(e)}"}), 500

@app.route('/admin/token/<int:token_id>/invalidar', methods=['POST'])
@login_required
def invalidar_token(token_id):
    """Ruta para invalidar tokens de acceso únicos"""
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos para realizar esta acción"}), 403
    
    try:
        token_obj = TokenAcceso.query.get_or_404(token_id)
        
        if token_obj.usado:
            return jsonify({"error": "El token ya ha sido utilizado"}), 400
        
        token_obj.usado = True
        token_obj.descripcion = token_obj.descripcion + ' (INVALIDADO)'
        db.session.commit()
        
        return jsonify({"success": "Token invalidado exitosamente"})
        
    except Exception as e:
        return jsonify({"error": f"Error al invalidar token: {str(e)}"}), 500

# Dashboard y rutas principales
@app.route('/dashboard')
@login_required
def dashboard():
    actualizar_estados_prestamos()
    
    # Estadísticas para el dashboard
    mis_prestamos = Prestamo.query.filter_by(usuario_id=current_user.id).count()
    prestamos_activos = Prestamo.query.filter_by(
        usuario_id=current_user.id, 
        estado=EstadoPrestamo.APROBADO
    ).count()
    prestamos_pendientes = Prestamo.query.filter_by(
        usuario_id=current_user.id, 
        estado=EstadoPrestamo.SOLICITADO
    ).count()
    
    # Estadísticas para administradores
    if current_user.puede_aprobar_prestamos():
        total_equipos = Equipo.query.count()
        equipos_disponibles = Equipo.query.filter_by(disponible=True, estado='disponible').count()
        prestamos_por_aprobar = Prestamo.query.filter_by(estado=EstadoPrestamo.SOLICITADO).count()
        prestamos_vencidos = Prestamo.query.filter_by(estado=EstadoPrestamo.VENCIDO).count()
        
        return render_template('dashboard.html', 
                             mis_prestamos=mis_prestamos,
                             prestamos_activos=prestamos_activos,
                             prestamos_pendientes=prestamos_pendientes,
                             total_equipos=total_equipos,
                             equipos_disponibles=equipos_disponibles,
                             prestamos_por_aprobar=prestamos_por_aprobar,
                             prestamos_vencidos=prestamos_vencidos)
    
    return render_template('dashboard.html', 
                         mis_prestamos=mis_prestamos,
                         prestamos_activos=prestamos_activos,
                         prestamos_pendientes=prestamos_pendientes)

# Rutas de equipos
@app.route('/equipos')
@login_required
def listar_equipos():
    """Lista todos los equipos con filtros"""
    # Obtener parámetros de filtro
    busqueda = request.args.get('busqueda', '').strip()
    tipo_filtro = request.args.get('tipo', '')  # Usado por el template actual
    categoria_filtro = request.args.get('categoria', '')
    estado_filtro = request.args.get('estado', '')
    page = request.args.get('page', 1, type=int)
    
    # Query base para equipos
    query = Equipo.query
    
    # Aplicar filtros de búsqueda
    if busqueda or request.args.get('termino'):  # Compatibilidad con ambos nombres
        termino = busqueda or request.args.get('termino')
        termino = f"%{termino}%"
        query = query.filter(
            (Equipo.nombre.ilike(termino)) |
            (Equipo.codigo.like(termino)) |
            (Equipo.descripcion.like(termino))
        )
    
    if categoria_filtro:
        try:
            categoria_enum = CategoriaEquipo(categoria_filtro)
            query = query.filter_by(categoria=categoria_enum)
        except ValueError:
            pass  # Ignorar categorías inválidas
    
    # Para compatibilidad con template existente que usa 'tipo'
    if tipo_filtro and not categoria_filtro:
        try:
            categoria_enum = CategoriaEquipo(tipo_filtro)
            query = query.filter_by(categoria=categoria_enum)
        except ValueError:
            pass
    
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    
    # Obtener equipos paginados
    equipos = query.order_by(Equipo.nombre.asc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Obtener tipos/categorías disponibles para el filtro
    tipos_disponibles = [cat.value for cat in CategoriaEquipo]
    
    return render_template('equipos/listar.html', 
                         equipos=equipos,
                         form=BuscarEquipoForm(),
                         busqueda=busqueda or request.args.get('termino', ''),
                         tipos_disponibles=tipos_disponibles,
                         tipo_filtro=tipo_filtro or categoria_filtro,
                         estado_filtro=estado_filtro)

@app.route('/equipos/nuevo', methods=['GET', 'POST'])
@login_required
def crear_equipo():
    if not current_user.es_admin():
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('listar_equipos'))
    
    form = EquipoForm()
    if form.validate_on_submit():
        equipo = Equipo(
            codigo=form.codigo.data,
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            categoria=CategoriaEquipo(form.categoria.data),
            marca=form.marca.data,
            modelo=form.modelo.data,
            numero_serie=form.numero_serie.data,
            estado=form.estado.data,
            disponible=form.disponible.data,
            fecha_adquisicion=form.fecha_adquisicion.data,
            observaciones=form.observaciones.data
        )
        db.session.add(equipo)
        registrar_accion('crear_equipo', f'Creado equipo {equipo.codigo} - {equipo.nombre}')
        db.session.commit()
        
        flash('Equipo creado exitosamente.', 'success')
        return redirect(url_for('listar_equipos'))
    
    return render_template('equipos/crear.html', form=form)

@app.route('/equipos/<int:equipo_id>')
@login_required
def ver_equipo(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    prestamos = Prestamo.query.filter_by(equipo_id=equipo_id).order_by(Prestamo.fecha_solicitud.desc()).limit(5).all()
    return render_template('equipos/ver.html', equipo=equipo, prestamos=prestamos)

@app.route('/equipos/<int:equipo_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_equipo(equipo_id):
    if not current_user.es_admin():
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('ver_equipo', equipo_id=equipo_id))
    
    equipo = Equipo.query.get_or_404(equipo_id)
    form = EquipoForm(equipo_original=equipo, obj=equipo)
    
    if form.validate_on_submit():
        form.populate_obj(equipo)
        equipo.categoria = CategoriaEquipo(form.categoria.data)
        registrar_accion('editar_equipo', f'Editado equipo {equipo.codigo} - {equipo.nombre}')
        db.session.commit()
        
        flash('Equipo actualizado exitosamente.', 'success')
        return redirect(url_for('ver_equipo', equipo_id=equipo_id))
    
    return render_template('equipos/editar.html', form=form, equipo=equipo)

# Rutas de préstamos
@app.route('/prestamos')
@login_required
def listar_prestamos():
    """Página principal de préstamos que muestra equipos disponibles"""
    # Obtener parámetros de filtro
    busqueda = request.args.get('busqueda', '').strip()
    categoria_filtro = request.args.get('categoria', '')
    estado_filtro = request.args.get('estado', '')
    
    # Query base para equipos
    query = Equipo.query
    
    # Aplicar filtros de búsqueda
    if busqueda:
        query = query.filter(
            (Equipo.nombre.ilike(f'%{busqueda}%')) |
            (Equipo.descripcion.ilike(f'%{busqueda}%')) |
            (Equipo.codigo.ilike(f'%{busqueda}%'))
        )
    
    if categoria_filtro:
        try:
            categoria_enum = CategoriaEquipo(categoria_filtro)
            query = query.filter_by(categoria=categoria_enum)
        except ValueError:
            pass  # Ignorar categorías inválidas
    
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    
    # Obtener equipos ordenados
    equipos = query.order_by(Equipo.nombre.asc()).all()
    
    # Calcular estadísticas
    equipos_totales = Equipo.query.count()
    equipos_disponibles = Equipo.query.filter_by(estado='disponible').count()
    equipos_prestados = Equipo.query.filter_by(estado='prestado').count()
    equipos_mantenimiento = Equipo.query.filter_by(estado='mantenimiento').count()
    
    # Obtener préstamos activos del usuario actual
    prestamos_usuario = Prestamo.query.filter_by(usuario_id=current_user.id).filter(
        Prestamo.estado.in_([EstadoPrestamo.SOLICITADO, EstadoPrestamo.APROBADO])
    ).order_by(Prestamo.fecha_solicitud.desc()).all()
    
    # Obtener categorías disponibles para el filtro
    categorias_disponibles = list(CategoriaEquipo)
    
    return render_template('prestamos/listar.html', 
                         equipos=equipos,
                         equipos_totales=equipos_totales,
                         equipos_disponibles=equipos_disponibles,
                         equipos_prestados=equipos_prestados,
                         equipos_mantenimiento=equipos_mantenimiento,
                         prestamos_usuario=prestamos_usuario,
                         categorias_disponibles=categorias_disponibles,
                         busqueda=busqueda,
                         categoria_filtro=categoria_filtro,
                         estado_filtro=estado_filtro)

@app.route('/prestamos/solicitar', methods=['GET', 'POST'])
@login_required
def solicitar_prestamo():
    form = PrestamoForm()
    if form.validate_on_submit():
        # Verificar que el equipo esté disponible
        equipo = Equipo.query.get(form.equipo_id.data)
        if not equipo or not equipo.esta_disponible():
            flash('El equipo seleccionado no está disponible.', 'error')
            return redirect(url_for('solicitar_prestamo'))
        
        prestamo = Prestamo(
            usuario_id=current_user.id,
            equipo_id=form.equipo_id.data,
            fecha_inicio=form.fecha_inicio.data,
            fecha_fin_programada=form.fecha_fin_programada.data,
            motivo=form.motivo.data,
            observaciones_usuario=form.observaciones_usuario.data
        )
        
        db.session.add(prestamo)
        registrar_accion('solicitar_prestamo', 
                        f'Solicitado préstamo del equipo {equipo.codigo} - {equipo.nombre}',
                        prestamo.id)
        db.session.commit()
        
        # Enviar notificación a los administradores usando la función correcta
        try:
            from models import notificar_nueva_solicitud_prestamo
            notificar_nueva_solicitud_prestamo(prestamo)
        except ImportError:
            # Si no existe la función, crear notificación manualmente
            administradores = Usuario.query.filter_by(tipo_usuario=TipoUsuario.ADMIN).all()
            for admin in administradores:
                notificacion = Notificacion(
                    usuario_id=admin.id,
                    prestamo_id=prestamo.id,
                    tipo=TipoNotificacion.SOLICITUD_PRESTAMO,
                    titulo="Nueva Solicitud de Préstamo",
                    mensaje=f"{current_user.nombre_completo} solicita el equipo '{equipo.nombre}' del {prestamo.fecha_inicio.strftime('%d/%m/%Y %H:%M')} al {prestamo.fecha_fin_programada.strftime('%d/%m/%Y %H:%M')}",
                    urgencia='alta',
                    icono='bell'
                )
                db.session.add(notificacion)
            db.session.commit()
        
        flash('Solicitud de préstamo enviada exitosamente.', 'success')
        return redirect(url_for('listar_prestamos'))
    
    return render_template('solicitar.html', form=form)

@app.route('/prestamos/<int:prestamo_id>')
@login_required
def ver_prestamo(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    # Verificar permisos
    if not current_user.puede_aprobar_prestamos() and prestamo.usuario_id != current_user.id:
        flash('No tienes permisos para ver este préstamo.', 'error')
        return redirect(url_for('listar_prestamos'))
    
    return render_template('prestamos/ver.html', prestamo=prestamo)

@app.route('/prestamos/<int:prestamo_id>/aprobar', methods=['GET', 'POST'])
@login_required
def aprobar_prestamo(prestamo_id):
    if not current_user.puede_aprobar_prestamos():
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('listar_prestamos'))
    
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    if prestamo.estado != EstadoPrestamo.SOLICITADO:
        flash('Este préstamo ya ha sido procesado.', 'warning')
        return redirect(url_for('ver_prestamo', prestamo_id=prestamo_id))
    
    form = AprobarPrestamoForm()
    if form.validate_on_submit():
        if form.accion.data == 'aprobar':
            if not prestamo.equipo.esta_disponible():
                flash('El equipo ya no está disponible.', 'error')
                return redirect(url_for('ver_prestamo', prestamo_id=prestamo_id))
            
            prestamo.estado = EstadoPrestamo.APROBADO
            prestamo.equipo.estado = 'prestado'
            prestamo.equipo.disponible = False
            accion_desc = 'Préstamo aprobado'
        else:
            prestamo.estado = EstadoPrestamo.RECHAZADO
            accion_desc = 'Préstamo rechazado'
        
        prestamo.aprobado_por_id = current_user.id
        prestamo.fecha_aprobacion = datetime.utcnow()
        prestamo.observaciones_admin = form.observaciones_admin.data
        prestamo.estado_equipo_entrega = form.estado_equipo_entrega.data
        
        registrar_accion('aprobar_prestamo', accion_desc, prestamo_id)
        db.session.commit()
        
        # Enviar notificación al usuario
        try:
            if form.accion.data == 'aprobar':
                from models import notificar_aprobacion_prestamo
                notificar_aprobacion_prestamo(prestamo)
            else:
                from models import notificar_rechazo_prestamo
                notificar_rechazo_prestamo(prestamo, form.observaciones_admin.data)
        except ImportError:
            # Si no existen las funciones, crear notificación manualmente
            tipo_notificacion = TipoNotificacion.APROBACION_PRESTAMO if form.accion.data == 'aprobar' else TipoNotificacion.RECHAZO_PRESTAMO
            titulo = "Préstamo Aprobado" if form.accion.data == 'aprobar' else "Préstamo Rechazado"
            mensaje = f"Tu solicitud de préstamo del equipo '{prestamo.equipo.nombre}' ha sido {form.accion.data}."
            if form.observaciones_admin.data:
                mensaje += f"\n\nObservaciones: {form.observaciones_admin.data}"
            
            notificacion = Notificacion(
                usuario_id=prestamo.usuario_id,
                prestamo_id=prestamo.id,
                tipo=tipo_notificacion,
                titulo=titulo,
                mensaje=mensaje,
                urgencia='alta',
                icono='check-circle' if form.accion.data == 'aprobar' else 'times-circle'
            )
            db.session.add(notificacion)
            db.session.commit()
        
        flash(f'Préstamo {form.accion.data} exitosamente.', 'success')
        return redirect(url_for('ver_prestamo', prestamo_id=prestamo_id))
    
    return render_template('prestamos/aprobar.html', form=form, prestamo=prestamo)

@app.route('/prestamos/<int:prestamo_id>/devolver', methods=['GET', 'POST'])
@login_required
def devolver_equipo(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    # Verificar permisos
    if not current_user.puede_aprobar_prestamos() and prestamo.usuario_id != current_user.id:
        flash('No tienes permisos para realizar esta acción.', 'error')
        return redirect(url_for('listar_prestamos'))
    
    if not prestamo.puede_ser_devuelto():
        flash('Este préstamo no puede ser devuelto en su estado actual.', 'warning')
        return redirect(url_for('ver_prestamo', prestamo_id=prestamo_id))
    
    form = DevolverEquipoForm()
    if form.validate_on_submit():
        prestamo.estado = EstadoPrestamo.DEVUELTO
        prestamo.fecha_devolucion = datetime.utcnow()
        prestamo.estado_equipo_devolucion = form.estado_equipo_devolucion.data
        prestamo.observaciones_admin = form.observaciones_devolucion.data
        
        # Restaurar disponibilidad del equipo
        prestamo.equipo.estado = 'disponible'
        prestamo.equipo.disponible = True
        
        registrar_accion('devolver_equipo', 
                        f'Devuelto equipo {prestamo.equipo.codigo} - {prestamo.equipo.nombre}',
                        prestamo_id)
        db.session.commit()
        
        flash('Equipo devuelto exitosamente.', 'success')
        return redirect(url_for('ver_prestamo', prestamo_id=prestamo_id))
    
    return render_template('prestamos/devolver.html', form=form, prestamo=prestamo)

# Rutas de administración
@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.es_admin():
        flash('No tienes permisos para acceder al panel de administración.', 'error')
        return redirect(url_for('dashboard'))
    
    # Estadísticas generales
    total_usuarios = Usuario.query.count()
    total_equipos = Equipo.query.count()
    total_prestamos = Prestamo.query.count()
    prestamos_activos = Prestamo.query.filter_by(estado=EstadoPrestamo.APROBADO).count()
    prestamos_vencidos = Prestamo.query.filter_by(estado=EstadoPrestamo.VENCIDO).count()
    equipos_disponibles = Equipo.query.filter_by(disponible=True, estado='disponible').count()
    prestamos_por_aprobar = Prestamo.query.filter_by(estado=EstadoPrestamo.SOLICITADO).count()
    
    return render_template('admin/admin_panel.html',
                         total_usuarios=total_usuarios,
                         total_equipos=total_equipos,
                         total_prestamos=total_prestamos,
                         prestamos_activos=prestamos_activos,
                         prestamos_vencidos=prestamos_vencidos,
                         equipos_disponibles=equipos_disponibles,
                         prestamos_por_aprobar=prestamos_por_aprobar,
                         csrf_token=generate_csrf())

@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.es_admin():
        flash('No tienes permisos para acceder a esta función.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    
    # Aplicar filtros
    query = Usuario.query
    
    if request.args.get('buscar'):
        termino = f"%{request.args.get('buscar')}%"
        query = query.filter(
            (Usuario.nombre.like(termino)) |
            (Usuario.apellido.like(termino)) |
            (Usuario.cedula.like(termino))
        )
    
    if request.args.get('tipo'):
        query = query.filter_by(tipo_usuario=TipoUsuario(request.args.get('tipo')))
    
    if request.args.get('estado') == 'activo':
        query = query.filter_by(activo=True)
    elif request.args.get('estado') == 'inactivo':
        query = query.filter_by(activo=False)
    
    usuarios = query.order_by(Usuario.fecha_registro.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/admin_usuarios.html', 
                         usuarios=usuarios,
                         csrf_token=generate_csrf())

@app.route('/admin/equipos')
@login_required
def admin_equipos():
    if not current_user.es_admin():
        flash('No tienes permisos para acceder a esta función.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    
    # Aplicar filtros
    query = Equipo.query
    
    if request.args.get('buscar'):
        termino = f"%{request.args.get('buscar')}%"
        query = query.filter(
            (Equipo.nombre.like(termino)) |
            (Equipo.codigo.like(termino)) |
            (Equipo.descripcion.like(termino))
        )
    
    if request.args.get('categoria'):
        query = query.filter_by(categoria=CategoriaEquipo(request.args.get('categoria')))
    
    if request.args.get('estado'):
        query = query.filter_by(estado=request.args.get('estado'))
    
    if request.args.get('disponible') == 'true':
        query = query.filter_by(disponible=True)
    elif request.args.get('disponible') == 'false':
        query = query.filter_by(disponible=False)
    
    equipos = query.order_by(Equipo.fecha_registro.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('admin/admin_equipos.html', 
                         equipos=equipos,
                         csrf_token=generate_csrf())

@app.route('/admin/prestamos')
@login_required
def admin_prestamos():
    if not current_user.es_admin():
        flash('No tienes permisos para acceder a esta función.', 'error')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    
    # Aplicar filtros
    query = Prestamo.query
    
    if request.args.get('buscar'):
        termino = f"%{request.args.get('buscar')}%"
        query = query.join(Usuario).join(Equipo).filter(
            (Usuario.nombre.like(termino)) |
            (Usuario.apellido.like(termino)) |
            (Equipo.nombre.like(termino)) |
            (Equipo.codigo.like(termino))
        )
    
    if request.args.get('estado'):
        query = query.filter_by(estado=EstadoPrestamo(request.args.get('estado')))
    
    if request.args.get('fecha_desde'):
        fecha_desde = datetime.strptime(request.args.get('fecha_desde'), '%Y-%m-%d')
        query = query.filter(Prestamo.fecha_solicitud >= fecha_desde)
    
    if request.args.get('fecha_hasta'):
        fecha_hasta = datetime.strptime(request.args.get('fecha_hasta'), '%Y-%m-%d')
        query = query.filter(Prestamo.fecha_solicitud <= fecha_hasta)
    
    if request.args.get('usuario'):
        termino = f"%{request.args.get('usuario')}%"
        query = query.join(Usuario).filter(
            (Usuario.nombre.like(termino)) |
            (Usuario.apellido.like(termino)) |
            (Usuario.cedula.like(termino))
        )
    
    prestamos = query.order_by(Prestamo.fecha_solicitud.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    prestamos_por_aprobar = Prestamo.query.filter_by(estado=EstadoPrestamo.SOLICITADO).count()
    prestamos_vencidos = Prestamo.query.filter_by(estado=EstadoPrestamo.VENCIDO).count()
    
    return render_template('admin/admin_prestamos.html', 
                         prestamos=prestamos,
                         prestamos_por_aprobar=prestamos_por_aprobar,
                         prestamos_vencidos=prestamos_vencidos,
                         csrf_token=generate_csrf())

@app.route('/admin/reportes')
@login_required
def admin_reportes():
    if not current_user.es_admin():
        flash('No tienes permisos para acceder a esta función.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/admin_reportes.html',
                         csrf_token=generate_csrf())

@app.route('/admin/configuracion')
@login_required
def admin_configuracion():
    if not current_user.es_admin():
        flash('No tienes permisos para acceder a esta función.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/admin_configuracion.html',
                         csrf_token=generate_csrf())

# Rutas adicionales para funcionalidades administrativas
@app.route('/admin/usuario/<int:usuario_id>/toggle', methods=['POST'])
@login_required
def toggle_usuario(usuario_id):
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        if usuario.id == current_user.id:
            return jsonify({"error": "No puedes desactivar tu propia cuenta"}), 400
        
        usuario.activo = not usuario.activo
        db.session.commit()
        
        return jsonify({"success": f"Usuario {'activado' if usuario.activo else 'desactivado'} exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/usuario/<int:usuario_id>/reset-password', methods=['POST'])
@login_required
def reset_password(usuario_id):
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        usuario = Usuario.query.get_or_404(usuario_id)
        from werkzeug.security import generate_password_hash
        nueva_password = 'password123'  # Password temporal
        usuario.password_hash = generate_password_hash(nueva_password)
        db.session.commit()
        
        return jsonify({"success": "Contraseña reseteada a 'password123'"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/usuario/<int:usuario_id>/ver')
@login_required
def ver_usuario(usuario_id):
    if not current_user.es_admin():
        abort(403)
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Obtener información adicional del usuario
    prestamos_activos = Prestamo.query.filter_by(usuario_id=usuario_id, devuelto=False).count()
    prestamos_totales = Prestamo.query.filter_by(usuario_id=usuario_id).count()
    
    return render_template('admin/ver_usuario.html', 
                         usuario=usuario, 
                         prestamos_activos=prestamos_activos,
                         prestamos_totales=prestamos_totales,
                         csrf_token=generate_csrf())

@app.route('/admin/equipo/<int:equipo_id>/eliminar', methods=['POST'])
@login_required
def eliminar_equipo(equipo_id):
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        equipo = Equipo.query.get_or_404(equipo_id)
        
        # Verificar que no tenga préstamos activos
        prestamos_activos = Prestamo.query.filter_by(
            equipo_id=equipo_id, 
            estado=EstadoPrestamo.APROBADO
        ).count()
        
        if prestamos_activos > 0:
            return jsonify({"error": "No se puede eliminar un equipo con préstamos activos"}), 400
        
        db.session.delete(equipo)
        db.session.commit()
        
        return jsonify({"success": "Equipo eliminado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/equipo/<int:equipo_id>/estado', methods=['POST'])
@login_required
def cambiar_estado_equipo(equipo_id):
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in ['disponible', 'prestado', 'mantenimiento', 'dañado']:
            return jsonify({"error": "Estado no válido"}), 400
        
        equipo = Equipo.query.get_or_404(equipo_id)
        equipo.estado = nuevo_estado
        
        if nuevo_estado == 'disponible':
            equipo.disponible = True
        else:
            equipo.disponible = False
        
        db.session.commit()
        
        return jsonify({"success": f"Estado cambiado a {nuevo_estado}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/prestamo/<int:prestamo_id>/cancelar', methods=['POST'])
@login_required
def cancelar_prestamo(prestamo_id):
    if not current_user.es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        prestamo = Prestamo.query.get_or_404(prestamo_id)
        
        if prestamo.estado == EstadoPrestamo.DEVUELTO:
            return jsonify({"error": "No se puede cancelar un préstamo ya devuelto"}), 400
        
        # Si estaba aprobado, liberar el equipo
        if prestamo.estado == EstadoPrestamo.APROBADO:
            prestamo.equipo.estado = 'disponible'
            prestamo.equipo.disponible = True
        
        prestamo.estado = EstadoPrestamo.RECHAZADO
        prestamo.observaciones_admin = 'Préstamo cancelado por el administrador'
        db.session.commit()
        
        return jsonify({"success": "Préstamo cancelado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================================
# RUTAS PARA EL SISTEMA DE NOTIFICACIONES
# ========================================

@app.route('/api/notificaciones')
@login_required
def obtener_notificaciones():
    """Obtiene las notificaciones del usuario actual"""
    try:
        from models import obtener_notificaciones_pendientes, contar_notificaciones_pendientes
        
        notificaciones = obtener_notificaciones_pendientes(current_user.id)
        conteo = contar_notificaciones_pendientes(current_user.id)
        
        return jsonify({
            'notificaciones': [
                {
                    'id': n.id,
                    'titulo': n.titulo,
                    'mensaje': n.mensaje,
                    'tiempo': getattr(n, 'tiempo_transcurrido', 'Hace un momento'),
                    'urgencia': n.urgencia,
                    'icono': n.icono,
                    'prestamo_id': n.prestamo_id
                } for n in notificaciones
            ],
            'conteo': conteo
        })
    except ImportError:
        # Si las funciones no existen, devolver respuesta vacía
        return jsonify({'notificaciones': [], 'conteo': 0})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/<int:notificacion_id>/marcar-leida', methods=['POST'])
@login_required
def marcar_notificacion_leida(notificacion_id):
    """Marca una notificación como leída"""
    try:
        from models import Notificacion
        
        notificacion = Notificacion.query.filter_by(
            id=notificacion_id,
            usuario_id=current_user.id
        ).first()
        
        if not notificacion:
            return jsonify({'error': 'Notificación no encontrada'}), 404
        
        notificacion.leida = True
        notificacion.fecha_lectura = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notificaciones/marcar-todas-leidas', methods=['POST'])
@login_required
def marcar_todas_notificaciones_leidas():
    """Marca todas las notificaciones como leídas"""
    try:
        from models import Notificacion
        
        Notificacion.query.filter_by(
            usuario_id=current_user.id,
            leida=False
        ).update({'leida': True, 'fecha_lectura': datetime.utcnow()})
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Contexto global para templates
@app.context_processor
def inject_global_vars():
    """Injecta variables globales en todas las templates"""
    try:
        notificaciones_conteo = 0
        if current_user.is_authenticated:
            # Contar notificaciones de forma segura
            notificaciones_conteo = Notificacion.query.filter_by(
                usuario_id=current_user.id,
                leida=False
            ).count()
    except Exception:
        # En caso de error, mostrar 0 notificaciones
        notificaciones_conteo = 0
    
    return {
        'now': datetime.utcnow(),
        'TipoUsuario': TipoUsuario,
        'EstadoPrestamo': EstadoPrestamo,
        'CategoriaEquipo': CategoriaEquipo,
        'notificaciones_conteo': notificaciones_conteo
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)