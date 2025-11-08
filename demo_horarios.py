#!/usr/bin/env python3
"""
Script para agregar horarios de demostración al sistema integrado.
"""

from app import app
from models import db, Usuario, Horario, TipoUsuario

def crear_horarios_demo():
    """Crear horarios de demostración"""
    
    # Obtener profesores
    profesores = Usuario.query.filter_by(tipo_usuario=TipoUsuario.PROFESOR).all()
    
    if not profesores:
        print("⚠ No hay profesores en el sistema. Creando horarios para administrador...")
        admin = Usuario.query.filter_by(tipo_usuario=TipoUsuario.ADMIN).first()
        if admin:
            profesores = [admin]
    
    if not profesores:
        print("❌ No hay usuarios que puedan tener horarios")
        return
    
    horarios_demo = [
        # Profesor 1 - María González
        {
            'profesor': profesores[0] if len(profesores) > 0 else profesores[0],
            'materia': 'Programación I',
            'dia_semana': 'Lunes',
            'hora_inicio': '08:00',
            'hora_fin': '10:00',
            'aula': 'LAB-1'
        },
        {
            'profesor': profesores[0] if len(profesores) > 0 else profesores[0],
            'materia': 'Programación I',
            'dia_semana': 'Miércoles',
            'hora_inicio': '08:00',
            'hora_fin': '10:00',
            'aula': 'LAB-1'
        },
        {
            'profesor': profesores[0] if len(profesores) > 0 else profesores[0],
            'materia': 'Bases de Datos',
            'dia_semana': 'Martes',
            'hora_inicio': '14:00',
            'hora_fin': '16:00',
            'aula': 'A-201'
        },
        # Profesor 2 - Carlos Rodríguez (si existe)
        {
            'profesor': profesores[1] if len(profesores) > 1 else profesores[0],
            'materia': 'Matemática Discreta',
            'dia_semana': 'Lunes',
            'hora_inicio': '10:00',
            'hora_fin': '12:00',
            'aula': 'A-101'
        },
        {
            'profesor': profesores[1] if len(profesores) > 1 else profesores[0],
            'materia': 'Algoritmos',
            'dia_semana': 'Viernes',
            'hora_inicio': '08:00',
            'hora_fin': '10:00',
            'aula': 'LAB-2'
        },
        {
            'profesor': profesores[1] if len(profesores) > 1 else profesores[0],
            'materia': 'Redes de Computadoras',
            'dia_semana': 'Jueves',
            'hora_inicio': '16:00',
            'hora_fin': '18:00',
            'aula': 'LAB-3'
        },
        # Horarios adicionales para crear algunos conflictos intencionales
        {
            'profesor': profesores[0] if len(profesores) > 0 else profesores[0],
            'materia': 'Tutoría Académica',
            'dia_semana': 'Viernes',
            'hora_inicio': '09:00',  # Se solapa con Algoritmos del otro profesor
            'hora_fin': '11:00',
            'aula': 'LAB-2'  # Mismo aula - conflicto de aula
        },
        # Horarios de fin de semana
        {
            'profesor': profesores[1] if len(profesores) > 1 else profesores[0],
            'materia': 'Seminario de Investigación',
            'dia_semana': 'Sábado',
            'hora_inicio': '09:00',
            'hora_fin': '12:00',
            'aula': 'Auditorio'
        }
    ]
    
    horarios_creados = []
    conflictos_detectados = []
    
    for datos_horario in horarios_demo:
        # Verificar si ya existe un horario similar
        horario_existente = Horario.query.filter_by(
            profesor_id=datos_horario['profesor'].id,
            materia=datos_horario['materia'],
            dia_semana=datos_horario['dia_semana']
        ).first()
        
        if not horario_existente:
            # Verificar conflictos antes de crear
            conflicto = False
            
            # Verificar conflictos de aula
            horarios_aula = Horario.query.filter_by(
                dia_semana=datos_horario['dia_semana'],
                aula=datos_horario['aula']
            ).all()
            
            for h in horarios_aula:
                if (datos_horario['hora_inicio'] < h.hora_fin and 
                    datos_horario['hora_fin'] > h.hora_inicio):
                    conflictos_detectados.append({
                        'tipo': 'aula',
                        'materia_nueva': datos_horario['materia'],
                        'materia_existente': h.materia,
                        'aula': datos_horario['aula'],
                        'dia': datos_horario['dia_semana']
                    })
                    conflicto = True
            
            # Verificar conflictos de profesor
            horarios_profesor = Horario.query.filter_by(
                profesor_id=datos_horario['profesor'].id,
                dia_semana=datos_horario['dia_semana']
            ).all()
            
            for h in horarios_profesor:
                if (datos_horario['hora_inicio'] < h.hora_fin and 
                    datos_horario['hora_fin'] > h.hora_inicio):
                    conflictos_detectados.append({
                        'tipo': 'profesor',
                        'materia_nueva': datos_horario['materia'],
                        'materia_existente': h.materia,
                        'profesor': datos_horario['profesor'].nombre_completo,
                        'dia': datos_horario['dia_semana']
                    })
                    conflicto = True
            
            # Crear el horario (incluso si hay conflicto para demostración)
            horario = Horario(
                materia=datos_horario['materia'],
                dia_semana=datos_horario['dia_semana'],
                hora_inicio=datos_horario['hora_inicio'],
                hora_fin=datos_horario['hora_fin'],
                aula=datos_horario['aula'],
                profesor_id=datos_horario['profesor'].id
            )
            db.session.add(horario)
            horarios_creados.append(horario)
    
    db.session.commit()
    
    print(f"✓ Creados {len(horarios_creados)} horarios de demostración")
    
    if conflictos_detectados:
        print(f"⚠ Se detectaron {len(conflictos_detectados)} conflictos (intencionales para demostración):")
        for conflicto in conflictos_detectados:
            if conflicto['tipo'] == 'aula':
                print(f"   - Conflicto de aula {conflicto['aula']}: {conflicto['materia_nueva']} vs {conflicto['materia_existente']}")
            else:
                print(f"   - Conflicto de profesor {conflicto['profesor']}: {conflicto['materia_nueva']} vs {conflicto['materia_existente']}")
    
    return horarios_creados, conflictos_detectados

def actualizar_datos_academicos():
    """Actualizar datos académicos de profesores existentes"""
    profesores = Usuario.query.filter_by(tipo_usuario=TipoUsuario.PROFESOR).all()
    
    datos_academicos = [
        {'carrera': 'Computación', 'turno': 'Diurno'},
        {'carrera': 'Computación', 'turno': 'Nocturno'},
    ]
    
    for i, profesor in enumerate(profesores[:2]):
        if i < len(datos_academicos):
            profesor.carrera = datos_academicos[i]['carrera']
            profesor.turno = datos_academicos[i]['turno']
    
    db.session.commit()
    print(f"✓ Actualizados datos académicos de {len(profesores)} profesores")

if __name__ == '__main__':
    with app.app_context():
        print("🕐 Iniciando creación de horarios de demostración...")
        print("=" * 50)
        
        # Actualizar datos académicos
        actualizar_datos_academicos()
        
        # Crear horarios
        horarios, conflictos = crear_horarios_demo()
        
        print("=" * 50)
        print("✅ Horarios de demostración creados exitosamente!")
        print(f"\n📊 Resumen:")
        print(f"   📚 Horarios creados: {len(horarios)}")
        print(f"   ⚠ Conflictos detectados: {len(conflictos)}")
        
        print(f"\n🔍 Para ver los horarios:")
        print(f"   • Inicia sesión como profesor (12345678 / profesor123)")
        print(f"   • Ve a la sección 'Horarios' en el menú")
        print(f"   • Los administradores pueden ver el análisis de conflictos")
