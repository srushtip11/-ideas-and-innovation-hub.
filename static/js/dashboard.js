// Dashboard interactions

document.addEventListener("DOMContentLoaded", function () {

    // Confirm before submitting a faculty review.
    const reviewForms = document.querySelectorAll(
        'form[action*="idea-review"]'
    );

    reviewForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const statusField = form.querySelector(
                'select[name="status"]'
            );

            if (!statusField || !statusField.value) {
                return;
            }

            const confirmed = window.confirm(
                "Are you sure you want to submit this idea review?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

    // Add a visual interaction to dashboard cards.
    const cards = document.querySelectorAll(
        ".stat-card, .idea-card"
    );

    cards.forEach(function (card) {

        card.addEventListener("mouseenter", function () {
            card.classList.add("card-active");
        });

        card.addEventListener("mouseleave", function () {
            card.classList.remove("card-active");
        });

    });

});