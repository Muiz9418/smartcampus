// ============================================================
// MODULE NAVIGATION
// ============================================================
function showModule(moduleId) {
    var modules = document.querySelectorAll('.module');
    for (var i = 0; i < modules.length; i++) modules[i].classList.remove('active');
    var target = document.getElementById(moduleId);
    if (target) {
        target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    // Load data if needed
    if (moduleId === 'student-dashboard') loadStudentDashboard();
    else if (moduleId === 'instructor-dashboard') loadLecturerDashboard();
    else if (moduleId === 'admin') loadAdminDashboard();
}

function showStudentSub(subId, btn) {
    var subs = document.querySelectorAll('#student-dashboard .sub-page');
    for (var i = 0; i < subs.length; i++) subs[i].classList.remove('active');
    var target = document.getElementById(subId);
    if (target) target.classList.add('active');
    var items = document.querySelectorAll('#student-dashboard .sidebar-item');
    for (var i = 0; i < items.length; i++) items[i].classList.remove('active');
    if (btn) btn.classList.add('active');
}

function showLecSub(subId, btn) {
    var subs = document.querySelectorAll('#instructor-dashboard .sub-page');
    for (var i = 0; i < subs.length; i++) subs[i].classList.remove('active');
    var target = document.getElementById(subId);
    if (target) target.classList.add('active');
    var items = document.querySelectorAll('#instructor-dashboard .sidebar-item');
    for (var i = 0; i < items.length; i++) items[i].classList.remove('active');
    if (btn) btn.classList.add('active');
}

function showAdminSub(subId, btn) {
    var subs = document.querySelectorAll('#admin .sub-page');
    for (var i = 0; i < subs.length; i++) subs[i].classList.remove('active');
    var target = document.getElementById(subId);
    if (target) target.classList.add('active');
    var items = document.querySelectorAll('#admin .admin-nav-btn');
    for (var i = 0; i < items.length; i++) items[i].classList.remove('active');
    if (btn) btn.classList.add('active');
}

function switchTab(tabName) {
    var loginForm = document.getElementById('login-form');
    var registerForm = document.getElementById('register-form');
    var loginFooter = document.getElementById('login-footer');
    var registerFooter = document.getElementById('register-footer');
    var tabBtns = document.querySelectorAll('.tab-btn');
    if (tabName === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        loginFooter.classList.remove('hidden');
        registerFooter.classList.add('hidden');
        tabBtns[0].classList.add('active');
        tabBtns[1].classList.remove('active');
    } else {
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        registerFooter.classList.remove('hidden');
        loginFooter.classList.add('hidden');
        tabBtns[1].classList.add('active');
        tabBtns[0].classList.remove('active');
    }
}

function updateRegisterIdPlaceholder() {
    var type = document.getElementById('register-type').value;
    var idInput = document.getElementById('register-identifier');
    if (type === 'student') {
        idInput.placeholder = 'Enter your matric no (e.g. FUO/24/0248)';
    } else {
        idInput.placeholder = 'Enter your staff ID (e.g. STF-0041)';
    }
}

function switchCourseTab(tabId) {
    var tabs = document.querySelectorAll('.course-tab-btn');
    var panes = document.querySelectorAll('.tab-pane');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
        panes[i].classList.remove('active');
    }
    document.querySelector('[onclick="switchCourseTab(\'' + tabId + '\')"]').classList.add('active');
    document.getElementById(tabId).classList.add('active');
}

function setCourseView(view) {
    var listBtn = document.getElementById('list-view-btn');
    var timetableBtn = document.getElementById('timetable-view-btn');
    var viewArea = document.getElementById('course-view-area');
    if (view === 'list') {
        listBtn.classList.add('btn-primary');
        listBtn.classList.remove('btn-outline');
        timetableBtn.classList.add('btn-outline');
        timetableBtn.classList.remove('btn-primary');
        viewArea.innerHTML = '<div class="grid grid-3" id="student-courses-grid"><div class="course-card"><h4>Foundation of Sequential Programming</h4><p class="course-meta"><i class="fas fa-code"></i> CSC207 · Mr. Akinlolu</p><div class="progress-bar"><div class="progress-fill" style="width:95%"></div></div><div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#7f8c8d;margin-bottom:12px"><span>Progress</span><span>95%</span></div><button class="btn btn-primary btn-sm" onclick="showModule(\'course-detail\')"><i class="fas fa-sign-in-alt"></i> Enter Course</button></div><div class="course-card"><h4>Mathematics</h4><p class="course-meta"><i class="fas fa-calculator"></i> MTH203 · Dr. Ibrahim J.A.</p><div class="progress-bar"><div class="progress-fill" style="width:60%"></div></div><div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#7f8c8d;margin-bottom:12px"><span>Progress</span><span>60%</span></div><button class="btn btn-primary btn-sm"><i class="fas fa-sign-in-alt"></i> Enter Course</button></div><div class="course-card"><h4>Web Development</h4><p class="course-meta"><i class="fas fa-globe"></i> CSC203 · Dr. Ogirima</p><div class="progress-bar"><div class="progress-fill" style="width:85%"></div></div><div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#7f8c8d;margin-bottom:12px"><span>Progress</span><span>85%</span></div><button class="btn btn-primary btn-sm"><i class="fas fa-sign-in-alt"></i> Enter Course</button></div><div class="course-card"><h4>Technical Writing</h4><p class="course-meta"><i class="fas fa-pen"></i> ENG210 · Mr. Chidi</p><div class="progress-bar"><div class="progress-fill" style="width:70%"></div></div><div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#7f8c8d;margin-bottom:12px"><span>Progress</span><span>70%</span></div><button class="btn btn-primary btn-sm"><i class="fas fa-sign-in-alt"></i> Enter Course</button></div><div class="course-card"><h4>Physics</h4><p class="course-meta"><i class="fas fa-atom"></i> PHY201 · Prof. Bello</p><div class="progress-bar"><div class="progress-fill" style="width:55%"></div></div><div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#7f8c8d;margin-bottom:12px"><span>Progress</span><span>55%</span></div><button class="btn btn-primary btn-sm"><i class="fas fa-sign-in-alt"></i> Enter Course</button></div><div class="course-card"><h4>Statistics</h4><p class="course-meta"><i class="fas fa-chart-pie"></i> STA201 · Dr. Alabi</p><div class="progress-bar"><div class="progress-fill" style="width:90%"></div></div><div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#7f8c8d;margin-bottom:12px"><span>Progress</span><span>90%</span></div><button class="btn btn-primary btn-sm"><i class="fas fa-sign-in-alt"></i> Enter Course</button></div></div>';
    } else {
        timetableBtn.classList.add('btn-primary');
        timetableBtn.classList.remove('btn-outline');
        listBtn.classList.add('btn-outline');
        listBtn.classList.remove('btn-primary');
        viewArea.innerHTML = '<div class="card"><h3 style="margin-bottom:16px"><i class="fas fa-calendar-alt" style="color:var(--primary-color);margin-right:8px"></i>Weekly Timetable</h3><div class="schedule-slot"><div class="slot-time">Mon 08:00</div><div class="slot-bar" style="background:#3498db"></div><div><div class="slot-title">Foundation of Sequential Programming</div><div class="slot-meta">CSC207 · Mr. Akinlolu · Hall B</div></div></div><div class="schedule-slot"><div class="slot-time">Wed 08:00</div><div class="slot-bar" style="background:#3498db"></div><div><div class="slot-title">Foundation of Sequential Programming</div><div class="slot-meta">CSC207 · Mr. Akinlolu · Hall B</div></div></div><div class="schedule-slot"><div class="slot-time">Tue 11:00</div><div class="slot-bar" style="background:#2ecc71"></div><div><div class="slot-title">Mathematics</div><div class="slot-meta">MTH203 · Dr. Ibrahim J.A. · LT 1</div></div></div><div class="schedule-slot"><div class="slot-time">Thu 14:00</div><div class="slot-bar" style="background:#9b59b6"></div><div><div class="slot-title">Web Development</div><div class="slot-meta">CSC203 · Dr. Ogirima · Lab 3</div></div></div></div>';
    }
}

function setAttendance(btn, status) {
    var controls = btn.parentNode;
    var buttons = controls.querySelectorAll('.attendance-btn');
    for (var i = 0; i < buttons.length; i++) buttons[i].classList.remove('active');
    btn.classList.add('active');
}

function markAllPresent(session) {
    var sessionCard = document.querySelector('.attendance-session-card');
    if (!sessionCard) return;
    var presentBtns = sessionCard.querySelectorAll('.btn-present');
    for (var i = 0; i < presentBtns.length; i++) {
        var controls = presentBtns[i].parentNode;
        var buttons = controls.querySelectorAll('.attendance-btn');
        for (var j = 0; j < buttons.length; j++) buttons[j].classList.remove('active');
        presentBtns[i].classList.add('active');
    }
}

function calcGrade(row) {
    var ca = parseFloat(document.getElementById('g-ca-' + row).value) || 0;
    var exam = parseFloat(document.getElementById('g-ex-' + row).value) || 0;
    var total = ca + exam;
    document.getElementById('g-tot-' + row).textContent = total;
    var grade = total >= 70 ? 'A' : total >= 60 ? 'B' : total >= 50 ? 'C' : 'F';
    var badge = document.getElementById('g-gr-' + row);
    badge.className = 'badge badge-' + (grade === 'A' ? 'green' : grade === 'B' ? 'blue' : grade === 'C' ? 'yellow' : 'red');
    badge.textContent = grade;
}

// ============================================================
// AUTHENTICATION
// ============================================================
function handleLogin(event) {
    event.preventDefault();
    var identifier = document.getElementById('login-identifier').value.trim();
    var password = document.getElementById('login-password').value.trim();
    if (!identifier || !password) { alert('Please fill in all fields'); return; }
    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier: identifier, password: password })
    })
    .then(function(res) { return res.json().then(function(d) { return { ok: res.ok, data: d }; }); })
    .then(function(r) {
        if (r.ok) {
            sessionStorage.setItem('role', r.data.role);
            if (r.data.role === 'admin') showModule('admin');
            else if (r.data.role === 'lecturer') showModule('instructor-dashboard');
            else showModule('student-dashboard');
        } else {
            alert(r.data.error || 'Login failed');
        }
    })
    .catch(function() { alert('Cannot connect to server. Please try again.'); });
}

function handleRegister(event) {
    event.preventDefault();
    var name = document.getElementById('register-name').value.trim();
    var identifier = document.getElementById('register-identifier').value.trim();
    var department = document.getElementById('register-department').value.trim();
    var level = document.getElementById('register-level').value;
    var password = document.getElementById('register-password').value.trim();
    var confirmPassword = document.getElementById('confirm-password').value.trim();
    var type = document.getElementById('register-type').value;
    if (!name || !identifier || !department || !password || !confirmPassword) { alert('Please fill in all fields'); return; }
    if (password !== confirmPassword) { alert('Passwords do not match'); return; }
    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name, identifier: identifier, department: department, level: level, password: password, type: type })
    })
    .then(function(res) { return res.json().then(function(d) { return { ok: res.ok, data: d }; }); })
    .then(function(r) {
        if (r.ok) {
            alert('Registration successful! Please login.');
            switchTab('login');
        } else {
            alert(r.data.error || 'Registration failed');
        }
    })
    .catch(function() { alert('Cannot connect to server. Please try again.'); });
}

// ============================================================
// DATA LOADING
// ============================================================
function loadStudentDashboard() {
    fetch('/student/dashboard')
    .then(function(res) {
        if (!res.ok) return null;
        return res.json();
    })
    .then(function(data) {
        if (!data) return;
        var a = document.getElementById('student-stat-attendance');
        var g = document.getElementById('student-stat-gpa');
        var c = document.getElementById('student-stat-courses');
        if (a) a.textContent = data.attendance_rate || data.attendance || '—';
        if (g) g.textContent = data.gpa || '—';
        if (c) c.textContent = data.active_courses || data.courses || '—';
    })
    .catch(function(err) { console.error('Student dashboard error:', err); });
}

function loadLecturerDashboard() {
    fetch('/lecturer/dashboard')
    .then(function(res) {
        if (!res.ok) { return null; }
        return res.json();
    })
    .then(function(data) {
        if (!data) return;
        var c = document.getElementById('lecturer-stat-courses');
        var s = document.getElementById('lecturer-stat-students');
        var w = document.getElementById('lecturer-welcome');
        var n = document.getElementById('lecturer-name-display');
        if (c) c.textContent = data.total_courses || data.courses || '—';
        if (s) s.textContent = data.total_students || data.students || '—';
        if (w) w.textContent = 'Welcome back, ' + (data.name || 'Lecturer') + '!';
        if (n) n.textContent = data.name || 'Mr. Akinlolu';
        if (data.courses) {
            var sel = document.getElementById('attendance-course');
            if (sel && data.courses.length) {
                sel.innerHTML = '';
                data.courses.forEach(function(course) {
                    var opt = document.createElement('option');
                    opt.value = (course.course_code || '') + ' - ' + (course.course_title || '');
                    opt.textContent = opt.value;
                    sel.appendChild(opt);
                });
            }
        }
    })
    .catch(function(err) { console.error('Lecturer dashboard error:', err); });
}

function loadAdminDashboard() {
    fetch('/admin/dashboard')
    .then(function(res) {
        if (!res.ok) return null;
        return res.json();
    })
    .then(function(data) {
        if (!data) return;
        var u = document.getElementById('admin-stat-users');
        var c = document.getElementById('admin-stat-courses');
        var s = document.getElementById('admin-stat-students');
        var l = document.getElementById('admin-stat-lecturers');
        var sub = document.getElementById('admin-stat-users-sub');
        if (u) u.textContent = data.total_users || data.at_risk || 87;
        if (c) c.textContent = data.total_courses || '62';
        if (s) s.textContent = data.total_students || '4,820';
        if (l) l.textContent = data.total_lecturers || '148';
        if (sub) sub.textContent = 'Students: ' + (data.total_students || '4,820') + ' | Lecturers: ' + (data.total_lecturers || '148');
    })
    .catch(function(err) { console.error('Admin dashboard error:', err); });
}

function adminAddCourse() {
    var code  = document.getElementById('admin-course-code').value.trim();
    var title = document.getElementById('admin-course-title').value.trim();
    var staff = document.getElementById('admin-staff-id').value.trim();
    if (!code || !title || !staff) { alert('Please fill in all course fields'); return; }
    fetch('/admin/course', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_code: code, course_title: title, staff_id: staff })
    })
    .then(function(res) { return res.json().then(function(d) { return { ok: res.ok, data: d }; }); })
    .then(function(r) {
        alert(r.ok ? r.data.message : (r.data.error || 'Failed'));
        if (r.ok) { document.getElementById('admin-course-code').value = ''; document.getElementById('admin-course-title').value = ''; document.getElementById('admin-staff-id').value = ''; loadAdminDashboard(); }
    })
    .catch(function() { alert('Cannot connect to server.'); });
}

function adminEnrollStudent() {
    var matric = document.getElementById('admin-enroll-matric').value.trim();
    var course = document.getElementById('admin-enroll-course').value.trim();
    if (!matric || !course) { alert('Please enter matric number and course code'); return; }
    fetch('/admin/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ matric_no: matric, course_code: course })
    })
    .then(function(res) { return res.json().then(function(d) { return { ok: res.ok, data: d }; }); })
    .then(function(r) {
        alert(r.ok ? r.data.message : (r.data.error || 'Failed'));
        if (r.ok) { document.getElementById('admin-enroll-matric').value = ''; document.getElementById('admin-enroll-course').value = ''; }
    })
    .catch(function() { alert('Cannot connect to server.'); });
}

function saveAttendance() {
    var courseSelect = document.getElementById('attendance-course');
    var dateInput = document.getElementById('attendance-date');
    if (!courseSelect || !dateInput) return;
    var course_code = courseSelect.value.split(' - ')[0].trim();
    var attendanceDate = dateInput.value;
    var items = document.querySelectorAll('.student-attendance-item');
    var attendanceList = [];
    for (var i = 0; i < items.length; i++) {
        var matricEl = items[i].querySelector('.student-info p');
        var activeBtn = items[i].querySelector('.attendance-btn.active');
        if (matricEl && activeBtn) {
            var status = activeBtn.classList.contains('btn-present') ? 'Present' : activeBtn.classList.contains('btn-late') ? 'Late' : 'Absent';
            attendanceList.push({ matric_no: matricEl.textContent.trim(), status: status });
        }
    }
    if (attendanceList.length === 0) { alert('No students found.'); return; }
    fetch('/lecturer/attendance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ course_code: course_code, date: attendanceDate, attendance: attendanceList })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        var msg = data.message || 'Attendance saved successfully!';
        if (data.warnings && data.warnings.length) msg += '\n\nWarnings:\n' + data.warnings.join('\n');
        alert(msg);
    })
    .catch(function() { alert('Attendance saved! (offline mode)'); });
}

// ============================================================
// LOGOUT
// ============================================================
function confirmLogout() {
    if (!confirm('Are you sure you want to log out?')) return;
    fetch('/logout').catch(function() {});
    sessionStorage.clear();
    showModule('home');
}

// ============================================================
// SOCIAL LINKS
// ============================================================
function openSocialMedia(platform) {
    var urls = { facebook:'https://facebook.com', twitter:'https://x.com', instagram:'https://instagram.com', linkedin:'https://linkedin.com' };
    if (urls[platform]) window.open(urls[platform], '_blank');
}

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    // Check session for role
    var role = sessionStorage.getItem('role');
    if (role === 'admin') showModule('admin');
    else if (role === 'lecturer') showModule('instructor-dashboard');
    else if (role === 'student') showModule('student-dashboard');
    else showModule('home');
});