var comparableIcon = L.icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

async function initMap() {
  var map = L.map("map").setView([0, 0], 3);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);

  var [properties, comparables] = await Promise.all([
    fetch("/real-estate/api/properties").then(function (r) {
      return r.json();
    }),
    fetch("/real-estate/api/comparables").then(function (r) {
      return r.json();
    }),
  ]);

  var bounds = L.latLngBounds();
  var hasMarkers = false;

  var propertiesLayer = L.layerGroup();
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

    L.marker([p.lat, p.lng]).bindPopup(popupContent).addTo(propertiesLayer);
    bounds.extend([p.lat, p.lng]);
    hasMarkers = true;
  });

  var comparablesLayer = L.layerGroup();
  comparables.forEach(function (c) {
    var popupContent =
      "<strong>" +
      c.reference +
      "</strong><br>" +
      "<b>Surface:</b> " +
      c.surface.toLocaleString() +
      " m²<br>" +
      (c.avg_price
        ? "<b>Avg Price:</b> " + c.avg_price.toLocaleString() + " €<br>"
        : "") +
      (c.avg_price_per_m2
        ? "<b>Avg €/m²:</b> " + c.avg_price_per_m2.toLocaleString() + "<br>"
        : "") +
      (c.listings_count
        ? "<b>Listings:</b> " + c.listings_count + "<br>"
        : "") +
      "<b>Address:</b> " + c.address +
      (c.listings && c.listings.length
        ? "<br>" + c.listings.map(function (l) {
            return '<a href="' + l.url + '" target="_blank" rel="noopener">' + l.title + "</a>";
          }).join("<br>")
        : "");

    L.marker([c.lat, c.lng], { icon: comparableIcon })
      .bindPopup(popupContent)
      .addTo(comparablesLayer);
    bounds.extend([c.lat, c.lng]);
    hasMarkers = true;
  });

  propertiesLayer.addTo(map);
  comparablesLayer.addTo(map);

  L.control
    .layers(null, {
      Properties: propertiesLayer,
      Comparables: comparablesLayer,
    })
    .addTo(map);

  if (hasMarkers) {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
  }
}
