const copyButtons = document.querySelectorAll('button[data-copy-code]');

if (copyButtons.length && navigator.clipboard) {
  const status = document.createElement('div');
  status.className = 'sr-only';
  status.setAttribute('role', 'status');
  document.body.append(status);

  for (const button of copyButtons) {
    const code = button.nextElementSibling?.querySelector('code');
    if (!code) continue;

    const label = button.textContent.trim();
    let reset;
    button.hidden = false;
    button.addEventListener('click', async () => {
      window.clearTimeout(reset);
      try {
        await navigator.clipboard.writeText(code.textContent.replace(/\n$/, ''));
        button.textContent = 'Copied';
        status.textContent = 'Code copied to the clipboard.';
      } catch {
        button.textContent = 'Copy failed';
        status.textContent = 'Copy failed. Select the code to copy it manually.';
      }

      reset = window.setTimeout(() => {
        button.textContent = label;
        status.textContent = '';
      }, 2100);
    });
  }
}
