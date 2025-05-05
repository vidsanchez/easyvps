// installer_banner.js - Copia el comando al portapapeles y muestra feedback

document.addEventListener('DOMContentLoaded', () => {
  const block = document.getElementById('installer-copy-block');
  const copied = document.getElementById('installer-copied');
  if (!block) return;
  block.addEventListener('click', () => {
    const code = block.querySelector('code').innerText.trim();
    navigator.clipboard.writeText(code).then(() => {
      if (copied) {
        copied.style.display = 'inline';
        setTimeout(() => { copied.style.display = 'none'; }, 1700);
      }
    });
  });
  block.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      block.click();
      e.preventDefault();
    }
  });
});
