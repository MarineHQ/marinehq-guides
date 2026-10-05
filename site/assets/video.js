/* Marine HQ Guides: silent looping clips. They play only while on screen, and not at all for
   visitors who have asked their device for reduced motion (those get the still frame and a play button). */
(function(){
  var vids=[].slice.call(document.querySelectorAll('video[data-auto]'));
  if(!vids.length)return;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce){vids.forEach(function(v){v.removeAttribute('autoplay');v.pause();v.controls=true;});return;}
  function play(v){var p=v.play();if(p&&p.catch)p.catch(function(){});}
  if(!('IntersectionObserver' in window)){vids.forEach(play);return;}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)play(e.target);else e.target.pause();});},{threshold:.2});
  vids.forEach(function(v){io.observe(v);});
})();
