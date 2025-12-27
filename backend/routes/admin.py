from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Course, User, AuditLog
from utils import role_required, log_audit

admin_bp = Blueprint('admin', __name__)

# --- Admin Management Tasks ---

@admin_bp.route('/courses', methods=['POST'])
@role_required('admin')
def add_course():
    """Create: Admin creates a new course"""
    data = request.get_json()
    
    new_course = Course(
        course_code=data['course_code'],
        course_name=data['course_name'],
        credits=data['credits'],
        description=data.get('description'),
        created_by=session['user_id']
    )
    
    try:
        db.session.add(new_course)
        db.session.commit()
        log_audit('CREATE', 'courses', new_course.id, f"Admin created course {new_course.course_code}")
        return jsonify({'message': 'Course created', 'course': new_course.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@role_required('admin')
def update_course(course_id):
    """Update: Admin edits a course"""
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    course.course_name = data.get('course_name', course.course_name)
    course.credits = data.get('credits', course.credits)
    course.description = data.get('description', course.description)
    
    db.session.commit()
    log_audit('UPDATE', 'courses', course.id, f"Admin updated course {course.course_code}")
    
    return jsonify({'message': 'Course updated', 'course': course.to_dict()}), 200

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@role_required('admin')
def delete_course(course_id):
    """Delete: Admin deletes a course"""
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    
    log_audit('DELETE', 'courses', course_id, f"Admin deleted course {course.course_code}")
    return jsonify({'message': 'Course deleted'}), 200

@admin_bp.route('/audit-logs', methods=['GET'])
@role_required('admin')
def get_audit_logs():
    """Read: Admin views system logs"""
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    log_list = [{
        'id': l.id,
        'action': l.action_type,
        'table': l.table_name,
        'description': l.description,
        'timestamp': str(l.timestamp)
    } for l in logs]
    
    return jsonify(log_list), 200