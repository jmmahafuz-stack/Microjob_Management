(function () {
    'use strict';

    function ready(fn) {
        if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
        else fn();
    }

    ready(function () {
        // Mobile navigation
        const menuButton = document.querySelector('[data-mobile-menu]');
        const menu = document.querySelector('[data-nav-menu]');
        if (menuButton && menu) {
            menuButton.addEventListener('click', function () {
                const open = menu.classList.toggle('is-open');
                menuButton.setAttribute('aria-expanded', String(open));
            });
            document.addEventListener('click', function (event) {
                if (window.innerWidth <= 800 && menu.classList.contains('is-open') && !menu.contains(event.target) && !menuButton.contains(event.target)) {
                    menu.classList.remove('is-open');
                    menuButton.setAttribute('aria-expanded', 'false');
                }
            });
        }

        // Password visibility
        document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
            button.addEventListener('click', function () {
                const input = document.getElementById(button.dataset.passwordToggle);
                if (!input) return;
                const show = input.type === 'password';
                input.type = show ? 'text' : 'password';
                button.innerHTML = show ? '<i class="fa-solid fa-eye-slash"></i>' : '<i class="fa-solid fa-eye"></i>';
                button.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
            });
        });

        // Close alert messages safely.
        document.querySelectorAll('[data-dismiss], .alert .btn-close').forEach(function (button) {
            button.addEventListener('click', function () {
                const alert = button.closest('.alert, .message-alert');
                if (alert) alert.remove();
            });
        });

        // Show selected file names without changing form values.
        document.querySelectorAll('input[type="file"]').forEach(function (input) {
            input.addEventListener('change', function () {
                const file = input.files && input.files[0];
                if (!file) return;
                let note = input.parentElement.querySelector('.selected-file-name');
                if (!note) {
                    note = document.createElement('small');
                    note.className = 'selected-file-name field-help';
                    input.insertAdjacentElement('afterend', note);
                }
                note.textContent = 'Selected: ' + file.name;
            });
        });

        // Prevent double submits while preserving browser validation.
        document.querySelectorAll('form').forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (form.dataset.submitting === 'true') {
                    event.preventDefault();
                    return;
                }
                form.dataset.submitting = 'true';
                const submit = form.querySelector('button[type="submit"]');
                if (submit && !submit.disabled) {
                    submit.disabled = true;
                    submit.classList.add('is-submitting');
                    const original = submit.innerHTML;
                    submit.dataset.originalText = original;
                    submit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                    window.setTimeout(function () {
                        if (document.body.contains(submit)) {
                            submit.disabled = false;
                            submit.classList.remove('is-submitting');
                            submit.innerHTML = submit.dataset.originalText || original;
                            form.dataset.submitting = 'false';
                        }
                    }, 10000);
                }
            });
        });

        // Keep long tables usable on small screens.
        document.querySelectorAll('table').forEach(function (table) {
            if (!table.parentElement.classList.contains('table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    });
}());
