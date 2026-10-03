/* Marine HQ Guides — numbered maps. Each .map element carries its points as JSON in data-map.
   A point may have "at":[lat,lon] = where its number sits, joined to the true position by a leader line
   (used where marinas sit too close together to number in place). */
(function(){
  function init(){
    if(!window.L) return;
    document.querySelectorAll('.map[data-map]').forEach(function(el){
      var d=JSON.parse(el.getAttribute('data-map')), pts=d.points, all=[];
      var m=L.map(el,{scrollWheelZoom:false,dragging:!L.Browser.mobile,zoomSnap:1,attributionControl:true});
      m.attributionControl.setPrefix(false);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:17,attribution:'&copy; OpenStreetMap contributors'}).addTo(m);
      if(d.line){
        L.polyline(pts.map(function(p){return [p.lat,p.lon]}),{color:'#e87722',weight:3,opacity:.95,dashArray:'2 8',lineCap:'round'}).addTo(m);
      }
      pts.forEach(function(p){
        var here=[p.lat,p.lon], at=p.at||here, kind=p.kind||'std';
        all.push(here); all.push(at);
        if(p.at){
          L.polyline([here,at],{color:'#1a2b5c',weight:1.5,opacity:.8}).addTo(m);
        }
        L.circleMarker(here,{radius:p.at?4:0,color:'#fff',weight:1.5,fillColor:'#1a2b5c',fillOpacity:1}).addTo(m);
        var icon=L.divIcon({className:'',html:'<span class="pin k-'+kind+'">'+p.n+'</span>',iconSize:[28,28],iconAnchor:[14,14]});
        L.marker(at,{icon:icon,title:p.name,keyboard:false}).addTo(m)
          .bindPopup('<b>'+p.n+' · '+p.name+'</b>'+(p.note?'<br>'+p.note:''));
      });
      m.fitBounds(L.latLngBounds(all),{padding:[34,34]});
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
