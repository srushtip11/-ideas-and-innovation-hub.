// College Idea Innovation Hub
// Common website interactions

document.addEventListener("DOMContentLoaded", function () {

    console.log("College Idea Innovation Hub is ready!");

    // Automatically hide messages after 6 seconds.
    const messages = document.querySelectorAll(
        ".success-message, .error-message"
    );

    messages.forEach(function (message) {

        setTimeout(function () {
            message.style.transition = "opacity 0.5s ease";
            message.style.opacity = "0";

            setTimeout(function () {
                message.style.display = "none";
            }, 500);

        }, 6000);

    });

});