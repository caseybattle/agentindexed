
// search
fetch('/search-index.json').then(r=>r.json()).then(d=>{
const inp=document.getElementById('q'),res=document.getElementById('results');
if(!inp)return;
inp.addEventListener('input',()=>{
const q=inp.value.toLowerCase().trim();
if(q.length<2){res.style.display='none';return}
const m=d.filter(x=>(x.n+' '+x.d+' '+x.c).toLowerCase().includes(q)).slice(0,8);
res.innerHTML=m.length?m.map(x=>`<a href="/agents/${x.s}/"><img src="https://www.google.com/s2/favicons?domain=${x.h}&sz=64" onerror="this.style.display='none'"><b>${x.n}</b><span class="rc">${x.c}</span></a>`).join(''):'<a href="/submit/"><b>No matches — be the first to list one →</b></a>';
res.style.display='block'});
document.addEventListener('click',e=>{if(!e.target.closest('.search'))res.style.display='none'})});
// reveal on scroll
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('vis');io.unobserve(e.target)}}),{threshold:.08});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
