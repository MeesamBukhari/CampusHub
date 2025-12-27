import { useEffect, useState } from 'react';
import api from '../api/axios';
import Loader from '../components/Loader';

const CourseEnrollment = () => {
    const [availableCourses, setAvailableCourses] = useState([]);
    const [myEnrollments, setMyEnrollments] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const [coursesRes, enrollRes] = await Promise.all([
                api.get('/student/courses'),
                api.get('/student/my-enrollments')
            ]);
            setAvailableCourses(coursesRes.data);
            setMyEnrollments(enrollRes.data);
        } catch (error) {
            console.error("Failed to fetch data");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleEnroll = async (courseId) => {
        try {
            await api.post('/student/enroll', { course_id: courseId });
            alert("Enrolled successfully!");
            fetchData(); // Refresh lists
        } catch (error) {
            alert(error.response?.data?.error || "Enrollment failed");
        }
    };

    const handleDrop = async (enrollmentId) => {
        if (!window.confirm("Are you sure?")) return;
        try {
            await api.delete(`/student/drop/${enrollmentId}`);
            fetchData();
        } catch (error) {
            console.error(error);
        }
    };

    if (loading) return <div className="p-10"><Loader /></div>;

    return (
        <div className="p-8 space-y-8">
            {/* Available Courses Section */}
            <section>
                <h2 className="text-2xl font-bold mb-4">Available Courses</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {availableCourses.map(course => (
                        <div key={course.id} className="bg-white p-4 border rounded shadow hover:shadow-md transition">
                            <h3 className="font-bold text-lg">{course.course_code}: {course.course_name}</h3>
                            <p className="text-gray-600 text-sm mt-1">{course.description}</p>
                            <div className="mt-4 flex justify-between items-center">
                                <span className="text-xs bg-gray-100 px-2 py-1 rounded">Credits: {course.credits}</span>
                                <button 
                                    onClick={() => handleEnroll(course.id)}
                                    className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                                >
                                    Enroll
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* My Enrollments Section */}
            <section>
                <h2 className="text-2xl font-bold mb-4">My Enrollments</h2>
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border rounded">
                        <thead>
                            <tr className="bg-gray-100 text-left">
                                <th className="p-3 border-b">Course</th>
                                <th className="p-3 border-b">Status</th>
                                <th className="p-3 border-b">Date</th>
                                <th className="p-3 border-b">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {myEnrollments.map(enroll => (
                                <tr key={enroll.id}>
                                    <td className="p-3 border-b">{enroll.course?.course_name}</td>
                                    <td className="p-3 border-b">
                                        <span className={`px-2 py-1 rounded text-xs ${enroll.status === 'enrolled' ? 'bg-green-100 text-green-800' : 'bg-red-100'}`}>
                                            {enroll.status}
                                        </span>
                                    </td>
                                    <td className="p-3 border-b">{enroll.enrollment_date}</td>
                                    <td className="p-3 border-b">
                                        <button 
                                            onClick={() => handleDrop(enroll.id)}
                                            className="text-red-600 hover:text-red-800 text-sm font-medium"
                                        >
                                            Drop
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </section>
        </div>
    );
};
export default CourseEnrollment;