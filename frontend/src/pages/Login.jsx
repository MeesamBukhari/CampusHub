import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({ email: '', password: '', username: '', role: 'student' });
    const [error, setError] = useState('');
    const { login, register } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                await login(formData.email, formData.password);
                navigate('/dashboard');
            } else {
                await register(formData.username, formData.email, formData.password, formData.role);
                alert('Registration successful! Please login.');
                setIsLogin(true);
            }
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded shadow-md w-96">
                <h2 className="text-2xl font-bold mb-6 text-center">{isLogin ? 'Login' : 'Register'}</h2>
                {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4 text-sm">{error}</div>}
                
                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <>
                            <input 
                                type="text" placeholder="Username" className="input-field" required 
                                onChange={e => setFormData({...formData, username: e.target.value})}
                            />
                            <select 
                                className="input-field" 
                                onChange={e => setFormData({...formData, role: e.target.value})}
                            >
                                <option value="student">Student</option>
                                <option value="teacher">Teacher</option>
                                <option value="admin">Admin</option>
                            </select>
                        </>
                    )}
                    <input 
                        type="email" placeholder="Email" className="input-field" required 
                        onChange={e => setFormData({...formData, email: e.target.value})}
                    />
                    <input 
                        type="password" placeholder="Password" className="input-field" required 
                        onChange={e => setFormData({...formData, password: e.target.value})}
                    />
                    <button type="submit" className="w-full btn-primary">
                        {isLogin ? 'Login' : 'Sign Up'}
                    </button>
                </form>
                
                <p className="mt-4 text-center text-sm text-blue-600 cursor-pointer" onClick={() => setIsLogin(!isLogin)}>
                    {isLogin ? "Need an account? Register" : "Have an account? Login"}
                </p>
            </div>
        </div>
    );
};

export default Login;