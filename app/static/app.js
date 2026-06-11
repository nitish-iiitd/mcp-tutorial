const output = document.getElementById('output');
const statusEl = document.getElementById('status');

function show(value) {
  output.textContent = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
}

function setStatus(value) { statusEl.textContent = value; }

async function postJson(url, payload) {
  setStatus('Calling...');
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  setStatus(response.ok ? 'Success' : 'Failed');
  if (!response.ok) throw data;
  return data;
}

async function loadCatalog() {
  try {
    setStatus('Loading catalog...');
    const response = await fetch('/api/mcp/catalog');
    const data = await response.json();
    setStatus('Catalog loaded');
    show(data);
  } catch (error) { setStatus('Failed'); show(error); }
}

async function callTool() {
  try {
    const name = document.getElementById('toolName').value;
    const args = JSON.parse(document.getElementById('toolArgs').value || '{}');
    show(await postJson('/api/mcp/tools/call', { name, arguments: args }));
  } catch (error) { setStatus('Failed'); show(error); }
}

async function readResource() {
  try {
    const uri = document.getElementById('resourceUri').value;
    show(await postJson('/api/mcp/resources/read', { uri }));
  } catch (error) { setStatus('Failed'); show(error); }
}

async function getPrompt() {
  try {
    const name = document.getElementById('promptName').value;
    const args = JSON.parse(document.getElementById('promptArgs').value || '{}');
    show(await postJson('/api/mcp/prompts/get', { name, arguments: args }));
  } catch (error) { setStatus('Failed'); show(error); }
}

loadCatalog();
