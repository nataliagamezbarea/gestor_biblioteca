const feedback = document.getElementById('feedback');
const booksTableBody = document.getElementById('books-table-body');
const usersTableBody = document.getElementById('users-table-body');
const loansTableBody = document.getElementById('loans-table-body');
const addBookModal = new bootstrap.Modal(document.getElementById('add-book-modal'));
const addUserModal = new bootstrap.Modal(document.getElementById('add-user-modal'));
const addLoanModal = new bootstrap.Modal(document.getElementById('add-loan-modal'));
const editBookModal = new bootstrap.Modal(document.getElementById('edit-book-modal'));
const editUserModal = new bootstrap.Modal(document.getElementById('edit-user-modal'));

function showFeedback(message, isError = false) {
    feedback.textContent = message;
    feedback.className = `alert alert-${isError ? 'danger' : 'success'}`;
}

async function requestJson(url, options = {}) {
    const response = await fetch(url, options);
    const result = await response.json();
    return { response, result };
}

async function loadBooks() {
    try {
        const { response, result } = await requestJson('/api/books');
        if (!response.ok) {
            throw new Error(result.error || 'No se pudieron cargar los libros.');
        }

        booksTableBody.replaceChildren();
        if (result.length === 0) {
            const row = booksTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 5;
            cell.className = 'text-center text-secondary py-4';
            cell.textContent = 'Todavía no hay libros registrados.';
            document.getElementById('loan-book').replaceChildren(new Option('No hay libros disponibles', ''));
            return;
        }

        const loanBookSelect = document.getElementById('loan-book');
        loanBookSelect.replaceChildren(new Option('Selecciona un libro', ''));
        result.filter((book) => book.copies > 0).forEach((book) => {
            loanBookSelect.add(new Option(`${book.title} (${book.copies} disponibles)`, book.id));
        });
        if (loanBookSelect.options.length === 1) {
            loanBookSelect.options[0].textContent = 'No hay libros disponibles';
        }

        result.forEach((book) => {
            const row = booksTableBody.insertRow();
            [book.title, book.author, book.isbn, book.copies].forEach((value) => {
                row.insertCell().textContent = value;
            });

            const actions = row.insertCell();
            actions.className = 'text-nowrap';

            const editButton = document.createElement('button');
            editButton.type = 'button';
            editButton.className = 'btn btn-sm btn-outline-primary me-2';
            editButton.dataset.action = 'edit';
            editButton.dataset.bookId = book.id;
            editButton.textContent = 'Editar';

            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'btn btn-sm btn-outline-danger';
            deleteButton.dataset.action = 'delete';
            deleteButton.dataset.bookId = book.id;
            deleteButton.dataset.bookTitle = book.title;
            deleteButton.textContent = 'Eliminar';

            actions.append(editButton, deleteButton);
        });
    } catch (error) {
        showFeedback(error.message || 'No se pudo conectar con el servidor.', true);
        console.error(error);
    }
}

async function loadUsers() {
    try {
        const { response, result } = await requestJson('/api/users');
        if (!response.ok) throw new Error(result.error || 'No se pudieron cargar los usuarios.');

        usersTableBody.replaceChildren();
        const loanUserSelect = document.getElementById('loan-user');
        loanUserSelect.replaceChildren(new Option('Selecciona un usuario', ''));
        result.forEach((user) => {
            loanUserSelect.add(new Option(`${user.name} (${user.email})`, user.id));

            const row = usersTableBody.insertRow();
            [user.name, user.email, user.role].forEach((value) => {
                row.insertCell().textContent = value;
            });
            const actions = row.insertCell();
            actions.className = 'text-nowrap';

            const editButton = document.createElement('button');
            editButton.type = 'button';
            editButton.className = 'btn btn-sm btn-outline-primary me-2';
            editButton.dataset.action = 'edit-user';
            editButton.dataset.userId = user.id;
            editButton.textContent = 'Editar';

            const deleteButton = document.createElement('button');
            deleteButton.type = 'button';
            deleteButton.className = 'btn btn-sm btn-outline-danger';
            deleteButton.dataset.action = 'delete-user';
            deleteButton.dataset.userId = user.id;
            deleteButton.dataset.userName = user.name;
            deleteButton.textContent = 'Eliminar';

            actions.append(editButton, deleteButton);
        });

        if (result.length === 0) {
            const row = usersTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 4;
            cell.className = 'text-center text-secondary py-4';
            cell.textContent = 'Todavía no hay usuarios registrados.';
        }
    } catch (error) {
        showFeedback(error.message || 'No se pudo conectar con el servidor.', true);
        console.error(error);
    }
}

async function loadLoans() {
    try {
        const { response, result } = await requestJson('/api/loans');
        if (!response.ok) throw new Error(result.error || 'No se pudo cargar el historial.');

        loansTableBody.replaceChildren();
        if (result.length === 0) {
            const row = loansTableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 6;
            cell.className = 'text-center text-secondary py-4';
            cell.textContent = 'Todavía no hay préstamos registrados.';
            return;
        }

        result.forEach((loan) => {
            const row = loansTableBody.insertRow();
            [
                loan.book_title,
                loan.user_name,
                loan.loan_date,
                loan.return_date || '—',
                loan.status
            ].forEach((value) => row.insertCell().textContent = value);
            const actions = row.insertCell();
            if (loan.status === 'Activo') {
                const returnButton = document.createElement('button');
                returnButton.type = 'button';
                returnButton.className = 'btn btn-sm btn-outline-success';
                returnButton.dataset.action = 'return-loan';
                returnButton.dataset.loanId = loan.id;
                returnButton.textContent = 'Registrar devolución';
                actions.append(returnButton);
            } else {
                actions.textContent = '—';
            }
        });
    } catch (error) {
        showFeedback(error.message || 'No se pudo conectar con el servidor.', true);
        console.error(error);
    }
}

async function sendForm(url, payload, successMessage) {
    try {
        const { response, result } = await requestJson(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        showFeedback(response.ok
            ? successMessage
            : (result.error || 'No se pudo completar la operación.'), !response.ok);
        return response.ok;
    } catch (error) {
        showFeedback('No se pudo conectar con el servidor.', true);
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
    if (saved) {
        event.target.reset();
        addBookModal.hide();
        await loadBooks();
        await loadLoans();
    }
});

document.getElementById('user-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const saved = await sendForm('/api/users', {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    }, 'Usuario creado correctamente.');
    if (saved) {
        event.target.reset();
        addUserModal.hide();
        await loadUsers();
    }
});

booksTableBody.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    const bookId = button.dataset.bookId;
    if (button.dataset.action === 'edit') {
        try {
            const { response, result } = await requestJson('/api/books');
            if (!response.ok) throw new Error(result.error || 'No se pudieron cargar los libros.');
            const book = result.find((item) => String(item.id) === bookId);
            if (!book) throw new Error('El libro ya no existe.');

            document.getElementById('edit-book-id').value = book.id;
            document.getElementById('edit-title').value = book.title;
            document.getElementById('edit-author').value = book.author;
            document.getElementById('edit-isbn').value = book.isbn;
            document.getElementById('edit-copies').value = book.copies;
            editBookModal.show();
        } catch (error) {
            showFeedback(error.message || 'No se pudo cargar el libro.', true);
        }
        return;
    }

    if (button.dataset.action === 'delete') {
        if (!window.confirm(`¿Eliminar el libro "${button.dataset.bookTitle}"?`)) return;
        try {
            const { response, result } = await requestJson(`/api/books/${bookId}`, { method: 'DELETE' });
            if (!response.ok) {
                showFeedback(result.error || 'No se pudo eliminar el libro.', true);
                return;
            }
            showFeedback(result.message || 'Libro eliminado correctamente.');
            await loadBooks();
        } catch (error) {
            showFeedback('No se pudo conectar con el servidor.', true);
            console.error(error);
        }
    }
});

usersTableBody.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    const userId = button.dataset.userId;

    if (button.dataset.action === 'edit-user') {
        try {
            const { response, result } = await requestJson('/api/users');
            if (!response.ok) throw new Error(result.error || 'No se pudieron cargar los usuarios.');
            const user = result.find((item) => String(item.id) === userId);
            if (!user) throw new Error('El usuario ya no existe.');
            document.getElementById('edit-user-id').value = user.id;
            document.getElementById('edit-user-name').value = user.name;
            document.getElementById('edit-user-email').value = user.email;
            document.getElementById('edit-user-role').value =
                user.role === 'Administrador' ? 'Administrador' : 'Usuario';
            document.getElementById('edit-user-password').value = '';
            editUserModal.show();
        } catch (error) {
            showFeedback(error.message || 'No se pudo cargar el usuario.', true);
        }
        return;
    }

    if (button.dataset.action === 'delete-user') {
        if (!window.confirm(`¿Eliminar al usuario "${button.dataset.userName}"?`)) return;
        try {
            const { response, result } = await requestJson(`/api/users/${userId}`, { method: 'DELETE' });
            if (!response.ok) {
                showFeedback(result.error || 'No se pudo eliminar el usuario.', true);
                return;
            }
            showFeedback(result.message || 'Usuario eliminado correctamente.');
            await loadUsers();
        } catch (error) {
            showFeedback('No se pudo conectar con el servidor.', true);
            console.error(error);
        }
    }
});

document.getElementById('edit-user-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const userId = document.getElementById('edit-user-id').value;
    const payload = {
        name: document.getElementById('edit-user-name').value,
        email: document.getElementById('edit-user-email').value,
        role: document.getElementById('edit-user-role').value,
        password: document.getElementById('edit-user-password').value
    };
    try {
        const { response, result } = await requestJson(`/api/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            showFeedback(result.error || 'No se pudo actualizar el usuario.', true);
            return;
        }
        editUserModal.hide();
        showFeedback(result.message || 'Usuario actualizado correctamente.');
        await loadUsers();
    } catch (error) {
        showFeedback('No se pudo conectar con el servidor.', true);
        console.error(error);
    }
});

document.getElementById('edit-book-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const bookId = document.getElementById('edit-book-id').value;
    try {
        const { response, result } = await requestJson(`/api/books/${bookId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: document.getElementById('edit-title').value,
                author: document.getElementById('edit-author').value,
                isbn: document.getElementById('edit-isbn').value,
                copies: document.getElementById('edit-copies').value
            })
        });
        if (!response.ok) {
            showFeedback(result.error || 'No se pudo actualizar el libro.', true);
            return;
        }
        editBookModal.hide();
        showFeedback(result.message || 'Libro actualizado correctamente.');
        await loadBooks();
        await loadLoans();
    } catch (error) {
        showFeedback('No se pudo conectar con el servidor.', true);
        console.error(error);
    }
});

document.getElementById('loan-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const saved = await sendForm('/api/loans', {
        user_id: document.getElementById('loan-user').value,
        book_id: document.getElementById('loan-book').value
    }, 'Préstamo registrado correctamente.');
    if (saved) {
        event.target.reset();
        addLoanModal.hide();
        await loadBooks();
        await loadLoans();
    }
});

loansTableBody.addEventListener('click', async (event) => {
    const button = event.target.closest('button[data-action="return-loan"]');
    if (!button) return;
    try {
        const { response, result } = await requestJson(`/api/loans/${button.dataset.loanId}/return`, {
            method: 'PUT'
        });
        if (!response.ok) {
            showFeedback(result.error || 'No se pudo registrar la devolución.', true);
            return;
        }
        showFeedback(result.message || 'Devolución registrada correctamente.');
        await loadBooks();
        await loadLoans();
    } catch (error) {
        showFeedback('No se pudo conectar con el servidor.', true);
        console.error(error);
    }
});

loadBooks();
loadUsers();
loadLoans();
