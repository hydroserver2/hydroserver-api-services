let map;
function initMap(){
    const markers = JSON.parse(document.getElementById('markers').textContent);
    let options = {center: {lat: 40, lng: -105}, zoom: 4,}
    map = new google.maps.Map(document.getElementById("map"), options);

    for(let marker of markers)
        addMarker(marker)

    initLocationClicking()
}

let markers = [];
let currentInfoWindow;
function addMarker(data){
    let latLng = new google.maps.LatLng(data['latitude'], data['longitude']);
    let marker = new google.maps.Marker({position: latLng, map: map});

    const content =
        `<h5> ${data["name"]} </h5>
         <p><b> 
                ${data['city'] ? data['city'] : ''} 
                ${data['state']? data['state'] : ''} 
                ${data['country']? data['country'] : ''}
        </b></p>
        <p>${data['description']}</p>
        <p><a href="${data["site_url"]}">View data for this site</a>`

    const info_window = new google.maps.InfoWindow({content: content});

    marker.addListener("click", () => {
        if (currentInfoWindow) currentInfoWindow.close();
        info_window.open({anchor: marker, map});
        currentInfoWindow = info_window;
    });

    markers.push(marker);
}


let new_marker = null;
function initLocationClicking() {
  const elevator = new google.maps.ElevationService();
  const geocoder = new google.maps.Geocoder();

  map.addListener("click", (mapsMouseEvent) => {
    elevator.getElevationForLocations({'locations': [mapsMouseEvent.latLng]})
    .then(({results}) => {
        if (!results[0]) return console.log("No results found");

        document.getElementById("id_latitude").value = mapsMouseEvent.latLng.lat().toFixed(6);
        document.getElementById("id_longitude").value = mapsMouseEvent.latLng.lng().toFixed(6);
        document.getElementById("id_elevation").value = Math.round(results[0].elevation);

        if (new_marker) new_marker.setMap(null);
        new_marker = new google.maps.Marker({position: mapsMouseEvent.latLng, map: map });

        geocoder.geocode({'location': mapsMouseEvent.latLng}, function(results, status) {
            if (status !== 'OK') return console.log("Geocoder failed due to: " + status);
            if (!results[0]) return console.log("No results found");

            const nearest_town = results[0].address_components.filter(component => {
                return component.types.includes('locality') ||
                       component.types.includes('administrative_area_level_1') ||
                       component.types.includes('country');
            });

            let city, state, country = '';
            nearest_town.forEach(component => {
                if (component.types.includes('locality')) city = component.long_name;
                if (component.types.includes('administrative_area_level_1')) state = component.short_name;
                if (component.types.includes('country')) country = component.short_name;
            });
            document.getElementById("id_nearest_town").value = city;
            document.getElementById("id_state").value = state;
            document.getElementById("id_country").value = country;
        });
    })
    .catch((e) => console.log("Elevation service failed due to: " + e))
  });
}
