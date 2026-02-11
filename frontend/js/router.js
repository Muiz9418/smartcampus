// Path-based router for the frontend
const routes = {
    '/': 'pages/home.html',
    '/home': 'pages/home.html',
    '/auth': 'pages/auth.html',
    '/auth/login': 'pages/auth.html',
    '/auth/register': 'pages/auth.html',
    '/learn-more': 'pages/learn-more.html',
    '/student-dashboard': 'pages/student-dashboard.html',
    '/instructor-dashboard': 'pages/instructor-dashboard.html',
    '/admin': 'pages/admin.html',
    '/profile': 'pages/profile.html',
    '/courses': 'pages/courses.html',
    '/attendance': 'pages/attendance.html',
    '/results': 'pages/results.html',
    '/settings': 'pages/settings.html',
    '/course-detail': 'pages/course-detail.html'
};

// Load navigation
async function loadNav() {
    try {
        const response = await fetch('/components/nav.html');
        if (response.ok) {
            const html = await response.text();
            const navContainer = document.getElementById('nav');
            if (navContainer) {
                navContainer.innerHTML = html;
            }
        }
    } catch (error) {
        console.error('Error loading navigation:', error);
    }
}

// Load page based on pathname
async function loadPage(pathname) {
    const route = routes[pathname] || routes['/'];
    
    try {
        const response = await fetch(`/${route}`);
        
        if (response.ok) {
            const html = await response.text();
            const appContainer = document.getElementById('app');
            if (appContainer) {
                appContainer.innerHTML = html;
                bindLinks();
            }
        } else {
            console.error(`Failed to load page: ${route}`);
        }
    } catch (error) {
        console.error('Error loading page:', error);
    }
}

// Load footer
async function loadFooter() {
    try {
        const response = await fetch('/components/footer.html');
        if (response.ok) {
            const html = await response.text();
            const footerContainer = document.getElementById('footer');
            if (footerContainer) {
                footerContainer.innerHTML = html;
                // Update year
                const yearElement = document.getElementById('year');
                if (yearElement) {
                    yearElement.textContent = new Date().getFullYear();
                }
            }
        }
    } catch (error) {
        console.error('Error loading footer:', error);
    }
}

// Bind navigation links
function bindLinks() {
    const links = document.querySelectorAll('[data-link]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const href = link.getAttribute('data-link');
            window.location.hash = href;
        });
    });
}

// Handle popstate and page load for path-based routing
function handlePopState() {
    const pathname = window.location.pathname;
    loadPage(pathname);
}

// Initialize router
window.addEventListener('load', () => {
    loadNav();
    loadFooter();
    handlePopState();
});

window.addEventListener('popstate', handlePopState);

// Expose navigate function globally for path-based routing
window.__navigate = function(path) {
    history.pushState({}, '', path);
    handlePopState();
};
