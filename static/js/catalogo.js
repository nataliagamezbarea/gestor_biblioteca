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
        const card = document.createElement('article');
        card.className = 'book-card';

        const cover = document.createElement('div');
        cover.className = 'book-cover';

        const initial = document.createElement('span');
        initial.className = 'book-cover-initial';
        initial.textContent = book.title.charAt(0).toLocaleUpperCase();

        cover.append(initial);

        if (book.cover_url) {
            const image = document.createElement('img');
            image.alt = `Portada de ${book.title}`;
            image.loading = 'lazy';
            image.src = book.cover_url;
            image.addEventListener('error', () => image.remove());
            cover.append(image);
        }

        const body = document.createElement('div');
        body.className = 'book-body';

        const title = document.createElement('h2');
        title.className = 'book-title';
        title.title = book.title;
        title.textContent = book.title;

        const author = document.createElement('p');
        author.className = 'book-author';
        author.title = book.author;
        author.textContent = book.author;

        const isbn = document.createElement('small');
        isbn.className = 'book-isbn';
        isbn.textContent = `ISBN: ${book.isbn}`;

        const availability = document.createElement('span');
        availability.className = `badge book-availability ${book.copies > 0 ? 'text-bg-success' : 'text-bg-secondary'}`;
        availability.textContent = book.copies > 0 ? `Disponibles: ${book.copies}` : 'No disponible';

        body.append(title, author, isbn, availability);
        card.append(cover, body);
        booksGrid.append(card);
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
