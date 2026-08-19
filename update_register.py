#!/usr/bin/env python
# Script to update register.html with professional styling

new_template = '''{% extends 'base.html' %}

{% block content %}
<div class="register-wrapper">
    <!-- Left Side: Branding & Info -->
    <div class="register-info">
        <div class="info-content">
            <h1>Join Our Community</h1>
            <p class="subtitle">Connect with skilled professionals or find services you need</p>
            
            <div class="benefits">
                <div class="benefit-item">
                    <span class="benefit-icon">✓</span>
                    <div>
                        <h4>For Customers</h4>
                        <p>Find trusted professionals for any job</p>
                    </div>
                </div>
                <div class="benefit-item">
                    <span class="benefit-icon">✓</span>
                    <div>
                        <h4>For Workers</h4>
                        <p>Grow your business and connect with customers</p>
                    </div>
                </div>
                <div class="benefit-item">
                    <span class="benefit-icon">✓</span>
                    <div>
                        <h4>Secure & Safe</h4>
                        <p>Verified profiles and secure transactions</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Right Side: Registration Form -->
    <div class="register-form-container">
        <div class="register-card">
            <div class="register-header">
                <h2>Create Account</h2>
                <p>Get started in just a few steps</p>
            </div>

            {% include 'partials/messages.html' %}

            <form method="POST" enctype="multipart/form-data" class="register-form" id="registerForm">
                {% csrf_token %}

                <!-- Role Selection Section -->
                <div class="form-section">
                    <h3 class="section-title">I want to register as:</h3>
                    <div class="role-selector">
                        {% for value, label in form.role.field.choices %}
                        <div class="role-option">
                            <input type="radio" name="role" value="{{ value }}" id="role_{{ value }}" 
                                   {% if form.role.value == value %}checked{% endif %} 
                                   onchange="updateRoleDescription(this)">
                            <label for="role_{{ value }}" class="role-label">
                                <span class="role-icon">{% if value == 'worker' %}👨‍💼{% else %}👤{% endif %}</span>
                                <span class="role-text">{{ label }}</span>
                            </label>
                        </div>
                        {% endfor %}
                    </div>
                    <div id="roleDescription" class="role-description"></div>
                </div>

                <!-- Basic Information Section -->
                <div class="form-section">
                    <h3 class="section-title">Basic Information</h3>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.first_name.id_for_label }}" class="form-label">
                                First Name
                            </label>
                            {{ form.first_name }}
                            <span class="error-message">{{ form.first_name.errors }}</span>
                        </div>

                        <div class="form-group">
                            <label for="{{ form.last_name.id_for_label }}" class="form-label">
                                Last Name
                            </label>
                            {{ form.last_name }}
                            <span class="error-message">{{ form.last_name.errors }}</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.username.id_for_label }}" class="form-label">
                            Username
                        </label>
                        {{ form.username }}
                        <span class="form-help">Choose a unique username for your account</span>
                        <span class="error-message">{{ form.username.errors }}</span>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.email.id_for_label }}" class="form-label">
                                Email Address
                            </label>
                            {{ form.email }}
                            <span class="error-message">{{ form.email.errors }}</span>
                        </div>

                        <div class="form-group">
                            <label for="{{ form.phone.id_for_label }}" class="form-label">
                                Phone Number
                            </label>
                            {{ form.phone }}
                            <span class="error-message">{{ form.phone.errors }}</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.address.id_for_label }}" class="form-label">
                            Address
                        </label>
                        {{ form.address }}
                        <span class="error-message">{{ form.address.errors }}</span>
                    </div>
                </div>

                <!-- Profile Picture Section -->
                <div class="form-section">
                    <h3 class="section-title">Profile Photo</h3>
                    
                    <div class="form-group">
                        <label for="{{ form.profile_picture.id_for_label }}" class="form-label">
                            Upload Profile Picture
                        </label>
                        <div class="file-upload-wrapper">
                            {{ form.profile_picture }}
                            <span class="file-upload-label">📷 Click to upload or drag and drop</span>
                        </div>
                        <span class="form-help">PNG, JPG up to 5MB</span>
                        <span class="error-message">{{ form.profile_picture.errors }}</span>
                    </div>
                </div>

                <!-- Security Section -->
                <div class="form-section">
                    <h3 class="section-title">Security</h3>
                    
                    <div class="form-group">
                        <label for="{{ form.password1.id_for_label }}" class="form-label">
                            Password
                        </label>
                        <div class="password-wrapper">
                            {{ form.password1 }}
                            <button type="button" class="password-toggle" 
                                    onclick="togglePassword('id_password1', this)" 
                                    aria-label="Show password">👁</button>
                        </div>
                        <span class="form-help">At least 8 characters with uppercase, lowercase, and numbers</span>
                        <span class="error-message">{{ form.password1.errors }}</span>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.password2.id_for_label }}" class="form-label">
                            Confirm Password
                        </label>
                        <div class="password-wrapper">
                            {{ form.password2 }}
                            <button type="button" class="password-toggle" 
                                    onclick="togglePassword('id_password2', this)" 
                                    aria-label="Show password">👁</button>
                        </div>
                        <span class="error-message">{{ form.password2.errors }}</span>
                    </div>
                </div>

                <!-- Preferences Section -->
                <div class="form-section">
                    <h3 class="section-title">Preferences</h3>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.preferred_contact_method.id_for_label }}" class="form-label">
                                Preferred Contact Method
                            </label>
                            {{ form.preferred_contact_method }}
                            <span class="error-message">{{ form.preferred_contact_method.errors }}</span>
                        </div>

                        <div class="form-group checkbox-group">
                            <label class="checkbox-label">
                                {{ form.receive_notifications }}
                                <span>{{ form.receive_notifications.label }}</span>
                            </label>
                            <span class="error-message">{{ form.receive_notifications.errors }}</span>
                        </div>
                    </div>
                </div>

                <!-- Worker-Specific Section -->
                <div class="form-section worker-section" style="display: none;">
                    <h3 class="section-title">🏢 Professional Details</h3>

                    <div class="form-group">
                        <label for="{{ form.worker_categories.id_for_label }}" class="form-label">
                            Categories You Work In
                        </label>
                        <div class="categories-wrapper">
                            {{ form.worker_categories }}
                        </div>
                        <span class="form-help">Select all the categories/professions you can work with</span>
                        <span class="error-message">{{ form.worker_categories.errors }}</span>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_service.id_for_label }}" class="form-label">
                            Service Offered
                        </label>
                        {{ form.worker_service }}
                        <span class="error-message">{{ form.worker_service.errors }}</span>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_service_category.id_for_label }}" class="form-label">
                            Service Category
                        </label>
                        {{ form.worker_service_category }}
                        <span class="error-message">{{ form.worker_service_category.errors }}</span>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.worker_experience.id_for_label }}" class="form-label">
                                Years of Experience
                            </label>
                            {{ form.worker_experience }}
                            <span class="error-message">{{ form.worker_experience.errors }}</span>
                        </div>

                        <div class="form-group">
                            <label for="{{ form.worker_hourly_rate.id_for_label }}" class="form-label">
                                Hourly Rate (Optional)
                            </label>
                            {{ form.worker_hourly_rate }}
                            <span class="error-message">{{ form.worker_hourly_rate.errors }}</span>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_skills.id_for_label }}" class="form-label">
                            Skills
                        </label>
                        {{ form.worker_skills }}
                        <span class="form-help">Comma-separated list of your skills</span>
                        <span class="error-message">{{ form.worker_skills.errors }}</span>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_service_area.id_for_label }}" class="form-label">
                            Service Area
                        </label>
                        {{ form.worker_service_area }}
                        <span class="error-message">{{ form.worker_service_area.errors }}</span>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_bio.id_for_label }}" class="form-label">
                            About You (Short Bio)
                        </label>
                        {{ form.worker_bio }}
                        <span class="form-help">Tell customers about yourself and your experience</span>
                        <span class="error-message">{{ form.worker_bio.errors }}</span>
                    </div>
                </div>

                <!-- Submit Button -->
                <div class="form-actions">
                    <button type="submit" class="btn-primary">Create Account</button>
                </div>

                <!-- Login Link -->
                <p class="login-switch">
                    Already have an account? <a href="{% url 'login' %}">Sign in here</a>
                </p>
            </form>
        </div>
    </div>
</div>

<style>
/* ===================================
   REGISTRATION PAGE STYLES
   =================================== */

:root {
    --primary-color: #1f527d;
    --primary-hover: #143c5c;
    --accent-color: #00a8e8;
    --success-color: #4caf50;
    --error-color: #f44336;
    --warning-color: #ff9800;
    --background-color: #f5f7fa;
    --surface-color: #ffffff;
    --text-primary: #2c3e50;
    --text-secondary: #666666;
    --border-color: #e0e0e0;
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.15);
    --border-radius: 8px;
    --transition: all 0.3s ease;
}

* {
    margin: 0;
    padding: 0;
}

.register-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Left Info Section */
.register-info {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
    color: white;
    padding: 60px 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;
    overflow: hidden;
}

.register-info::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 600px;
    height: 600px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    animation: float 8s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(20px); }
}

.info-content {
    position: relative;
    z-index: 1;
    text-align: center;
    max-width: 400px;
}

.register-info h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 12px;
    line-height: 1.2;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 48px;
    line-height: 1.6;
}

.benefits {
    display: flex;
    flex-direction: column;
    gap: 28px;
    text-align: left;
}

.benefit-item {
    display: flex;
    gap: 16px;
    align-items: flex-start;
}

.benefit-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    min-width: 40px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    font-size: 20px;
    font-weight: bold;
}

.benefit-item h4 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 4px 0;
}

.benefit-item p {
    font-size: 0.9rem;
    opacity: 0.85;
    margin: 0;
}

/* Right Form Section */
.register-form-container {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    background: var(--background-color);
    overflow-y: auto;
}

.register-card {
    background: var(--surface-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    padding: 48px 40px;
    width: 100%;
    max-width: 480px;
}

.register-header {
    text-align: center;
    margin-bottom: 32px;
}

.register-header h2 {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 8px 0;
}

.register-header p {
    color: var(--text-secondary);
    margin: 0;
    font-size: 0.95rem;
}

/* Form Sections */
.form-section {
    margin-bottom: 32px;
}

.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--border-color);
}

/* Role Selector */
.role-selector {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
}

.role-option {
    position: relative;
}

.role-option input[type="radio"] {
    display: none;
}

.role-label {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border: 2px solid var(--border-color);
    border-radius: var(--border-radius);
    cursor: pointer;
    transition: var(--transition);
    background: var(--surface-color);
}

.role-option input[type="radio"]:checked + .role-label {
    border-color: var(--primary-color);
    background: rgba(31, 82, 125, 0.05);
    color: var(--primary-color);
    font-weight: 600;
}

.role-icon {
    font-size: 1.5rem;
}

.role-description {
    font-size: 0.9rem;
    color: var(--text-secondary);
    padding: 8px 0;
    min-height: 20px;
}

/* Form Layout */
.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 0;
}

.form-label {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
    font-size: 0.95rem;
}

/* Form Inputs */
.register-form input[type="text"],
.register-form input[type="email"],
.register-form input[type="password"],
.register-form input[type="number"],
.register-form input[type="tel"],
.register-form select,
.register-form textarea {
    width: 100%;
    padding: 12px 14px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 0.95rem;
    font-family: inherit;
    color: var(--text-primary);
    background: var(--surface-color);
    transition: var(--transition);
    box-sizing: border-box;
}

.register-form input[type="text"]:focus,
.register-form input[type="email"]:focus,
.register-form input[type="password"]:focus,
.register-form input[type="number"]:focus,
.register-form input[type="tel"]:focus,
.register-form select:focus,
.register-form textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(31, 82, 125, 0.1);
    background: rgba(31, 82, 125, 0.02);
}

.register-form textarea {
    resize: vertical;
    min-height: 100px;
}

/* Password Toggle */
.password-wrapper {
    position: relative;
    width: 100%;
}

.password-wrapper input {
    padding-right: 44px;
}

.password-toggle {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
    padding: 0;
    margin: 0;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
}

.password-toggle:hover {
    opacity: 0.7;
}

/* Checkboxes */
.checkbox-group {
    align-content: flex-end;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-weight: 500;
    color: var(--text-primary);
    margin: 0;
}

.checkbox-label input[type="checkbox"] {
    width: 16px;
    height: 16px;
    min-width: 16px;
    cursor: pointer;
    accent-color: var(--primary-color);
}

/* Categories Wrapper */
.categories-wrapper {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 12px;
    background: rgba(0, 0, 0, 0.02);
    border-radius: 6px;
    max-height: 150px;
    overflow-y: auto;
}

.categories-wrapper label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    cursor: pointer;
    margin: 0;
}

.categories-wrapper input[type="checkbox"] {
    width: 16px;
    height: 16px;
    cursor: pointer;
    accent-color: var(--primary-color);
}

/* File Upload */
.file-upload-wrapper {
    position: relative;
    border: 2px dashed var(--border-color);
    border-radius: var(--border-radius);
    padding: 24px;
    text-align: center;
    cursor: pointer;
    transition: var(--transition);
    background: rgba(0, 0, 0, 0.02);
}

.file-upload-wrapper:hover {
    border-color: var(--primary-color);
    background: rgba(31, 82, 125, 0.05);
}

.file-upload-wrapper input[type="file"] {
    display: none;
}

.file-upload-label {
    display: block;
    font-size: 0.95rem;
    color: var(--text-secondary);
    font-weight: 500;
}

/* Help Text */
.form-help {
    display: block;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 4px;
}

/* Error Messages */
.error-message {
    display: block;
    color: var(--error-color);
    font-size: 0.8rem;
    margin-top: 4px;
    font-weight: 500;
}

/* Submit Button */
.form-actions {
    margin-top: 32px;
    margin-bottom: 20px;
}

.btn-primary {
    width: 100%;
    padding: 14px 24px;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
    color: white;
    border: none;
    border-radius: var(--border-radius);
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
    box-shadow: var(--shadow-md);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-primary:active {
    transform: translateY(0);
}

/* Login Switch */
.login-switch {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin: 0;
}

.login-switch a {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 600;
    transition: var(--transition);
}

.login-switch a:hover {
    color: var(--accent-color);
    text-decoration: underline;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .register-wrapper {
        grid-template-columns: 1fr;
    }

    .register-info {
        display: none;
    }

    .register-card {
        max-width: 100%;
        padding: 40px 30px;
    }
}

@media (max-width: 768px) {
    .register-card {
        padding: 30px 20px;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .role-selector {
        grid-template-columns: 1fr;
    }

    .register-header h2 {
        font-size: 1.4rem;
    }

    .btn-primary {
        padding: 12px 20px;
    }
}
</style>

<script>
function togglePassword(fieldId, button) {
    const field = document.getElementById(fieldId);
    if (!field) return;

    if (field.type === "password") {
        field.type = "text";
        button.textContent = "🙈";
        button.setAttribute("aria-label", "Hide password");
    } else {
        field.type = "password";
        button.textContent = "👁";
        button.setAttribute("aria-label", "Show password");
    }
}

function updateRoleDescription(radioButton) {
    const description = document.getElementById('roleDescription');
    const descriptions = {
        customer: "Looking for skilled professionals to complete your tasks and projects",
        worker: "Ready to showcase your skills and connect with customers who need your services"
    };
    description.textContent = descriptions[radioButton.value] || '';
}

document.addEventListener('DOMContentLoaded', function () {
    const selectedRole = document.querySelector('input[name="role"]:checked');
    if (selectedRole) {
        updateRoleDescription(selectedRole);
    }

    const toggleWorkerFields = function () {
        const selectedRole = document.querySelector('input[name="role"]:checked')?.value || 'customer';
        const workerSection = document.querySelector('.worker-section');
        
        if (selectedRole === 'worker') {
            workerSection.style.display = 'block';
        } else {
            workerSection.style.display = 'none';
        }
    };

    const roleRadios = document.querySelectorAll('input[name="role"]');
    roleRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            updateRoleDescription(this);
            toggleWorkerFields();
        });
    });

    toggleWorkerFields();

    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        const wrapper = fileInput.closest('.file-upload-wrapper');
        wrapper.addEventListener('click', () => fileInput.click());
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                const label = wrapper.querySelector('.file-upload-label');
                label.textContent = '✓ ' + fileName;
                wrapper.style.borderColor = 'var(--success-color)';
            }
        });

        wrapper.addEventListener('dragover', (e) => {
            e.preventDefault();
            wrapper.style.borderColor = 'var(--primary-color)';
            wrapper.style.background = 'rgba(31, 82, 125, 0.1)';
        });

        wrapper.addEventListener('dragleave', () => {
            wrapper.style.borderColor = 'var(--border-color)';
            wrapper.style.background = 'rgba(0, 0, 0, 0.02)';
        });

        wrapper.addEventListener('drop', (e) => {
            e.preventDefault();
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                fileInput.dispatchEvent(new Event('change'));
            }
        });
    }
});
</script>

{% endblock %}'''

# Write the new template
output_path = r"c:\Users\Mahafuz\OneDrive\Desktop\Projects\Micro-Job Management\Micro-Job\templates\accounts\register.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(new_template)

print(f"✅ Successfully updated {output_path}")
print(f"File size: {len(new_template)} characters")
