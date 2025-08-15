document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('searchInput');
    const resultsBox = document.getElementById('searchResults');

    input.addEventListener('input', function () {
        const query = this.value.trim();
        resultsBox.innerHTML = '';

        if (query.length > 1) {
            fetch(`/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultsBox.innerHTML = '';
                    if (data.results.length === 0) {
                        resultsBox.innerHTML = '<div class="list-group-item text-muted">Нет результатов</div>';
                    }
                    data.results.forEach(item => {
                        const link = document.createElement('a');
                        link.href = `/product/${item.id}/`;
                        link.classList.add('list-group-item', 'list-group-item-action');
                        link.textContent = item.name;
                        resultsBox.appendChild(link);
                    });
                });
        }
    });

    document.addEventListener('click', function (event) {
        if (!resultsBox.contains(event.target) && event.target !== input) {
            resultsBox.innerHTML = '';
        }
    });
});
