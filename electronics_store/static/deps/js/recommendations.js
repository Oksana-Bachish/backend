(function() {
    const listContainer = document.getElementById("recommendations-list");

    if (!listContainer) return;

    const productSlug = listContainer.getAttribute("data-product-slug");

    let apiBase = 'http://127.0.0.1:8085'

    if (window.location.hostname !== '127.0.0.1' && window.location.hostname !== 'localhost') {
        apiBase = 'https://electronics24.store';
    }

    const url = apiBase + "/recommendations/" + productSlug;

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error("FastAPI сервис недоступен");
            return response.json();
        })
        .then(data => {
            if (!data || data.length === 0) {
                document.querySelector(".recommendations-section").style.display = "none";
                return;
            }

            listContainer.innerHTML = "";

            data.forEach(item => {
                listContainer.innerHTML += `
                    <div class="col">
                        <div class="card h-100 shadow-sm" style="border-radius: 8px; overflow: hidden;">
                            <a href="/products/product/${item.slug}/" class="text-decoration-none text-dark">
                                <img src="/media/${item.image}" class="card-img-top p-3" style="height: 180px; object-fit: contain;" alt="${item.name}">
                                <div class="card-body text-center">
                                    <h5 class="card-title fw-bold fs-6 text-truncate" title="${item.name}">${item.name}</h5>
                                    <p class="card-text text-success fw-bold m-0">${item.price} р.</p>
                                </div>
                            </a>
                        </div>
                    </div>
                `;
            });
        })
        .catch(error => {
            console.error("Ошибка микросервиса рекомендаций:", error);
            const section = document.querySelector(".recommendations-section");
            if (section) section.style.display = "none";
        });
})();
