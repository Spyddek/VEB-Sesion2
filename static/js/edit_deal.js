document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("edit-modal");
  const openBtn = document.getElementById("edit-deal-btn");
  const closeBtn = document.querySelector(".close");
  const saveBtn = document.getElementById("save-deal-btn");

  if (!openBtn) return;

  openBtn.addEventListener("click", () => (modal.style.display = "block"));
  closeBtn.addEventListener("click", () => (modal.style.display = "none"));
  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  saveBtn.addEventListener("click", async () => {
    const data = {
      title: document.getElementById("title-input").value,
      price_original: document.getElementById("price-original-input").value,
      price_discount: document.getElementById("price-discount-input").value,
      expires_at: document.getElementById("expires-at-input").value,
      image_url: document.getElementById("image-url-input").value,
      description: document.getElementById("desc-input").value,
    };

    const response = await fetch(window.location.pathname + "update_all/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      const updated = await response.json();
      modal.style.display = "none";

      // Обновление данных на странице без перезагрузки
      document.getElementById("deal-title").textContent = data.title;
      document.getElementById("deal-old").textContent = data.price_original + " ₽";
      document.getElementById("deal-new").textContent = data.price_discount + " ₽";
      document.getElementById("deal-expire").innerHTML =
        `<i class="fa fa-calendar"></i> Действует до ${data.expires_at.split("-").reverse().join(".")}`;
      document.getElementById("deal-image").src = data.image_url;
      document.getElementById("description-text").textContent = data.description;
    } else {
      const errorData = await response.json();
      alert("Ошибка при сохранении: " + (errorData.message || "Неизвестная ошибка"));
    }
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      for (const cookie of document.cookie.split(";")) {
        const c = cookie.trim();
        if (c.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(c.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});