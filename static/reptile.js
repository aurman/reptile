var map = L.map('map', {
    minZoom: 0,
    maxZoom: 10,
    crs: L.CRS.Simple,
    center: [0, 0],
    zoom: 4
});

var southWest = map.unproject([0, 8*90910], map.getMaxZoom());
var northEast = map.unproject([8*33706, 0], map.getMaxZoom());
map.setMaxBounds(new L.LatLngBounds(southWest, northEast));

L.tileLayer('ESP_011273_1925_RED.JP2/{z}/{x}/{y}.png', {
    attribution: 'NASA/JPL/University of Arizona',
}).addTo(map);
