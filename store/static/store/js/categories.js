document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-bs-toggle="collapse"]').forEach(function (toggle) {
        toggle.addEventListener('click', function () {
            const icon = this.querySelector('.bi');
            if (icon) {
                icon.classList.toggle('bi-chevron-down');
                icon.classList.toggle('bi-chevron-up');
            }
        });
    });
});