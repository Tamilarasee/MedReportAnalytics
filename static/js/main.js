document.addEventListener("DOMContentLoaded", function () {
  // Highlight evidence phrases inside report
  function highlightEvidence() {
    const evidenceElements = document.querySelectorAll(".evidence-text");
    const reportText = document.querySelector(".report-text-full");

    if (!reportText || evidenceElements.length === 0) return;

    let html = reportText.innerHTML;

    evidenceElements.forEach((evidenceEl) => {
      const evidence = evidenceEl.textContent.trim();
      if (evidence) {
        const regex = new RegExp(
          evidence.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"),
          "gi"
        );
        html = html.replace(
          regex,
          `<span class="highlighted-evidence">$&</span>`
        );
      }
    });

    reportText.innerHTML = html;
  }

  highlightEvidence();
});
