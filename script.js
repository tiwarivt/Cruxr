async function generateNotes() {
  const url = document.getElementById('youtubeUrl').value;
  const status = document.getElementById('status');
  const output = document.getElementById('output');

  if (!url.trim()) {
    status.textContent = "❌ Please enter a valid YouTube URL.";
    return;
  }

  status.textContent = "⏳ Processing, please wait...";
  output.textContent = "";

  try {
    const response = await fetch("https://cruxr.onrender.com/api/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ youtubeUrl: url })
    });

    const data = await response.json();

    if (response.ok) {
      status.textContent = "✅ Notes generated successfully!";
      output.textContent = data.notes;
    } else {
      status.textContent = `❌ Error: ${data.error}`;
    }
  } catch (err) {
    status.textContent = `❌ Failed to connect to the backend.`;
  }
}
