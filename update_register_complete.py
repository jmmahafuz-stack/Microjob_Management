#!/usr/bin/env python
# Comprehensive registration page update

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
                            <label for="{{ form.first_name.id_for_label }}" class="form-label">First Name</label>
                            {{ form.first_name }}
                            {% if form.first_name.errors %}<span class="error-message">{{ form.first_name.errors }}</span>{% endif %}
                        </div>

                        <div class="form-group">
                            <label for="{{ form.last_name.id_for_label }}" class="form-label">Last Name</label>
                            {{ form.last_name }}
                            {% if form.last_name.errors %}<span class="error-message">{{ form.last_name.errors }}</span>{% endif %}
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.username.id_for_label }}" class="form-label">Username</label>
                        {{ form.username }}
                        <span class="form-help">Choose a unique username for your account</span>
                        {% if form.username.errors %}<span class="error-message">{{ form.username.errors }}</span>{% endif %}
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.email.id_for_label }}" class="form-label">Email</label>
                            {{ form.email }}
                            {% if form.email.errors %}<span class="error-message">{{ form.email.errors }}</span>{% endif %}
                        </div>

                        <div class="form-group">
                            <label for="{{ form.phone.id_for_label }}" class="form-label">Phone</label>
                            {{ form.phone }}
                            {% if form.phone.errors %}<span class="error-message">{{ form.phone.errors }}</span>{% endif %}
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.address.id_for_label }}" class="form-label">Address</label>
                        {{ form.address }}
                        {% if form.address.errors %}<span class="error-message">{{ form.address.errors }}</span>{% endif %}
                    </div>
                </div>

                <!-- Preferences Section -->
                <div class="form-section preferences-section">
                    <h3 class="section-title preferences-title">Preferences</h3>
                    
                    <div class="form-row preferences-row">
                        <div class="form-group preferences-group">
                            <label for="{{ form.preferred_contact_method.id_for_label }}" class="form-label preferences-label">Contact Method</label>
                            {{ form.preferred_contact_method }}
                            {% if form.preferred_contact_method.errors %}<span class="error-message">{{ form.preferred_contact_method.errors }}</span>{% endif %}
                        </div>

                        <div class="form-group checkbox-group preferences-checkbox">
                            <label class="checkbox-label">
                                {{ form.receive_notifications }}
                                <span>Notifications</span>
                            </label>
                            {% if form.receive_notifications.errors %}<span class="error-message">{{ form.receive_notifications.errors }}</span>{% endif %}
                        </div>
                    </div>
                </div>

                <!-- Profile Picture Section -->
                <div class="form-section">
                    <h3 class="section-title">Profile Photo</h3>
                    
                    <div class="form-group">
                        <div class="file-upload-wrapper">
                            {{ form.profile_picture }}
                            <span class="file-upload-label">📷 Click to upload or drag and drop</span>
                        </div>
                        <span class="form-help">PNG, JPG up to 5MB</span>
                        {% if form.profile_picture.errors %}<span class="error-message">{{ form.profile_picture.errors }}</span>{% endif %}
                    </div>
                </div>

                <!-- Security Section -->
                <div class="form-section">
                    <h3 class="section-title">Security</h3>
                    
                    <div class="form-group">
                        <label for="{{ form.password1.id_for_label }}" class="form-label">Password</label>
                        <div class="password-wrapper">
                            {{ form.password1 }}
                            <button type="button" class="password-toggle" onclick="togglePassword('id_password1', this)" aria-label="Show password">👁</button>
                        </div>
                        <span class="form-help">At least 8 characters with uppercase, lowercase, and numbers</span>
                        {% if form.password1.errors %}<span class="error-message">{{ form.password1.errors }}</span>{% endif %}
                    </div>

                    <div class="form-group">
                        <label for="{{ form.password2.id_for_label }}" class="form-label">Confirm Password</label>
                        <div class="password-wrapper">
                            {{ form.password2 }}
                            <button type="button" class="password-toggle" onclick="togglePassword('id_password2', this)" aria-label="Show password">👁</button>
                        </div>
                        {% if form.password2.errors %}<span class="error-message">{{ form.password2.errors }}</span>{% endif %}
                    </div>
                </div>

                <!-- Worker-Specific Section -->
                <div class="form-section worker-section" style="display: none;">
                    <h3 class="section-title">🏢 Professional Details</h3>

                    <div class="form-group">
                        <label for="{{ form.worker_categories.id_for_label }}" class="form-label">Work Categories</label>
                        <div class="categories-wrapper">
                            {{ form.worker_categories }}
                        </div>
                        <span class="form-help">Select all the categories you work with</span>
                        {% if form.worker_categories.errors %}<span class="error-message">{{ form.worker_categories.errors }}</span>{% endif %}
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.worker_service.id_for_label }}" class="form-label">Service Offered</label>
                            {{ form.worker_service }}
                            {% if form.worker_service.errors %}<span class="error-message">{{ form.worker_service.errors }}</span>{% endif %}
                        </div>

                        <div class="form-group">
                            <label for="{{ form.worker_service_category.id_for_label }}" class="form-label">Category</label>
                            {{ form.worker_service_category }}
                            {% if form.worker_service_category.errors %}<span class="error-message">{{ form.worker_service_category.errors }}</span>{% endif %}
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="{{ form.worker_experience.id_for_label }}" class="form-label">Experience (Years)</label>
                            {{ form.worker_experience }}
                            {% if form.worker_experience.errors %}<span class="error-message">{{ form.worker_experience.errors }}</span>{% endif %}
                        </div>

                        <div class="form-group">
                            <label for="{{ form.worker_hourly_rate.id_for_label }}" class="form-label">Hourly Rate</label>
                            {{ form.worker_hourly_rate }}
                            {% if form.worker_hourly_rate.errors %}<span class="error-message">{{ form.worker_hourly_rate.errors }}</span>{% endif %}
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_skills.id_for_label }}" class="form-label">Skills</label>
                        {{ form.worker_skills }}
                        <span class="form-help">Comma-separated list of your skills</span>
                        {% if form.worker_skills.errors %}<span class="error-message">{{ form.worker_skills.errors }}</span>{% endif %}
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_service_area.id_for_label }}" class="form-label">Service Area</label>
                        {{ form.worker_service_area }}
                        {% if form.worker_service_area.errors %}<span class="error-message">{{ form.worker_service_area.errors }}</span>{% endif %}
                    </div>

                    <div class="form-group">
                        <label for="{{ form.worker_bio.id_for_label }}" class="form-label">About You</label>
                        {{ form.worker_bio }}
                        <span class="form-help">Tell customers about yourself and your experience</span>
                        {% if form.worker_bio.errors %}<span class="error-message">{{ form.worker_bio.errors }}</span>{% endif %}
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
   REGISTRATION PAGE STYLES - PROFESSIONAL
   =================================== */

:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --accent-color: #06b6d4;
    --success-color: #10b981;
    --error-color: #ef4444;
    --warning-color: #f59e0b;
    --background-color: #f8fafc;
    --surface-color: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    --border-radius: 10px;
    --transition: all 0.2s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.register-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 100vh;
    background: var(--background-color);
}

/* ===== LEFT PANEL ===== */
.register-info {
    background: linear-gradient(135deg, #163a56 0%, #0f2537 100%);
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
    background: rgba(255, 255, 255, 0.08);
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
    color: white;
}

.subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-bottom: 48px;
    line-height: 1.6;
    color: white;
}

.benefits {
    display: flex;
    flex-direction: column;
    gap: 24px;
    text-align: left;
}

.benefit-item {
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.benefit-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    min-width: 44px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    font-size: 22px;
    font-weight: bold;
}

.benefit-item h4 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 4px 0;
    color: white;
}

.benefit-item p {
    font-size: 0.9rem;
    opacity: 0.85;
    margin: 0;
    color: white;
}

/* ===== RIGHT PANEL ===== */
.register-form-container {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    background: var(--background-color);
    overflow-y: auto;
    min-height: 100vh;
}

.register-card {
    background: var(--surface-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-lg);
    padding: 50px 40px;
    width: 100%;
    max-width: 520px;
}

.register-header {
    text-align: center;
    margin-bottom: 32px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border-color);
}

.register-header h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}

.register-header p {
    color: var(--text-secondary);
    font-size: 0.95rem;
}

/* ===== FORM SECTIONS ===== */
.form-section {
    margin-bottom: 28px;
}

.form-section:last-of-type {
    margin-bottom: 20px;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
    padding-bottom: 0;
    border-bottom: none;
}

.preferences-section {
    margin-bottom: 16px;
}

.preferences-title {
    font-size: 0.95rem;
    margin-bottom: 12px;
}

/* ===== FORM LAYOUT ===== */
.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 0;
}

.form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 16px;
}

.form-group:last-child {
    margin-bottom: 0;
}

.preferences-row {
    gap: 12px;
}

.preferences-group {
    margin-bottom: 0;
}

.form-label {
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
    font-size: 0.9rem;
}

.preferences-label {
    font-size: 0.85rem;
    margin-bottom: 4px;
}

/* ===== FORM INPUTS ===== */
.register-form input[type="text"],
.register-form input[type="email"],
.register-form input[type="password"],
.register-form input[type="number"],
.register-form input[type="tel"],
.register-form select,
.register-form textarea {
    width: 100%;
    padding: 11px 13px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: inherit;
    color: var(--text-primary);
    background: var(--surface-color);
    transition: var(--transition);
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
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    background: white;
}

.register-form textarea {
    resize: vertical;
    min-height: 90px;
}

/* ===== ROLE SELECTOR ===== */
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
    padding: 12px 14px;
    border: 2px solid var(--border-color);
    border-radius: 8px;
    cursor: pointer;
    transition: var(--transition);
    background: var(--surface-color);
}

.role-option input[type="radio"]:checked + .role-label {
    border-color: var(--primary-color);
    background: rgba(37, 99, 235, 0.05);
    color: var(--primary-color);
    font-weight: 600;
}

.role-icon {
    font-size: 1.4rem;
}

.role-description {
    font-size: 0.85rem;
    color: var(--text-secondary);
    padding: 8px 0 0 0;
    min-height: 20px;
    font-style: italic;
}

/* ===== PASSWORD FIELD ===== */
.password-wrapper {
    position: relative;
    width: 100%;
}

.password-wrapper input {
    padding-right: 40px;
}

.password-toggle {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 28px;
    height: 28px;
    padding: 0;
    margin: 0;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
    z-index: 10;
}

.password-toggle:hover {
    opacity: 0.7;
}

/* ===== CHECKBOXES ===== */
.checkbox-group {
    display: flex;
    align-items: center;
    justify-content: flex-start;
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

.checkbox-group .checkbox-label input[type="checkbox"] {
    width: 12px;
    height: 12px;
    min-width: 12px;
    cursor: pointer;
    accent-color: var(--primary-color);
    border: 1.5px solid var(--border-color);
    border-radius: 3px;
    transition: var(--transition);
    flex-shrink: 0;
}

.checkbox-group .checkbox-label input[type="checkbox"]:hover {
    border-color: var(--primary-color);
}

.checkbox-group .checkbox-label input[type="checkbox"]:checked {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.preferences-checkbox .checkbox-label {
    gap: 6px;
    font-size: 0.85rem;
}

/* ===== CATEGORIES ===== */
.categories-wrapper {
    display: grid;
    grid-template-columns: 1fr;
    gap: 6px;
    padding: 8px;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    max-height: 120px;
    overflow-y: auto;
    box-sizing: border-box;
}

.categories-wrapper label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
    font-size: 0.85rem;
    cursor: pointer;
    margin: 0;
    word-wrap: break-word;
    overflow-wrap: break-word;
    min-width: 0;
    line-height: 1.2;
}

.categories-wrapper input[type="checkbox"] {
    width: 14px;
    height: 14px;
    min-width: 14px;
    cursor: pointer;
    accent-color: var(--primary-color);
    border: 1.5px solid var(--border-color);
    border-radius: 3px;
    transition: var(--transition);
    flex-shrink: 0;
}

.categories-wrapper input[type="checkbox"]:hover {
    border-color: var(--primary-color);
}

.categories-wrapper input[type="checkbox"]:checked {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

/* ===== FILE UPLOAD ===== */
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
    background: rgba(37, 99, 235, 0.05);
}

.file-upload-wrapper input[type="file"] {
    display: none;
}

.file-upload-label {
    display: block;
    font-size: 0.9rem;
    color: var(--text-secondary);
    font-weight: 500;
}

/* ===== HELP TEXT & ERRORS ===== */
.form-help {
    display: block;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 5px;
    font-style: italic;
}

.error-message {
    display: block;
    color: var(--error-color);
    font-size: 0.75rem;
    margin-top: 4px;
    font-weight: 500;
}

/* ===== BUTTON ===== */
.form-actions {
    margin-top: 28px;
    margin-bottom: 16px;
}

.btn-primary {
    width: 100%;
    padding: 12px 24px;
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.95rem;
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

/* ===== LOGIN LINK ===== */
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
}

/* ===== WORKER SECTION ===== */
.worker-section {
    display: none;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid var(--border-color);
}

/* ===== RESPONSIVE ===== */
@media (max-width: 1024px) {
    .register-wrapper {
        grid-template-columns: 1fr;
    }

    .register-info {
        display: none;
    }

    .register-card {
        max-width: 100%;
    }
}

@media (max-width: 768px) {
    .register-card {
        padding: 35px 25px;
    }

    .register-header {
        margin-bottom: 24px;
    }

    .register-header h2 {
        font-size: 1.4rem;
    }

    .form-row {
        grid-template-columns: 1fr;
        gap: 0;
    }

    .role-selector {
        grid-template-columns: 1fr;
    }

    .btn-primary {
        padding: 11px 20px;
        font-size: 0.9rem;
    }

    .register-form input[type="text"],
    .register-form input[type="email"],
    .register-form input[type="password"],
    .register-form input[type="number"],
    .register-form input[type="tel"],
    .register-form select,
    .register-form textarea {
        padding: 10px 12px;
        font-size: 0.88rem;
    }
}

@media (max-width: 480px) {
    .register-wrapper {
        min-height: auto;
    }

    .register-form-container {
        padding: 20px 10px;
        min-height: auto;
    }

    .register-card {
        padding: 25px 20px;
        border-radius: 8px;
    }

    .register-header h2 {
        font-size: 1.2rem;
    }

    .section-title {
        font-size: 0.95rem;
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
            wrapper.style.background = 'rgba(37, 99, 235, 0.1)';
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

output_path = r"c:\Users\Mahafuz\OneDrive\Desktop\Projects\Micro-Job Management\Micro-Job\templates\accounts\register.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(new_template)

print("✅ Complete registration page updated!")
print(f"File size: {len(new_template)} characters")
