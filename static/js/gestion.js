const feedback = document.getElementById('feedback');

async function sendForm(url, payload, successMessage) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        feedback.textContent = response.ok
            ? successMessage
            : (result.error || 'No se pudo completar la operación.');
        feedback.className = `alert alert-${response.ok ? 'success' : 'danger'}`;
        return response.ok;
    } catch (error) {
        feedback.textContent = 'No se pudo conectar con el servidor.';
        feedback.className = 'alert alert-danger';
        console.error(error);
        return false;
    }
}

document.getElementById('book-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const saved = await sendForm('/api/books', {
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        isbn: document.getElementById('isbn').value,
        copies: document.getElementById('copies').value
    }, 'Libro guardado correctamente.');
    if (saved) event.target.reset();
});

document.getElementById('user-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const saved = await sendForm('/api/users', {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    }, 'Usuario creado correctamente.');
    if (saved) event.target.reset();
});
