/* Marine HQ — WhatsApp chat widget. Self-contained: drop this file in, or paste the whole thing inside a
   <script> tag in Duda's HTML widget. Visitor types a message → their WhatsApp opens on 0439 748 387 with it. */
(function(){
  var NUMBER="61439748387", NAME="Marine HQ", SUB="Typically replies within the hour",
      GREETING="Hi, welcome to Marine HQ. How can we help with your yacht?";
  var css='#mhqwa{position:fixed;right:18px;bottom:18px;z-index:9999;font-family:Inter,"Helvetica Neue",Arial,sans-serif}'
  +'#mhqwa .b{width:60px;height:60px;border-radius:50%;background:#25D366;border:0;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.25);display:flex;align-items:center;justify-content:center;position:relative}'
  +'#mhqwa .b svg{width:32px;height:32px;fill:#fff}#mhqwa .b i{position:absolute;top:2px;right:2px;width:12px;height:12px;border-radius:50%;background:#e87722;border:2px solid #fff}'
  +'#mhqwa .p{position:absolute;right:0;bottom:74px;width:min(340px,calc(100vw - 36px));background:#fff;border-radius:14px;box-shadow:0 16px 48px rgba(22,34,63,.28);overflow:hidden;display:none}'
  +'#mhqwa.open .p{display:block}#mhqwa .h{background:#16223f;color:#fff;padding:14px 16px;display:flex;align-items:center;gap:12px}'
  +'#mhqwa .h b{display:block;font-size:15px}#mhqwa .h span{font-size:12px;color:#c9d3e6}#mhqwa .h .x{margin-left:auto;background:none;border:0;color:#fff;font-size:22px;cursor:pointer;line-height:1}'
  +'#mhqwa .lg{width:36px;height:36px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:#16223f;font-weight:800;font-size:11px;letter-spacing:.5px}'
  +'#mhqwa .m{background:#eef1f8;padding:16px}#mhqwa .g{background:#fff;border-radius:10px;padding:12px 14px;font-size:14px;color:#1f2740;line-height:1.5;max-width:88%;box-shadow:0 1px 2px rgba(0,0,0,.06)}'
  +'#mhqwa .f{padding:12px}#mhqwa textarea{width:100%;box-sizing:border-box;border:1px solid #cfd6e2;border-radius:10px;padding:10px 12px;font:inherit;font-size:14px;resize:none;height:64px}'
  +'#mhqwa .s{display:block;width:100%;margin-top:10px;background:#25D366;color:#fff;border:0;border-radius:10px;padding:13px;font-weight:700;font-size:15px;cursor:pointer}'
  +'#mhqwa .n{text-align:center;font-size:11px;color:#7c8699;margin-top:8px}';
  var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
  var w=document.createElement('div');w.id='mhqwa';w.innerHTML=
   '<div class="p" role="dialog" aria-label="Chat with Marine HQ on WhatsApp"><div class="h"><div class="lg">HQ</div><div><b>'+NAME+'</b><span>'+SUB+'</span></div><button class="x" aria-label="Close">&times;</button></div>'
  +'<div class="m"><div class="g">'+GREETING+'</div></div>'
  +'<div class="f"><textarea placeholder="Type your message" aria-label="Your message"></textarea><button class="s">Send on WhatsApp</button><div class="n">Opens WhatsApp on your phone or computer</div></div></div>'
  +'<button class="b" aria-label="Chat on WhatsApp"><svg viewBox="0 0 32 32"><path d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.4.7 4.7 1.9 6.7L3 29l6.9-2.1c1.9 1 4 1.6 6.1 1.6 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23c-1.9 0-3.8-.5-5.4-1.5l-.4-.2-4.1 1.2 1.3-3.9-.3-.4c-1.1-1.7-1.7-3.7-1.7-5.7C5.4 9.9 10.2 5.2 16 5.2s10.6 4.7 10.6 10.5S21.8 26 16 26zm5.8-7.8c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2-.2.3-.8 1-1 1.2-.2.2-.4.2-.7.1-.3-.2-1.3-.5-2.5-1.6-.9-.8-1.6-1.8-1.8-2.1-.2-.3 0-.5.1-.6l.5-.6c.2-.2.2-.3.3-.5.1-.2.1-.4 0-.6-.1-.2-.7-1.7-1-2.3-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.3 1.4 3.5c.2.2 2.4 3.6 5.8 5 .8.3 1.4.6 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.6-.4z"/></svg><i></i></button>';
  document.body.appendChild(w);
  var ta=w.querySelector('textarea');
  w.querySelector('.b').onclick=function(){w.classList.toggle('open');if(w.classList.contains('open'))ta.focus();};
  w.querySelector('.x').onclick=function(){w.classList.remove('open');};
  w.querySelector('.s').onclick=function(){
    var t=(ta.value||'').trim()||'Hi Marine HQ, I have a question about my yacht.';
    t+='\n\n(Sent from '+location.href+')';
    window.open('https://wa.me/'+NUMBER+'?text='+encodeURIComponent(t),'_blank','noopener');
  };
})();
