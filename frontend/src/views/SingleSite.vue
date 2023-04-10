<template>
  <div v-if="isLoaded">
    <GoogleMap :markers="[thing]" :mapOptions="mapOptions"/>

    <div class="site-information-container">
      <h2 class="site-information-title">Site Information</h2>
      <div v-if="isAuthenticated && thing && thing.owns_thing" >
        <v-btn color="green">Edit Site Information</v-btn>
        <v-btn color="red-darken-3" style="margin-left: 1rem">Delete Site</v-btn>
      </div>
      <div v-else-if="isAuthenticated && thing && !thing.owns_thing">
        <input class="follow-checkbox" type="checkbox" :checked="followsThing" @change="updateFollow"/>
        <label>Follow Thing</label>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="table-container">
        <table>
          <tr>
            <td><i class="fas fa-info-circle"></i> Name</td>
            <td>{{ thing?.name }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-id-badge"></i> ID</td>
            <td>{{ thing?.id }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-file-alt"></i> Description</td>
            <td>{{ thing?.description }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map-marker-alt"></i> Sampling Feature Type</td>
            <td>{{ thing?.sampling_feature_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-barcode"></i> Sampling Feature Code</td>
            <td>{{ thing?.sampling_feature_code }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map-pin"></i> Site Type</td>
            <td>{{ thing?.site_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map"></i> Latitude</td>
            <td>{{ thing?.latitude }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map"></i> Longitude</td>
            <td>{{ thing?.longitude }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-mountain"></i> Elevation</td>
            <td>{{ thing?.elevation }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-users"></i> Followers</td>
            <td>{{ thing?.followers }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-user-check"></i> Is Primary Owner</td>
            <td>{{ thing?.is_primary_owner ? 'Yes' : 'No' }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-user"></i> Owns Thing</td>
            <td>{{ thing?.owns_thing ? 'Yes' : 'No' }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-user-friends"></i> Follows Thing</td>
            <td>{{ thing?.follows_thing ? 'Yes' : 'No' }}</td>
          </tr>
        </table>
      </div>
      <ImageCarousel :carousel-items="carouselItems" />
    </div>
  </div>

  <div class="site-information-container">
    <h2 class="site-information-title">Datastreams Available at this Site</h2>
    <v-btn v-if="thing?.owns_thing" color="grey-lighten-2">Manage Datastreams</v-btn>
    <img src="@/assets/hydro.png" alt="hydro" class="site-information-image">
    <v-btn color="grey-lighten-2" class="site-information-button">Download Data from HydroShare</v-btn>
  </div>

  <v-row class="ma-2">
    <v-col md="3" class="pa-3 d-flex flex-column" v-for="datastream in thing?.datastreams" :key="datastream.id">
      <v-card class="elevation-5 flex d-flex flex-column" outlined>
        <v-card-title>{{ datastream.name }}</v-card-title>
      </v-card>
    </v-col>
  </v-row>

</template>

<script>
import GoogleMap from "../components/GoogleMap.vue";
import ImageCarousel from "../components/ImageCarousel.vue";
import MoonIm1 from "@/assets/moon_bridge1.jpg"
import MoonIm2 from "@/assets/moon_bridge2.jpg"
import MoonIm3 from "@/assets/moon_bridge3.jpg"
import {computed, ref} from "vue";
import { useDataStore } from "@/store/data.js";
import {useAuthStore} from "@/store/authentication.js";
import axios from "@/axiosConfig"

export default {
  name: "SingleSite",
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  components: {
    GoogleMap,
    ImageCarousel,
  },
  setup(props) {
    const authStore = useAuthStore();
    authStore.fetchAccessToken();
    const dataStore = useDataStore();
    const thing = ref(null);
    const currentSlide = ref(0);
    const carouselItems = ref([
      {
        src: MoonIm1,
        alt: "Moon1",
      },
      {
        src: MoonIm2,
        alt: "Moon2",
      },
      {
        src: MoonIm3,
        alt: "Moon3",
      },
    ]);

    const isAuthenticated = computed(() => !!authStore.access_token)
    const isLoaded = computed(() => thing.value);
    const mapOptions = computed(() => thing.value ?
        {
           center: { lat: thing.value.latitude, lng: thing.value.longitude },
           zoom: 16,
           mapTypeId: "satellite",
        } : null
    );

    let cachedThingName = `thing_${props.id}`;
    const followsThing = ref(false)
    dataStore.fetchOrGetFromCache(cachedThingName, `/things/${props.id}`)
      .then(() => {
        thing.value = dataStore[cachedThingName]
        followsThing.value = thing.value.follows_thing
      })
      .catch((error) => {console.error("Error fetching thing data from API", error)})

    function updateFollow() {
      axios.get(`/things/${props.id}/ownership`)
          .then(response => {
            dataStore.cacheProperty(cachedThingName, response.data)
            localStorage.removeItem("things")
            dataStore.things = []
            thing.value = dataStore[cachedThingName]
            followsThing.value = thing.value.follows_thing
          })
          .catch(error => {console.error('Error updating follow status:', error)})
    }

    return {isLoaded, mapOptions, currentSlide, carouselItems, thing, isAuthenticated, followsThing, updateFollow }
  },
};
</script>

<style scoped>
 .site-information-image {
   margin-left: auto;
   margin-right: 1rem;
   max-height: 30px;
}

.hydroshare-logo-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.hydroshare-logo-container img {
  max-height: 50px;
}

table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
   border-right: 1px solid lightgray;
  border-bottom: 1px solid lightgray;
  border-collapse: collapse;
  border-spacing: 0;
  margin-left: auto;
  margin-right: auto;
}

table th,
table td {
  padding: 0.1rem; /* Adjusted padding to make elements shorter */
  vertical-align: middle;
  border-top: 1px solid #dee2e6;
}

table thead th {
  vertical-align: bottom;
  border-bottom: 2px solid #dee2e6;
}

table tbody + tbody {
  border-top: 2px solid #dee2e6;
}

table th {
  font-weight: 500;
  text-align: left;
}

table tr:nth-of-type(odd) {
  background-color: rgba(0, 0, 0, 0.05);
}

 table td:first-child {
  display: flex;
  align-items: center;
  white-space: nowrap;
  background-color: #f5f5f5;
  text-align: left; /* Added to align text to the left */
}

table td:first-child i {
  margin-right: 0.5rem;
  width: 1.5rem; /* Set a fixed width for the icons */
  text-align: center; /* Center the icons within the fixed width */
}

table td:last-child {
  background-color: #ffffff; /* Set background color for right td */
}

table td:first-child i {
  margin-right: 0.5rem;
}

.site-information-container {
  padding: 1rem;
  display: flex;
  align-items: center;
}

.site-information-title{
  margin-right: 2rem;
}

.content-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.content-wrapper > * {
  max-height: 30vh;
}

.table-container {
  width: 60%;
  position: relative;
}

.carousel-container {
  width: calc(40% - 1rem); /* Subtract the gap from the width */
  position: relative;
}

.follow-checkbox .v-input--selection-controls__input .v-icon {
  color: rgba(0, 0, 0, 0.54) !important;
}
</style>
