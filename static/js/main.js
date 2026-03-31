document.addEventListener('DOMContentLoaded', () => {
    // --- Password Validation ---
    const passwordInput = document.getElementById('password');
    const signupBtn = document.getElementById('signupBtn');
    
    if (passwordInput) {
        const requirements = {
            upper: { regex: /[A-Z]/, element: document.getElementById('req-upper') },
            lower: { regex: /[a-z]/, element: document.getElementById('req-lower') },
            number: { regex: /[0-9]/, element: document.getElementById('req-num') },
            special: { regex: /[^A-Za-z0-9]/, element: document.getElementById('req-special') }
        };

        passwordInput.addEventListener('input', () => {
            const password = passwordInput.value;
            let isValid = true;

            for (const key in requirements) {
                const req = requirements[key];
                if (req.element) {
                    if (req.regex.test(password)) {
                        req.element.classList.remove('invalid');
                        req.element.classList.add('valid');
                        req.element.innerHTML = '<i class="fas fa-check-circle"></i> ' + req.element.innerText;
                    } else {
                        req.element.classList.remove('valid');
                        req.element.classList.add('invalid');
                        req.element.innerHTML = '<i class="fas fa-times-circle"></i> ' + req.element.innerText;
                        isValid = false;
                    }
                }
            }

            if (signupBtn) {
                signupBtn.disabled = !isValid;
                if (!isValid) {
                    signupBtn.style.opacity = '0.5';
                    signupBtn.style.cursor = 'not-allowed';
                } else {
                    signupBtn.style.opacity = '1';
                    signupBtn.style.cursor = 'pointer';
                }
            }
        });
    }

    // --- Dynamic Form Fields ---
    const roleSelect = document.getElementById('role');
    const dynamicFields = document.getElementById('dynamic-fields');

    if (roleSelect && dynamicFields) {
        const renderFields = () => {
            const role = roleSelect.value;
            dynamicFields.innerHTML = ''; // Clear fields
            
            if (role === 'student') {
                dynamicFields.innerHTML = `
                    <div class="form-group">
                        <label for="education">Education Level</label>
                        <select id="education" name="education" class="form-control" required>
                            <option value="">Select Level</option>
                            <option value="highschool">High School</option>
                            <option value="undergrad">Undergraduate</option>
                            <option value="postgrad">Postgraduate</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="skills">Skills you want to learn (Comma separated)</label>
                        <input type="text" id="skills" name="skills" class="form-control" placeholder="e.g. Python, UI Design..." required>
                    </div>
                `;
            } else if (role === 'mentor') {
                dynamicFields.innerHTML = `
                    <div class="form-group">
                        <label for="experience">Years of Experience</label>
                        <input type="number" id="experience" name="experience" class="form-control" placeholder="e.g. 5" required>
                    </div>
                    <div class="form-group">
                        <label for="skills">Skills you can teach (Comma separated)</label>
                        <input type="text" id="skills" name="skills" class="form-control" placeholder="e.g. React, Docker..." required>
                    </div>
                    <div class="form-group">
                        <label for="bio">Portfolio Link / Short Bio</label>
                        <textarea id="bio" name="bio" class="form-control" placeholder="Tell us about your background..." required></textarea>
                    </div>
                `;
            } else if (role === 'admin') {
                dynamicFields.innerHTML = `
                    <div class="form-group">
                        <label for="admin_code">Admin Verification Code</label>
                        <input type="password" id="admin_code" name="admin_code" class="form-control" placeholder="Enter strictly provided code" required>
                    </div>
                `;
            }
        };

        roleSelect.addEventListener('change', renderFields);
        
        // Initial render
        renderFields();
    }
});
