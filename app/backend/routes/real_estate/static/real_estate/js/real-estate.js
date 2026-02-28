async function initMap() {
  var map = L.map("map").setView([0, 0], 3);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  var response = await fetch("/real-estate/api/properties");
  var properties = await response.json();

  if (!properties || properties.length === 0) return;

  var bounds = L.latLngBounds();

  properties.forEach(function (p) {
    var popupContent =
      "<strong>" +
      p.title +
      "</strong><br>" +
      "<b>Type:</b> " +
      p.re_type +
      "<br>" +
      "<b>Price:</b> " +
      p.price.toLocaleString() +
      " €<br>" +
      "<b>Surface:</b> " +
      p.surface.toLocaleString() +
      " m²<br>" +
      (p.price_per_m2
        ? "<b>€/m²:</b> " + p.price_per_m2.toLocaleString() + "<br>"
        : "") +
      "<b>Address:</b> " +
      p.address;

    var marker = L.marker([p.lat, p.lng]).addTo(map);
    marker.bindPopup(popupContent);
    bounds.extend([p.lat, p.lng]);
  });

  map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
}
