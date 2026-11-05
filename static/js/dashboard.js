const feedback = document.getElementById('feedback');

function showMessage(message, isError = false) {
    feedback.textContent = message;
    feedback.className = `alert alert-${isError ? 'danger' : 'success'}`;
}

document.querySelectorAll('.borrow-book').forEach((button) => {
    button.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/loans', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ book_id: button.dataset.bookId })
            });
            const result = await response.json();
            if (!response.ok) {
                showMessage(result.error || 'No se pudo registrar el préstamo.', true);
                return;
            }
            window.location.reload();
        } catch (error) {
            showMessage('No se pudo conectar con el servidor.', true);
            console.error(error);
        }
    });
});

document.querySelectorAll('.return-loan').forEach((button) => {
    button.addEventListener('click', async () => {
        try {
            const response = await fetch(`/api/loans/${button.dataset.loanId}/return`, { method: 'PUT' });
            const result = await response.json();
            if (!response.ok) {
                showMessage(result.error || 'No se pudo registrar la devolución.', true);
                return;
            }
            window.location.reload();
        } catch (error) {
            showMessage('No se pudo conectar con el servidor.', true);
            console.error(error);
        }
    });
});
