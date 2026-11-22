document.querySelectorAll('.publication-copy').forEach(button=>{
  button.hidden=false;
  button.addEventListener('click',async()=>{
    const citation=button.closest('details').querySelector('.publication-citation__text');
    const status=button.nextElementSibling;
    try{await navigator.clipboard.writeText(citation.textContent);status.textContent=button.dataset.done;}
    catch{const range=document.createRange();range.selectNodeContents(citation);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);status.textContent=button.dataset.failed;}
  });
});
