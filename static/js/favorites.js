document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("favorites-container");
  if (!container) return;

  container.addEventListener("click", async (e) => {
    if (e.target.classList.contains("btn-delete")) {
      const btn = e.target;
      const card = btn.closest(".card");
      const dealId = btn.dataset.id;

      if (!confirm("Удалить акцию из избранного?")) return;

      try {
        const response = await fetch(`/deal/${dealId}/favorite/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            });

        if (response.ok) {
          card.style.transition = "opacity 0.4s ease, transform 0.3s ease";
          card.style.opacity = "0";
          card.style.transform = "scale(0.95)";
          setTimeout(() => card.remove(), 400);

          // Проверяем, остались ли карточки
          setTimeout(() => {
            if (!container.querySelector(".card")) {
              container.innerHTML = "";
              const msg = document.createElement("p");
              msg.id = "empty-message";
              msg.className = "text-muted";
              msg.textContent = "У вас пока нет избранных акций";
              container.parentElement.appendChild(msg);
            }
          }, 500);
        } else {
          alert("Ошибка при удалении. Попробуйте снова.");
        }
      } catch (err) {
        console.error(err);
        alert("Ошибка при соединении с сервером.");
      }
    }
  });

  // Получение CSRF токена из cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});