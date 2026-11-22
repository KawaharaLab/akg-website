document.querySelectorAll('.home-slideshow').forEach(root=>{
  const slides=[...root.querySelectorAll('.home-slide')],pause=root.querySelector('[data-slide-pause]');
  if(slides.length<2||!pause)return;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let index=0,timer=null,playing=root.dataset.autoplay==='true'&&!reduced.matches,hover=false;
  pause.hidden=false;
  function schedule(){clearTimeout(timer);timer=null;pause.textContent=playing?pause.dataset.pause:pause.dataset.play;if(playing&&!hover&&!document.hidden)timer=setTimeout(()=>show(index+1),Math.max(5,Number(root.dataset.interval)||7)*1000);}
  function show(next){index=(next+slides.length)%slides.length;slides.forEach((s,i)=>{s.hidden=i!==index;});const img=slides[(index+1)%slides.length].querySelector('img');img.loading='eager';schedule();}
  let pointerIntent=null;
  pause.addEventListener('pointerdown',()=>{pointerIntent=!playing;});
  pause.addEventListener('pointercancel',()=>{pointerIntent=null;});
  pause.addEventListener('keydown',()=>{pointerIntent=null;});
  pause.onclick=()=>{playing=pointerIntent===null?!playing:pointerIntent;pointerIntent=null;schedule();};
  root.addEventListener('pointerenter',()=>{hover=true;schedule();});root.addEventListener('pointerleave',()=>{hover=false;schedule();});
  root.addEventListener('focusin',()=>{playing=false;schedule();});
  root.addEventListener('focusout',()=>setTimeout(schedule,0));
  document.addEventListener('visibilitychange',schedule);
  reduced.addEventListener('change',()=>{if(reduced.matches)playing=false;schedule();});
  show(0);
});
