<template>
  <div ref="mapDiv" style="width: 100%; height: 30vh" />
</template>

<script>
import {ref, onMounted, toRef, watch} from 'vue'
import { Loader } from '@googlemaps/js-api-loader'

export default {
  name: 'GoogleMap',
  props: {
    markers: { type: Array, default: [] },
    mapOptions: { type: Object, default: {center: {lat: 39, lng:  -100}, zoom: 4}}
  },
  setup(props) {
    const markersArray = ref([]);
    let map = ref(null);
    const loader = new Loader({ apiKey: import.meta.env.VUE_APP_GOOGLE_MAPS_API_KEY });
    const mapDiv = ref(null);
    const googleRef = ref(null);

    async function loadMap() {
      await loader.load();
      googleRef.value = google;
      map = new google.maps.Map(mapDiv.value, props.mapOptions);
    }

    function createMarker(google, data) {
      const latLng = new google.maps.LatLng(data.latitude, data.longitude);
      return new google.maps.Marker({ position: latLng, map });
    }

    function createInfoWindow(marker, content) {
      const infoWindow = new google.maps.InfoWindow({ content });
      marker.addListener("click", () => infoWindow.open({ anchor: marker, map }));
    }

    function clearMarkers() {
      markersArray.value.forEach((marker) => marker.setMap(null))
      markersArray.value = [];
    }

    async function addMarkers() {
      if (!googleRef.value) await loadMap()
      clearMarkers();

      props.markers.forEach((markerData) => {
        const marker = createMarker(googleRef.value, markerData);
        const content = `
          <h5>${markerData.name}</h5>
          <p><b>${markerData.city ? markerData.city : ""}
                 ${markerData.state ? markerData.state : ""}
                 ${markerData.country ? markerData.country : ""}
          </b></p>
          <p>${markerData.description}</p>
          <p><a href="/sites/${markerData.id}">View data for this site</a>`;
        createInfoWindow(marker, content);
        markersArray.value.push(marker);
      });
    }

    watch(() => props.markers, () => addMarkers())
    onMounted(async () => await loadMap())

    return { mapDiv };
  },
}
</script>
