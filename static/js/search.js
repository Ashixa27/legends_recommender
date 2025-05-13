
document.addEventListener('DOMContentLoaded', () => {

    // Get references to the input box and suggestions container
    const input = document.getElementById('search_input');
    const suggestions = document.getElementById('suggestions');

    // Listen for any input changes
    input.addEventListener('input', async () => {
        const query = input.value.trim();

        // If input is empty, clear suggestions
        if (!query) {
            suggestions.innerHTML = '';
            return;
        }

        try {
            // Make an request to get search results
            const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const results = await res.json();

            suggestions.innerHTML = results.map(name =>
                `<li onclick="location.href='/champion/${name}'">${name}</li>`
            ).join('');
        } catch (err) {
            console.error('Search failed:', err);
        }
    });
});