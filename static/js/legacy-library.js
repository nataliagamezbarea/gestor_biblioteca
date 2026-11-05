async function submitJsonForm(url, payload, successMessage) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        if (!response.ok) {
            alert(result.error || 'No se pudo completar la operación.');
            return false;
        }
        alert(successMessage);
        return true;
    } catch (error) {
        alert('No se pudo conectar con el servidor.');
        console.error(error);
        return false;
    }
}

document.getElementById('book-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const saved = await submitJsonForm('/api/books', {
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        isbn: document.getElementById('isbn').value,
        copies: document.getElementById('copies').value
    }, 'Libro registrado.');
    if (saved) event.target.reset();
});

document.getElementById('user-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const saved = await submitJsonForm('/api/users', {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    }, 'Usuario registrado.');
    if (saved) event.target.reset();
});
