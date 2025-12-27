from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Course, Enrollment
from utils import login_required, role_required, log_audit

student_bp = Blueprint('student', __name__)

# --- Student Course Enrollment Module ---

@student_bp.route('/courses', methods=['GET'])
@login_required
def get_available_courses():
    """Read: Get all courses available for enrollment"""
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses]), 200

@student_bp.route('/enroll', methods=['POST'])
@role_required('student')
def enroll_course():
    """Create: Enroll in a course"""
    data = request.get_json()
    course_id = data.get('course_id')
    student_id = session['user_id']

    # Check if already enrolled
    existing = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing:
        return jsonify({'error': 'Already enrolled in this course'}), 400

    new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
    db.session.add(new_enrollment)
    db.session.commit()

    log_audit('CREATE', 'enrollments', new_enrollment.id, f"Student {student_id} enrolled in course {course_id}")

    return jsonify({'message': 'Enrolled successfully', 'enrollment': new_enrollment.to_dict()}), 201

@student_bp.route('/my-enrollments', methods=['GET'])
@role_required('student')
def my_enrollments():
    """Read: Get logged-in student's enrollments"""
    student_id = session['user_id']
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    return jsonify([e.to_dict() for e in enrollments]), 200

@student_bp.route('/drop/<int:enrollment_id>', methods=['DELETE'])
@role_required('student')
def drop_course(enrollment_id):
    """Delete: Drop a course (Soft delete or Hard delete based on preference)"""
    # Using hard delete for simplicity, or update status to 'dropped'
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    if enrollment.student_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(enrollment)
    db.session.commit()
    
    log_audit('DELETE', 'enrollments', enrollment_id, f"Student dropped course {enrollment.course_id}")

    return jsonify({'message': 'Course dropped successfully'}), 200