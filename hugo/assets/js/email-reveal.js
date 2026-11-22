document.addEventListener('click', async (event) => {
  const button = event.target.closest('.email-reveal, .email-copy');
  if (!button) return;
  const contact = button.closest('.email-contact');
  const en = document.documentElement.lang.startsWith('en');
  const email = atob(contact.dataset.email);
  if (button.classList.contains('email-copy')) {
    try {
      await navigator.clipboard.writeText(email);
      button.textContent = en ? 'Copied' : 'コピーしました';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(contact.querySelector('a'));
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      const copied = document.execCommand('copy');
      button.textContent = copied ? (en ? 'Copied' : 'コピーしました') : (en ? 'Select the address to copy' : 'アドレスを選択してコピー');
    }
    return;
  }
  const result = contact.querySelector('.email-contact__result');
  const link = document.createElement('a');
  link.href = 'mailto:' + email;
  link.textContent = email;
  const copy = document.createElement('button');
  copy.type = 'button';
  copy.className = 'email-copy';
  copy.textContent = en ? 'Copy' : 'コピー';
  result.append(link, copy);
  button.hidden = true;
  link.focus();
});
