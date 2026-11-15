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

document.querySelector('.mobile-contents')?.addEventListener('click', (event) => {
  if (event.target.closest('a[href^="#"]')) event.currentTarget.open = false;
});

async function renderLessonDiagrams(diagrams) {
  let mermaid;
  try {
    ({ default: mermaid } = await import('https://cdn.jsdelivr.net/npm/mermaid@12.3.0/dist/mermaid.esm.min.mjs'));
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      suppressErrorRendering: true,
      htmlLabels: false,
      fontFamily: 'system-ui, sans-serif',
      theme: 'base',
      themeVariables: {
        background: '#f8faff',
        primaryColor: '#edf1ff',
        primaryTextColor: '#191b42',
        primaryBorderColor: '#6366c5',
        secondaryColor: '#eaf3ff',
        tertiaryColor: '#f2ecff',
        lineColor: '#5147a7',
        noteBkgColor: '#f3edff',
        noteTextColor: '#241b4d',
        edgeLabelBackground: '#f0efff',
      },
      flowchart: { useMaxWidth: false },
      sequence: { useMaxWidth: false },
    });
  } catch {
    return;
  }

  for (const [index, diagram] of diagrams.entries()) {
    const source = diagram.querySelector('.diagram-source');
    const view = diagram.querySelector('.diagram-view');
    try {
      const { svg } = await mermaid.render(`lesson-diagram-${index + 1}`, source.querySelector('code').textContent);
      view.innerHTML = svg;
      const nativeWidth = view.querySelector('svg').viewBox.baseVal.width;
      view.style.setProperty('--diagram-native-width', `${Math.ceil(nativeWidth)}px`);
      if (nativeWidth > 360) {
        const readableWidth = Math.min(620, Math.round(nativeWidth * 0.76));
        view.style.setProperty('--diagram-readable-width', `${readableWidth}px`);
      }
      const title = view.querySelector('title')?.textContent.trim();
      if (title) view.setAttribute('aria-label', title);
      view.hidden = false;
      source.hidden = true;
    } catch {
      // The source and prose remain available when a diagram cannot render.
    }
  }
}

const diagrams = document.querySelectorAll('[data-mermaid-diagram]');
if (diagrams.length) renderLessonDiagrams(diagrams);
