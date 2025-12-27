import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
    const { user } = useAuth();

    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">Welcome, {user.username}!</h1>
            <div className="bg-white p-6 rounded shadow-sm border">
                <h2 className="text-xl font-semibold mb-2">Role: {user.role.toUpperCase()}</h2>
                <p className="text-gray-600">
                    Select a module from the navigation bar to get started.
                </p>
                {/* Module Quick Links could go here */}
            </div>
        </div>
    );
};
export default Dashboard;