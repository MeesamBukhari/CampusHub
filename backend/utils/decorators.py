from functools import wraps
from flask import session, jsonify, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            # Allow admins to access everything, or strict role check
            user_role = session.get('role')
            if user_role != required_role and user_role != 'admin':
                return jsonify({'error': 'Access denied: Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_audit(action, table_name, record_id=None, description=None):
    """Helper to write to AuditLog table"""
    from extensions import db
    from models import AuditLog
    
    try:
        log = AuditLog(
            user_id=session.get('user_id'),
            action_type=action,
            table_name=table_name,
            record_id=record_id,
            description=description,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Audit Log Failed: {e}")