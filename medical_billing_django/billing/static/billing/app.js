(() => {
  const modal = document.getElementById("detailModal");
  const modalTitle = document.getElementById("modalTitle");
  const modalEyebrow = document.getElementById("modalEyebrow");
  const modalContent = document.getElementById("modalContent");
  const toast = document.getElementById("toast");

  function showToast(message, error = false) {
    toast.textContent = message;
    toast.className = `toast show${error ? " error" : ""}`;
    window.setTimeout(() => toast.className = "toast", 3200);
  }
  function openModal(title, eyebrow, content) {
    modalTitle.textContent = title;
    modalEyebrow.textContent = eyebrow;
    modalContent.replaceChildren(content);
    modal.hidden = false;
    document.body.classList.add("modal-open");
    document.getElementById("closeModal").focus();
  }
  function closeModal() {
    modal.hidden = true;
    document.body.classList.remove("modal-open");
  }
  function addField(parent, label, value) {
    const item = document.createElement("div");
    item.className = "detail-field";
    const name = document.createElement("span");
    name.className = "field-label";
    name.textContent = label;
    const val = document.createElement("strong");
    val.textContent = value === null || value === undefined || value === "" ? "—" : String(value);
    item.append(name, val);
    parent.append(item);
  }
  function detailGrid(data, fields) {
    const grid = document.createElement("div");
    grid.className = "detail-grid";
    fields.forEach(([label, key, prefix = ""]) => addField(grid, label, `${prefix}${data[key] ?? "—"}`));
    return grid;
  }
  async function getJSON(url) {
    const response = await fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}});
    if (!response.ok) throw new Error("Could not load this record.");
    return response.json();
  }
  document.querySelectorAll(".view-claim").forEach(button => {
    button.addEventListener("click", async () => {
      try {
        const d = await getJSON(`/claim/${button.dataset.claimId}/`);
        const wrap = document.createElement("div");
        const grid = detailGrid(d, [
          ["Patient", "patient"], ["Patient ID", "patient_id"], ["Insurance payer", "payer"],
          ["Member ID", "member_id"], ["Provider", "provider"], ["Service date", "service_date"],
          ["Procedure code", "procedure_code"], ["Procedure description", "procedure_description"],
          ["Quantity", "quantity"], ["Diagnosis codes", "diagnosis_codes"], ["Charge", "charge_amount", "$"],
          ["Adjustments", "adjustment_amount", "$"], ["Payments", "payment_amount", "$"],
          ["Current balance", "balance", "$"], ["Claim status", "status"], ["Batch number", "batch_number"]
        ]);
        const note = document.createElement("p");
        note.className = "document-note";
        note.textContent = `Reference notes: ${d.reference_note || "No reference note recorded."}`;
        wrap.append(grid, note);
        openModal(`CMS-1500 Claim Summary #${d.id}`, "CLAIM FORM VIEWER", wrap);
      } catch (e) { showToast(e.message, true); }
    });
  });
  document.querySelectorAll(".view-eob").forEach(button => {
    button.addEventListener("click", async () => {
      if (!button.dataset.eobId) return;
      try {
        const d = await getJSON(`/eob/${button.dataset.eobId}/`);
        const wrap = document.createElement("div");
        const grid = detailGrid(d, [
          ["EOB number", "eob_number"], ["Payer claim number", "payer_claim_number"],
          ["Patient", "patient"], ["Insurance payer", "payer"], ["Procedure code", "procedure_code"],
          ["Issued date", "issued_date"], ["Billed charge", "charge_amount", "$"],
          ["Allowed amount", "allowed_amount", "$"], ["Patient responsibility", "patient_responsibility", "$"],
          ["Adjustment code", "adjustment_code"], ["Denial / adjustment reason", "denial_reason"]
        ]);
        const note = document.createElement("p");
        note.className = "document-note";
        note.textContent = d.document_text || "No additional EOB explanation provided.";
        wrap.append(grid, note);
        openModal(`Explanation of Benefits · ${d.eob_number}`, "EOB DOCUMENT VIEWER", wrap);
      } catch (e) { showToast(e.message, true); }
    });
  });
  async function saveStatus(button) {
    const id = button.dataset.claimId;
    const select = document.querySelector(`.status-select[data-claim-id="${id}"]`);
    const formData = new FormData();
    formData.append("status", select.value);
    formData.append("csrfmiddlewaretoken", getCookie("csrftoken"));
    button.disabled = true;
    try {
      const response = await fetch(`/claim/${id}/status/`, {
        method: "POST", body: formData,
        headers: {"X-Requested-With": "XMLHttpRequest"}
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "Could not update status.");
      showToast(`Claim status updated to ${result.status}.`);
      window.setTimeout(() => window.location.reload(), 650);
    } catch (e) {
      showToast(e.message, true);
      button.disabled = false;
    }
  }
  document.querySelectorAll(".save-status").forEach(button => button.addEventListener("click", () => saveStatus(button)));

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const item of cookies) {
      const cookie = item.trim();
      if (cookie.startsWith(`${name}=`)) return decodeURIComponent(cookie.slice(name.length + 1));
    }
    return "";
  }

  const patientSelect = document.getElementById("notePatient");
  const claimSelect = document.getElementById("noteClaim");
  function filterNoteClaims() {
    const patientId = patientSelect.value;
    Array.from(claimSelect.options).forEach((option, index) => {
      if (index === 0) return;
      option.hidden = option.dataset.patient !== patientId;
      if (option.hidden && option.selected) claimSelect.value = "";
    });
  }
  patientSelect?.addEventListener("change", filterNoteClaims);
  filterNoteClaims();

  document.getElementById("openClaimBlank")?.addEventListener("click", () => {
    const wrap = document.createElement("div");
    const p = document.createElement("p");
    p.className = "document-note";
    p.textContent = "This demo provides a claim summary viewer inspired by a professional CMS-1500 workflow. It is not an official CMS form and does not submit claims to an insurer.";
    const grid = document.createElement("div");
    grid.className = "detail-grid";
    [["Patient information", "Fictional patient record"], ["Insurance", "Select a payer from the dropdown"], ["Service details", "Procedure code, service date and diagnosis"], ["Billing", "Charge, adjustment, payment and balance"]]
      .forEach(([label, value]) => addField(grid, label, value));
    wrap.append(p, grid);
    openModal("CMS-1500 Claim Form Guide", "CLAIM FORM VIEWER", wrap);
  });

  document.getElementById("closeModal").addEventListener("click", closeModal);
  document.getElementById("closeModalBottom").addEventListener("click", closeModal);
  modal.addEventListener("click", event => { if (event.target === modal) closeModal(); });
  document.addEventListener("keydown", event => { if (event.key === "Escape" && !modal.hidden) closeModal(); });
  document.getElementById("noteForm")?.addEventListener("submit", event => {
    const note = event.currentTarget.querySelector('textarea[name="note"]').value.trim();
    if (!note) { event.preventDefault(); showToast("Enter a note before saving.", true); }
  });
})();