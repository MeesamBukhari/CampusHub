import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    if (!user) return null;

    return (
        <nav className="bg-white shadow-md p-4 flex justify-between items-center">
            <div className="text-xl font-bold text-blue-600">CampusHub</div>
            <div className="flex gap-4 items-center">
                <Link to="/dashboard" className="hover:text-blue-600">Dashboard</Link>
                
                {/* Role Based Links */}
                {user.role === 'student' && (
                    <Link to="/courses" className="hover:text-blue-600">My Courses</Link>
                )}
                {user.role === 'admin' && (
                    <Link to="/admin" className="hover:text-blue-600">Admin Panel</Link>
                )}

                <span className="text-gray-500 text-sm">Hi, {user.username} ({user.role})</span>
                <button onClick={handleLogout} className="text-red-500 hover:text-red-700 font-medium">
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navbar;