import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loader from './Loader';

const PrivateRoute = ({ allowedRoles }) => {
    const { user, loading } = useAuth();

    if (loading) return <div className="h-screen flex items-center justify-center"><Loader /></div>;

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(user.role)) {
        // Simple "Access Denied" UI for unauthorized roles
        return (
            <div className="p-10 text-center">
                <h1 className="text-3xl font-bold text-red-600">403 Access Denied</h1>
                <p>You do not have permission to view this page.</p>
            </div>
        );
    }

    return <Outlet />;
};

export default PrivateRoute;