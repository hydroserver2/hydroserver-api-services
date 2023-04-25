<template>
  <div v-if="isLoaded" style="margin: 1rem">
    <h2>{{ thing?.name }}</h2>
    <GoogleMap :markers="[thing]" :mapOptions="mapOptions" />

    <div class="site-information-container">
      <h2 class="site-information-title">Site Information</h2>
      <div v-if="isAuthenticated && thing && thing.owns_thing">
        <v-btn @click="showRegisterSiteModal = true" color="green"
          >Edit Site Information</v-btn
        >
        <DeleteSiteModal
          :site-id="thing.id"
          :site-name="thing.name"
          v-model="showDeleteModal"
          @close="showDeleteModal = false"
        />
        <v-btn
          color="red-darken-3"
          style="margin-left: 1rem"
          @click="showDeleteModal = true"
          >Delete Site</v-btn
        >
      </div>
      <div v-else-if="isAuthenticated && thing && !thing.owns_thing">
        <input
          class="follow-checkbox"
          type="checkbox"
          :checked="followsThing"
          @change="updateFollow"
        />
        <label>Follow Thing</label>
      </div>
    </div>

    <site-form
      v-if="showRegisterSiteModal && thing_id"
      @close="showRegisterSiteModal = false"
      @siteCreated="loadThing"
      :thing-id="thing_id"
    ></site-form>

    <div class="content-wrapper">
      <div class="table-container">
        <table>
          <tr>
            <td><i class="fas fa-barcode"></i> Site Code</td>
            <td>{{ thing?.sampling_feature_code }}</td>
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
            <td><i class="fas fa-map-pin"></i> Site Type</td>
            <td>{{ thing?.site_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-users"></i> Followers</td>
            <td>{{ thing?.followers }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-flag-usa"></i>State</td>
            <td>{{ thing?.state }}</td>
          </tr>
        </table>
      </div>
      <ImageCarousel :carousel-items="carouselItems" />
    </div>
  </div>

  <div class="site-information-container">
    <h2 class="site-information-title">Datastreams Available at this Site</h2>
    <v-btn
      v-if="thing?.owns_thing"
      color="grey-lighten-2"
      :to="{ name: 'SiteDatastreams', params: { id: thing.id } }"
      >Manage Datastreams</v-btn
    >
    <img src="@/assets/hydro.png" alt="hydro" class="site-information-image" />
    <v-btn color="grey-lighten-2" class="site-information-button"
      >Download Data from HydroShare</v-btn
    >
  </div>

  <v-row class="ma-2">
    <v-col
      md="3"
      class="pa-3 d-flex flex-column"
      v-for="datastream in thing?.datastreams"
      :key="datastream.id"
    >
      <v-card class="elevation-5 flex d-flex flex-column" outlined>
        <v-card-title>{{ datastream.name }}</v-card-title>
      </v-card>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import GoogleMap from '../components/GoogleMap.vue'
import ImageCarousel from '../components/ImageCarousel.vue'
import DeleteSiteModal from '@/components/Site/DeleteSiteModal.vue'
import MoonIm1 from '@/assets/moon_bridge1.jpg'
import MoonIm2 from '@/assets/moon_bridge2.jpg'
import MoonIm3 from '@/assets/moon_bridge3.jpg'
import { computed, ref } from 'vue'
import { useDataStore } from '@/store/data'
import { useAuthStore } from '@/store/authentication'
import axios from '@/plugins/axios.config'
import { useRoute } from 'vue-router'
import SiteForm from '@/components/Site/SiteForm.vue'

export default {
  name: 'SingleSite',
  components: {
    SiteForm,
    GoogleMap,
    ImageCarousel,
    DeleteSiteModal,
  },
  setup() {
    const authStore = useAuthStore()
    const dataStore = useDataStore()
    const route = useRoute()

    authStore.fetchAccessToken()
    const showRegisterSiteModal = ref(false)
    const thing_id = route.params.id.toString()
    const thing = ref(null)
    const showDeleteModal = ref(false)
    const currentSlide = ref(0)
    const carouselItems = ref([
      {
        src: MoonIm1,
        alt: 'Moon1',
      },
      {
        src: MoonIm2,
        alt: 'Moon2',
      },
      {
        src: MoonIm3,
        alt: 'Moon3',
      },
    ])

    const isAuthenticated = computed(() => !!authStore.access_token)
    const isLoaded = computed(() => thing.value)
    const mapOptions = computed(() =>
      thing.value
        ? {
            center: { lat: thing.value.latitude, lng: thing.value.longitude },
            zoom: 16,
            mapTypeId: 'satellite',
          }
        : null
    )

    let cachedThingName = `thing_${thing_id}`
    const followsThing = ref(false)
    function loadThing() {
      dataStore
        .fetchOrGetFromCache(cachedThingName, `/things/${thing_id}`)
        .then(() => {
          thing.value = dataStore[cachedThingName]
          followsThing.value = thing.value.follows_thing
        })
        .catch((error) => {
          console.error('Error fetching thing data from API', error)
        })
    }

    loadThing()

    function updateFollow() {
      axios
        .get(`/things/${thing_id}/ownership`)
        .then((response) => {
          dataStore.cacheProperty(cachedThingName, response.data)
          localStorage.removeItem('things')
          dataStore.things = []
          thing.value = dataStore[cachedThingName]
          followsThing.value = thing.value.follows_thing
        })
        .catch((error) => {
          console.error('Error updating follow status:', error)
        })
    }

    return {
      loadThing,
      showRegisterSiteModal,
      isLoaded,
      mapOptions,
      currentSlide,
      carouselItems,
      thing,
      isAuthenticated,
      followsThing,
      updateFollow,
      showDeleteModal,
      thing_id,
    }
  },
}
</script>

<style scoped lang="scss">
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
  padding-bottom: 1rem;
  padding-top: 1rem;
  display: flex;
  align-items: center;
}

.site-information-title {
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
