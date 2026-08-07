// clever_terminal_boot.js
// Adds an in‑page console that allows running code through the sandbox endpoint.
// Toggle with Ctrl+` in the browser.

(() => {
  const root = document.createElement('div');
  root.id = 'clever-terminal';
  root.style.cssText = `
    position: fixed; right: 0; top: 0; height: 100%; width: 440px;
    background: rgba(0,0,0,.85); color:#00e0ff; font: 12px monospace;
    border-left: 2px solid #00e0ff; z-index: 10000; display:none; padding:10px; box-sizing: border-box;`;
  root.innerHTML = `
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
      <strong style="font-size:14px;">Clever Sandbox Console</strong>
      <span style="opacity:.7;">(Ctrl+\\\` to toggle)</span>
    </div>
    <textarea id="clever-code" spellcheck="false" style="
      width:100%;height:160px;background:#0b1c1f;color:#c7f8ff;border:1px solid #07343a;
      outline:none;padding:8px;resize:vertical;border-radius:6px;"></textarea>
    <div style="margin:8px 0;">
      <button id="clever-run" style="padding:6px 10px;background:#00e0ff;color:#001316;border:none;border-radius:6px;cursor:pointer;">
        Run
      </button>
      <span id="clever-status" style="margin-left:8px;opacity:.8;"></span>
    </div>
    <pre id="clever-out" style="
      background:#071a1e;border:1px solid #07343a;border-radius:6px;padding:8px;
      height: calc(100% - 250px); overflow:auto; white-space:pre-wrap;"></pre>
  `;
  document.body.appendChild(root);

  const panel = root;
  const codeInput = root.querySelector('#clever-code');
  const output = root.querySelector('#clever-out');
  const runBtn = root.querySelector('#clever-run');
  const status = root.querySelector('#clever-status');

  function toggle() { panel.style.display = panel.style.display === 'none' ? 'block' : 'none'; }
  window.addEventListener('keydown', (e) => { if (e.ctrlKey && e.key === '`') toggle(); });

  runBtn.addEventListener('click', async () => {
    status.textContent = 'running…';
    output.textContent = '';
    try {
      const response = await fetch('/sandbox/run', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({code: codeInput.value})
      });
      const json = await response.json();
      output.textContent =
        (json.ok ? '' : '⚠️ Error\n') +
        (json.stdout || '') +
        (json.stderr ? '\n' + json.stderr : '');
      status.textContent = json.ok ? 'done' : 'error';
    } catch (err) {
      output.textContent = 'Failed to call /sandbox/run: ' + err;
      status.textContent = 'error';
    }
  });

  // Sample starter code to demonstrate the console
  codeInput.value = "print('Hello from Clever sandbox!')\\nfor i in range(3): print('tick', i)";
})();
