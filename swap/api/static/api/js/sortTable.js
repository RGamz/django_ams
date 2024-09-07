function sortTable(tableId, col, type) {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.rows).slice(1); // Convert HTMLCollection to Array and skip the header row
    const fragment = document.createDocumentFragment();
    let sorted = false;

    rows.sort((a, b) => {
        let x = a.querySelectorAll('th, td')[col];
        let y = b.querySelectorAll('th, td')[col];

        if (x.dataset.sortValue) {
            x = x.dataset.sortValue;
            y = y.dataset.sortValue;
        } else {
            x = x.innerHTML;
            y = y.innerHTML;
        }

        if (type === 'number') {
            x = Number(x);
            y = Number(y);
        }

        if (x > y) {
            sorted = true;
            return 1;
        } else if (x < y) {
            sorted = true;
            return -1;
        }
        return 0;
    });

    if (!sorted) return;

    rows.forEach(row => fragment.appendChild(row));
    table.tBodies[0].appendChild(fragment);
}

function reverseTable(tableId) {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.rows).slice(1).reverse(); // Convert HTMLCollection to Array, skip header, and reverse
    const fragment = document.createDocumentFragment();

    rows.forEach(row => fragment.appendChild(row));
    table.tBodies[0].appendChild(fragment);
}

function getHeaders(table) {
    const head = table.querySelector('thead');
    return Array.from(head.querySelectorAll('th'));
}

function addSortListeners(tables) {
    tables.forEach(table => {
        const headers = getHeaders(table);
        const tableId = table.id;

        headers.forEach((header, i) => {
            const sortType = header.dataset.type || '';

            header.addEventListener('click', (event) => {
                const target = event.target;
                const sorted = (target.dataset.sorted === 'true');

                if (sorted) {
                    reverseTable(tableId);
                    const arrow = target.querySelector('span');
                    arrow.innerHTML = (arrow.innerHTML === '↑') ? '↓' : '↑';
                } else {
                    headers.forEach(header2 => {
                        const arrow = header2.querySelector('span');
                        if (arrow) {
                            arrow.innerHTML = '';
                        } else {
                            header2.innerHTML += '<span></span>';
                        }
                        header2.dataset.sorted = false;
                    });

                    sortTable(tableId, i, sortType);
                    target.dataset.sorted = true;
                    target.querySelector('span').innerHTML = '↓';
                }
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const TABLES = Array.from(document.getElementsByClassName('sortTable'));
    addSortListeners(TABLES);
});
