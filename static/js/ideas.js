// Idea search functionality

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("ideaSearch");

    const ideaCards = document.querySelectorAll(".searchable-idea");

    const noResults = document.getElementById("noSearchResults");

    // Stop if this page does not contain the idea search box.
    if (!searchInput) {
        return;
    }

    searchInput.addEventListener("input", function () {

        const searchText = searchInput.value
            .trim()
            .toLowerCase();

        let visibleCount = 0;

        ideaCards.forEach(function (card) {

            const title = card.dataset.title || "";

            const category = card.dataset.category || "";

            const matches =
                title.includes(searchText) ||
                category.includes(searchText);

            card.style.display = matches ? "" : "none";

            if (matches) {
                visibleCount++;
            }

        });

        // Show a message if no cards match the search.
        if (noResults) {
            noResults.hidden = visibleCount !== 0;
        }

    });

});