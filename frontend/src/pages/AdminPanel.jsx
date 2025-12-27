import { useEffect, useState } from 'react';
import api from '../api/axios';
import Modal from '../components/Modal';

const AdminPanel = () => {
    const [logs, setLogs] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newCourse, setNewCourse] = useState({ course_code: '', course_name: '', credits: 3, description: '' });

    useEffect(() => {
        const fetchLogs = async () => {
            const { data } = await api.get('/admin/audit-logs');
            setLogs(data);
        };
        fetchLogs();
    }, []);

    const handleCreateCourse = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/courses', newCourse);
            alert("Course Created!");
            setIsModalOpen(false);
            setNewCourse({ course_code: '', course_name: '', credits: 3, description: '' });
        } catch (err) {
            alert("Failed to create course");
        }
    };

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Admin Panel</h1>
                <button onClick={() => setIsModalOpen(true)} className="btn-primary">
                    + Add New Course
                </button>
            </div>

            {/* Audit Logs Table */}
            <div className="bg-white rounded shadow border overflow-hidden">
                <h3 className="p-4 font-semibold bg-gray-50 border-b">System Audit Logs</h3>
                <table className="min-w-full text-sm">
                    <thead className="bg-gray-100">
                        <tr>
                            <th className="p-3 text-left">Time</th>
                            <th className="p-3 text-left">Action</th>
                            <th className="p-3 text-left">Table</th>
                            <th className="p-3 text-left">Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs.map(log => (
                            <tr key={log.id} className="border-b">
                                <td className="p-3 text-gray-500">{new Date(log.timestamp).toLocaleString()}</td>
                                <td className="p-3 font-medium text-blue-600">{log.action}</td>
                                <td className="p-3">{log.table}</td>
                                <td className="p-3">{log.description}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Create Course Modal */}
            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add New Course">
                <form onSubmit={handleCreateCourse} className="space-y-4">
                    <input 
                        className="input-field" placeholder="Course Code (e.g., CS101)" required
                        onChange={e => setNewCourse({...newCourse, course_code: e.target.value})}
                    />
                    <input 
                        className="input-field" placeholder="Course Name" required
                        onChange={e => setNewCourse({...newCourse, course_name: e.target.value})}
                    />
                    <input 
                        className="input-field" type="number" placeholder="Credits" required
                        onChange={e => setNewCourse({...newCourse, credits: parseInt(e.target.value)})}
                    />
                    <textarea 
                        className="input-field" placeholder="Description"
                        onChange={e => setNewCourse({...newCourse, description: e.target.value})}
                    />
                    <button type="submit" className="w-full btn-primary">Create Course</button>
                </form>
            </Modal>
        </div>
    );
};
export default AdminPanel;