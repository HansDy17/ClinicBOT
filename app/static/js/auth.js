
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const togglePassword = document.querySelector('.toggle-password');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('loginButton');
    
    // Toggle password visibility
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye-slash');
            this.querySelector('i').classList.toggle('fa-eye');
        });
    }
    
    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Show loading state
            loginButton.disabled = true;
            loginButton.querySelector('.button-text').textContent = 'Signing In...';
            loginButton.querySelector('.button-spinner').style.display = 'inline-block';
            
            try {
                const formData = new FormData(loginForm);
                const response = await fetch(loginForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Redirect on successful login
                    window.location.href = data.redirect || '/dashboard';
                } else {
                    // Show error message
                    alert(data.message || 'Login failed. Please try again.');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('An error occurred. Please try again.');
            } finally {
                // Reset button state
                loginButton.disabled = false;
                loginButton.querySelector('.button-text').textContent = 'Sign In';
                loginButton.querySelector('.button-spinner').style.display = 'none';
            }
        });
    }
    
    // Clear error messages when user starts typing
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const flashMessages = document.querySelector('.flash-messages');
            if (flashMessages) {
                flashMessages.innerHTML = '';
            }
        });
    });
});