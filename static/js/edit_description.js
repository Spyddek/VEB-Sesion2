document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("edit-modal");
  const openBtn = document.getElementById("edit-desc-btn");
  const closeBtn = document.querySelector(".close");
  const saveBtn = document.getElementById("save-desc-btn");
  const textarea = document.getElementById("desc-input");
  const descText = document.getElementById("description-text");

  if (!openBtn) return;

  // открыть модалку
  openBtn.addEventListener("click", () => {
    modal.style.display = "block";
  });

  // закрыть
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });

  // сохранить изменения
  saveBtn.addEventListener("click", async () => {
    const newText = textarea.value.trim();
    if (!newText) return alert("Описание не может быть пустым!");

    const response = await fetch(window.location.pathname + "update_description/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ description: newText }),
    });

    if (response.ok) {
      descText.textContent = newText;
      modal.style.display = "none";
    } else {
      alert("Ошибка при сохранении. Проверьте права доступа.");
    }
  });

  // csrf helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});