// Toggle password visibility
function togglePassword(fieldId, button) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    if (field.type === "password") {
        field.type = "text";
        button.textContent = "🙈";
    } else {
        field.type = "password";
        button.textContent = "👁";
    }
}

// Toggle worker fields visibility
function toggleWorkerFields() {
    const selectedRole = document.querySelector('input[name="role"]:checked')?.value || 'customer';
    const workerSection = document.querySelector('.worker-section');
    const nidField = document.getElementById('id_worker_nid_number');
    if (!workerSection) return;
    
    if (selectedRole === 'worker') {
        workerSection.classList.remove('is-hidden');
        nidField?.setAttribute('required', 'required');
    } else {
        workerSection.classList.add('is-hidden');
        nidField?.removeAttribute('required');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    const roleRadios = document.querySelectorAll('input[name="role"]');
    roleRadios.forEach(radio => {
        radio.addEventListener('change', toggleWorkerFields);
    });

    toggleWorkerFields();
});
