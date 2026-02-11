// Global auth handlers for path-based routing
window.__handleLogin = function(event) {
    if (event) event.preventDefault();
    
    const identifier = document.getElementById('login-identifier')?.value;
    const password = document.getElementById('login-password')?.value;
    const userType = document.getElementById('user-type')?.value || 'student';
    
    if (!identifier || !password) {
        alert('Please provide credentials');
        return;
    }
    
    // Route by user type
    if (userType === 'instructor') {
        navigate('/instructor-dashboard');
    } else if (userType === 'admin') {
        navigate('/admin');
    } else {
        navigate('/student-dashboard');
    }
};

window.__handleRegister = function(event) {
    if (event) event.preventDefault();
    // Handled by auth page
};

window.__confirmLogout = function(event) {
    if (event) event.preventDefault();
    
    if (confirm('Are you sure you want to logout?')) {
        navigate('/auth/login');
    }
};
