document.addEventListener('DOMContentLoaded', () => {
    // Basic interactions
    console.log('Skillify loaded.');

    // Auto-dismiss flashes
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300); // Wait for transition
        }, 5000); // 5s visible
    });

    // Mobile nav toggle (placeholder logic)
    // Add real toggle if you want a burger menu in base.html
});
