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

  var comparableLookup = buildComparableLookup(comparables);

  var parcelsLayer = L.geoJSON(null, {
    style: { color: "#e67e22", weight: 2, fillOpacity: 0.15 },
    onEachFeature: function (feature, layer) {
      var refcat = feature.properties.refcat;
      var items = comparableLookup[refcat] || [];
      var popupContent = "<strong>" + refcat + "</strong>";

      items.forEach(function (c) {
        popupContent +=
          "<hr style='margin:4px 0'>" +
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
          "<b>Address:</b> " +
          c.address +
          "<br>" +
          '<a href="https://www.google.com/maps?q=' +
          c.lat +
          "," +
          c.lng +
          '" target="_blank" rel="noopener">Google Maps</a>' +
          (c.listings && c.listings.length
            ? "<br>" +
              c.listings
                .map(function (l) {
                  return (
                    '<a href="' +
                    l.url +
                    '" target="_blank" rel="noopener">' +
                    l.title +
                    "</a>"
                  );
                })
                .join("<br>")
            : "");
      });

      layer.bindPopup(popupContent, { maxHeight: 300 });
      bounds.extend(layer.getBounds());
      hasMarkers = true;
    },
  });

  propertiesLayer.addTo(map);
  parcelsLayer.addTo(map);

  L.control
    .layers(null, {
      Properties: propertiesLayer,
      "Cadastral Parcels": parcelsLayer,
    })
    .addTo(map);

  if (hasMarkers) {
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
  }

  loadComparablesTable();
  loadCadastralParcels(parcelsLayer);
}

function buildComparableLookup(comparables) {
  var lookup = {};
  comparables.forEach(function (c) {
    var refcat14 = c.reference.substring(0, 14);
    if (!lookup[refcat14]) lookup[refcat14] = [];
    lookup[refcat14].push(c);
  });
  return lookup;
}

async function loadComparablesTable() {
  var response = await fetch("/real-estate/api/comparables-table");
  var html = await response.text();
  document.getElementById("comparables-table").innerHTML = html;
}

async function loadCadastralParcels(parcelsLayer) {
  var response = await fetch("/real-estate/api/cadastral-parcels");
  var geojson = await response.json();
  parcelsLayer.addData(geojson);
}
