const booksGrid = document.getElementById('books-grid');
const searchInput = document.getElementById('search-input');
let books = [];

function renderBooks(query = '') {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    const visibleBooks = books.filter((book) =>
        [book.title, book.author, book.isbn].some((value) =>
            value.toLocaleLowerCase().includes(normalizedQuery)
        )
    );

    booksGrid.replaceChildren();
    if (visibleBooks.length === 0) {
        const emptyMessage = document.createElement('p');
        emptyMessage.className = 'text-center text-secondary';
        emptyMessage.textContent = 'No se encontraron libros.';
        booksGrid.append(emptyMessage);
        return;
    }

    visibleBooks.forEach((book) => {
        const column = document.createElement('div');
        column.className = 'col-12 col-sm-6 col-lg-4';

        const card = document.createElement('article');
        card.className = 'card h-100 shadow-sm';

        const body = document.createElement('div');
        body.className = 'card-body';

        const availability = document.createElement('span');
        availability.className = `badge ${book.copies > 0 ? 'text-bg-success' : 'text-bg-secondary'} mb-2`;
        availability.textContent = book.copies > 0 ? `Disponibles: ${book.copies}` : 'No disponible';

        const title = document.createElement('h2');
        title.className = 'h5 card-title';
        title.textContent = book.title;

        const author = document.createElement('p');
        author.className = 'card-text';
        author.textContent = `Autor: ${book.author}`;

        const isbn = document.createElement('small');
        isbn.className = 'text-secondary';
        isbn.textContent = `ISBN: ${book.isbn}`;

        const detailLink = document.createElement('a');
        detailLink.className = 'btn btn-outline-primary btn-sm mt-3';
        detailLink.href = `/libro/${encodeURIComponent(book.id)}`;
        detailLink.textContent = 'Ver detalles';
        detailLink.setAttribute('aria-label', `Ver detalles de ${book.title}`);

        body.append(availability, title, author, isbn, detailLink);
        card.append(body);
        column.append(card);
        booksGrid.append(column);
    });
}

async function loadCatalog() {
    try {
        const response = await fetch('/catalogo');
        if (!response.ok) throw new Error(`Error al cargar catálogo (${response.status})`);
        books = await response.json();
        renderBooks(searchInput.value);
    } catch (error) {
        booksGrid.textContent = 'No se pudo cargar el catálogo.';
        console.error(error);
    }
}

searchInput.addEventListener('input', () => renderBooks(searchInput.value));
loadCatalog();
