const API_BASE = "https://yiwprm0rbi.execute-api.eu-north-1.amazonaws.com/prod";

function showLoading(id, loading = true) {
  const el = document.getElementById(id);
  el.innerHTML = loading ? "<li>Loading...</li>" : "";
}

async function fetchDaily() {
  showLoading("dailyList");
  try {
    const res = await fetch(`${API_BASE}/violations/daily`);
    const data = await res.json();
    const ul = document.getElementById("dailyList");
    ul.innerHTML = "";
    data.forEach(v => {
      ul.innerHTML += `<li>🚗 ${v.license_plate} – ${v.reason} @ ${v.timestamp}</li>`;
    });
  } catch (err) {
    alert("Failed to load daily violations.");
    console.error(err);
  }
}

async function fetchWeekly() {
  showLoading("weeklyList");
  try {
    const res = await fetch(`${API_BASE}/violations/weekly`);
    const data = await res.json();
    const ul = document.getElementById("weeklyList");
    ul.innerHTML = "";
    data.forEach(v => {
      ul.innerHTML += `<li> ${v.license_plate} → ${v.totalViolations} violations this week</li>`;
    });
  } catch (err) {
    alert("Failed to load weekly reports.");
    console.error(err);
  }
}

async function submitViolation() {
  const plateNumber = document.getElementById("plateNumber").value;
  const reason = document.getElementById("reason").value;

  if (!plateNumber || !reason) {
    alert("Please enter both license plate and reason.");
    return;
  }

  const body = { license_plate: plateNumber, reason };

  try {
    const res = await fetch(`${API_BASE}/violations/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();
    if (res.ok) {
      alert("Violation recorded:\nFouls: " + data.fouls);
      document.getElementById("plateNumber").value = "";
      document.getElementById("reason").value = "";
      fetchDaily();
    } else {
      alert("Failed: " + data.error);
    }
  } catch (err) {
    alert("Error submitting violation.");
    console.error(err);
  }
}

async function sendDailyEmail() {
  try {
    const res = await fetch(`${API_BASE}/violations/daily_summary`, { method: "POST" });
    const data = await res.json();
    if (res.ok) alert(" Daily summary email sent.");
    else alert("Failed: " + data.message || "Unknown error.");
  } catch (err) {
    alert("Error sending daily email.");
    console.error(err);
  }
}

async function sendWeeklyEmail() {
  try {
    const res = await fetch(`${API_BASE}/violations/weekly_summary`, { method: "POST" });
    const data = await res.json();
    if (res.ok) alert(" Weekly summary email sent.");
    else alert("Failed: " + data.message || "Unknown error.");
  } catch (err) {
    alert("Error sending weekly email.");
    console.error(err);
  }
}

async function searchDriver() {
  const plate = document.getElementById("searchPlate").value.trim();
  if (!plate) return alert("Please enter a license plate");

  try {
    const res = await fetch(`${API_BASE}/drivers/${plate}`);
    const data = await res.json();

    if (!res.ok) {
      alert("Driver not found");
      return;
    }

    const el = document.getElementById("driverDetails");
    el.innerHTML = `
      <p><strong>Name:</strong> ${data.name}</p>
      <p><strong>Role:</strong> ${data.role}</p>
      <p><strong>Phone:</strong> ${data.phone}</p>
      <p><strong>Email:</strong> ${data.email}</p>
    `;
  } catch (err) {
    console.error(err);
    alert("Failed to fetch driver data");
  }
}

async function sendNotification() {
  const plate = document.getElementById("searchPlate").value.trim();
  if (!plate) return alert("Please search for a driver first");

  try {
    const res = await fetch(`${API_BASE}/notify/${plate}`, { method: "POST" });
    const data = await res.json();
    alert(res.ok ? "Notification sent" : `Failed: ${data.message}`);
  } catch (err) {
    console.error(err);
    alert("Error sending notification");
  }
}

function openReportModal() {
  document.getElementById("reportModal").style.display = "block";
}

function closeReportModal() {
  document.getElementById("reportModal").style.display = "none";
}

async function submitDetailedReport() {
  const plate = document.getElementById("searchPlate").value.trim();
  const reason = document.getElementById("violationReason").value;
  const file = document.getElementById("violationImage").files[0];

  if (!plate || !reason || !file) {
    alert("Please fill all fields and select an image");
    return;
  }

  const formData = new FormData();
  formData.append("license_plate", plate);
  formData.append("reason", reason);
  formData.append("image", file);

  try {
    const res = await fetch(`${API_BASE}/violations/report_full`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (res.ok) {
      alert("Violation report submitted");
      closeReportModal();
    } else {
      alert("Failed: " + data.message);
    }
  } catch (err) {
    console.error(err);
    alert("Error submitting detailed report");
  }
}

