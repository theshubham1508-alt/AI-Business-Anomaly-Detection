(() => {
  const menuToggle = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");

  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("is-open");
      menuToggle.setAttribute("aria-expanded", String(open));
    });

    document.addEventListener("click", (event) => {
      if (
        sidebar.classList.contains("is-open") &&
        !sidebar.contains(event.target) &&
        !menuToggle.contains(event.target)
      ) {
        sidebar.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  const analysisForms = document.querySelectorAll("[data-analysis-form]");
  const analysisProgress = document.getElementById("analysisProgress");
  const asyncNotices = document.getElementById("asyncNotices");

  const showAnalysisNotice = (message, category) => {
    if (!asyncNotices) return;
    asyncNotices.replaceChildren();
    const notice = document.createElement("div");
    notice.className = `flash flash-${category}`;
    const icon = document.createElement("span");
    icon.textContent = category === "success" ? "✓" : "!";
    notice.append(icon, document.createTextNode(message));
    asyncNotices.append(notice);
    asyncNotices.hidden = false;
  };

  analysisForms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (form.dataset.submitting === "true") return;
      form.dataset.submitting = "true";
      if (asyncNotices) asyncNotices.hidden = true;
      if (analysisProgress) analysisProgress.hidden = false;

      const buttons = document.querySelectorAll("[data-analysis-button]");
      const originalLabels = new Map();
      buttons.forEach((button) => {
        originalLabels.set(button, button.innerHTML);
        button.disabled = true;
        button.classList.add("is-loading");
        button.innerHTML =
          '<span class="button-spinner" aria-hidden="true"></span><span>Analyzing dataset…</span>';
      });

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: new FormData(form),
          headers: {
            Accept: "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
        });
        const contentType = response.headers.get("content-type") || "";
        const result = contentType.includes("application/json")
          ? await response.json()
          : {
              ok: false,
              message: `The analysis service returned HTTP ${response.status}. Check the Flask server logs.`,
            };
        if (!response.ok || !result.ok) {
          throw new Error(result.message || `Analysis failed (${response.status}).`);
        }
        showAnalysisNotice(result.message, "success");
        window.location.assign(result.redirect_url);
      } catch (error) {
        const message =
          error instanceof Error && error.message !== "Failed to fetch"
            ? error.message
            : "Could not reach the analysis service. Check that Flask is running, then try again.";
        showAnalysisNotice(message, "error");
        if (analysisProgress) analysisProgress.hidden = true;
        form.dataset.submitting = "false";
        buttons.forEach((button) => {
          button.disabled = false;
          button.classList.remove("is-loading");
          button.innerHTML = originalLabels.get(button);
        });
      }
    });
  });

  const fileInput = document.getElementById("dataset-file");
  const dropZone = document.getElementById("dropZone");
  const fileName = document.getElementById("fileName");
  if (!fileInput || !dropZone || !fileName) return;

  const updateFileName = (file) => {
    fileName.textContent = file ? file.name : "Drop a CSV here or browse files";
  };
  fileInput.addEventListener("change", () => updateFileName(fileInput.files[0]));
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add("drag-over");
    });
  });
  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.remove("drag-over");
    });
  });
  dropZone.addEventListener("drop", (event) => {
    const [file] = event.dataTransfer.files;
    if (file) {
      const transfer = new DataTransfer();
      transfer.items.add(file);
      fileInput.files = transfer.files;
      updateFileName(file);
    }
  });
})();
