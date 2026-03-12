/**
 * main.js - Basic JavaScript for Django Web Application
 * This file provides basic interactivity and is ready for future enhancements.
 */

// Example: Show/hide password toggle for login/register forms
document.addEventListener('DOMContentLoaded', function () {
    // Password visibility toggle
    document.querySelectorAll('.form-control[type="password"]').forEach(function (input) {
        // Create toggle button
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'btn btn-secondary btn-sm password-toggle';
        toggle.textContent = 'Show';
        toggle.style.marginLeft = '8px';

        // Insert after input
        input.parentNode.appendChild(toggle);

        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            if (input.type === 'password') {
                input.type = 'text';
                toggle.textContent = 'Hide';
            } else {
                input.type = 'password';
                toggle.textContent = 'Show';
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function () {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 500);
        });
    }, 5000);
});