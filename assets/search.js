document.documentElement.classList.add('js');
(function(){
var inp=document.getElementById('q'),res=document.getElementById('results'),data=null,sel=-1;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(){if(data)return Promise.resolve(data);return fetch('/search-index.json').then(function(r){return r.json()}).then(function(d){data=d;return d})}
function render(q){
 var m=data.filter(function(x){return (x.n+' '+x.d+' '+x.c+' '+(x.t||'')).toLowerCase().indexOf(q)>-1});
 m.sort(function(a,b){return (b.n.toLowerCase().indexOf(q)===0)-(a.n.toLowerCase().indexOf(q)===0)});
 m=m.slice(0,8);sel=-1;
 res.innerHTML=m.length?m.map(function(x){return '<a href="/agents/'+x.s+'/"><img src="https://www.google.com/s2/favicons?domain='+esc(x.h)+'&sz=64" alt="" width="22" height="22" loading="lazy"><b>'+esc(x.n)+'</b><span class="rc">'+esc(x.c)+'</span></a>'}).join(''):'<a href="/submit/"><b>No matches. List your agent free &rarr;</b></a>';
 res.style.display='block';
}
if(inp&&res){
 inp.addEventListener('focus',load,{once:true});
 inp.addEventListener('input',function(){var q=inp.value.toLowerCase().trim();if(q.length<2){res.style.display='none';return}load().then(function(){render(q)})});
 inp.addEventListener('keydown',function(e){
  var items=res.querySelectorAll('a');if(!items.length)return;
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();sel=(sel+(e.key==='ArrowDown'?1:-1)+items.length)%items.length;items.forEach(function(a,i){a.classList.toggle('on',i===sel)})}
  else if(e.key==='Enter'){e.preventDefault();location.href=(items[sel]||items[0]).href}
  else if(e.key==='Escape'){res.style.display='none';inp.blur()}
 });
 document.addEventListener('keydown',function(e){var t=document.activeElement.tagName;if(e.key==='/'&&t!=='INPUT'&&t!=='TEXTAREA'&&t!=='SELECT'){e.preventDefault();inp.focus()}});
 document.addEventListener('click',function(e){if(!e.target.closest('.search'))res.style.display='none'});
 var q0=new URLSearchParams(location.search).get('q');if(q0){inp.value=q0;load().then(function(){render(q0.toLowerCase())})}
}
if('IntersectionObserver' in window){
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('vis');io.unobserve(e.target)}})},{threshold:.06,rootMargin:'0px 0px -40px 0px'});
 document.querySelectorAll('.reveal').forEach(function(el){io.observe(el)});
}else{document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('vis')})}
})();
