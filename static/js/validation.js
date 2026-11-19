// Form validation for College Idea Innovation Hub

document.addEventListener("DOMContentLoaded", function () {

    const forms = document.querySelectorAll("form[data-validate]");

    forms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const password = form.querySelector(
                'input[name="password"]'
            );

            // Check password length if the form has a password field.
            if (password && password.value.length < 8) {

                event.preventDefault();

                alert("Password must contain at least 8 characters.");

                password.focus();

                return;
            }

            // Check that required fields are filled in.
            const requiredFields = form.querySelectorAll("[required]");

            for (const field of requiredFields) {

                if (!field.value.trim()) {

                    event.preventDefault();

                    alert("Please fill in all required fields.");

                    field.focus();

                    return;
                }
            }

        });

    });

});