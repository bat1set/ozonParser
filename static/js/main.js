function showAddProduct() {
    document.getElementById('add-product-modal').classList.add('show');
}

function hideAddProduct() {
    document.getElementById('add-product-modal').classList.remove('show');
}

function addProduct() {
    const url = document.getElementById('product-url').value;
    if (!url) {
        alert('Пожалуйста, введите URL товара');
        return;
    }

    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = '<div class="loader"></div><p>Добавление товара...</p>';
    document.body.appendChild(loadingOverlay);

    fetch('/add_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Ошибка при добавлении товара: ' + data.error);
        }
    })
    .catch(error => {
        alert('Ошибка при добавлении товара: ' + error);
    })
    .finally(() => {
        document.body.removeChild(loadingOverlay);
        hideAddProduct();
    });
}

function updateProduct(name) {
    const loadingOverlay = document.querySelector('.loading-overlay');
    loadingOverlay.classList.remove('hidden');

    fetch(`/update_product/${encodeURIComponent(name)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка при обновлении товара: ' + data.error);
            }
        })
        .catch(error => {
            alert('Ошибка при обновлении товара: ' + error);
        })
        .finally(() => {
            loadingOverlay.classList.add('hidden');
        });
}

function showPriceHistory(name) {
    const modal = document.getElementById('price-history-modal');
    const graph = document.getElementById('price-history-graph');
    modal.classList.add('show');

    fetch(`/get_price_history/${encodeURIComponent(name)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                graph.innerHTML = `<img src="data:image/png;base64,${data.graph}" alt="График цен">`;
            } else {
                graph.innerHTML = 'Ошибка при загрузке графика: ' + data.error;
            }
        })
        .catch(error => {
            graph.innerHTML = 'Ошибка при загрузке графика: ' + error;
        });
}

function hidePriceHistory() {
    document.getElementById('price-history-modal').classList.remove('show');
}

function toggleDeleteMode() {
    const checkboxes = document.querySelectorAll('.delete-checkbox');
    const deleteControls = document.getElementById('delete-controls');

    checkboxes.forEach(checkbox => {
        checkbox.classList.toggle('hidden');
    });

    deleteControls.classList.toggle('hidden');

    const cards = document.querySelectorAll('.product-card');
    cards.forEach(card => {
        card.style.cursor = card.style.cursor === 'default' ? 'pointer' : 'default';
    });
}

function deleteSelectedProducts() {
    const selectedProducts = [];
    document.querySelectorAll('.product-checkbox:checked').forEach(checkbox => {
        selectedProducts.push(checkbox.closest('.product-card').dataset.name);
    });

    if (selectedProducts.length === 0) {
        alert('Выберите товары для удаления');
        return;
    }

    if (!confirm('Вы уверены, что хотите удалить выбранные товары?')) {
        return;
    }

    fetch('/delete_products', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ products: selectedProducts }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Ошибка при удалении товаров');
        }
    })
    .catch(error => {
        alert('Ошибка при удалении товаров: ' + error);
    });
}

function cancelDelete() {
    toggleDeleteMode();
}

function updateAllProducts() {
    if (!confirm('Обновить данные всех товаров?')) {
        return;
    }

    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = '<div class="loader"></div><p>Обновление всех товаров...</p>';
    document.body.appendChild(loadingOverlay);

    fetch('/update_all_products')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка при обновлении товаров: ' + data.error);
            }
        })
        .catch(error => {
            alert('Ошибка при обновлении товаров: ' + error);
        })
        .finally(() => {
            document.body.removeChild(loadingOverlay);
        });
}

function productClick(event, name) {
    if (!event.target.closest('.delete-checkbox')) {
        window.location.href = `/product/${encodeURIComponent(name)}`;
    }
}