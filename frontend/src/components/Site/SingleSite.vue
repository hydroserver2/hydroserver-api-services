<template>
  <div style="margin: 1rem" v-if="thingStore.things[thingId]">
    <h2>{{ thingStore.things[thingId]?.name }}</h2>
    <div class="mb-8 flex-shrink-0" style="height: 25rem">
      <GoogleMap
        :key="thingStore.things[thingId]"
        :things="[thingStore.things[thingId]]"
        :mapOptions="mapOptions"
      />
    </div>

    <div class="site-information-container">
      <h2 class="site-information-title">Site Information</h2>
      <div
        v-if="
          isAuthenticated &&
          thingStore.things[thingId] &&
          thingStore.things[thingId].owns_thing
        "
      >
        <v-btn @click="showAccessControlModal = true">Access Control</v-btn>
        <v-dialog v-model="showAccessControlModal" width="60rem">
          <SiteAccessControl
            @close="showAccessControlModal = false"
            :thing-id="thingId"
          ></SiteAccessControl>
        </v-dialog>
        <v-btn @click="showRegisterSiteModal = true" color="green"
          >Edit Site Information</v-btn
        >
        <v-dialog v-model="showRegisterSiteModal" width="80rem">
          <SiteForm
            @close="showRegisterSiteModal = false"
            :thing-id="thingId"
          ></SiteForm>
        </v-dialog>
        <v-btn
          color="red-darken-3"
          style="margin-left: 1rem"
          @click="showDeleteModal = true"
          >Delete Site</v-btn
        >
        <v-dialog v-model="showDeleteModal" width="40rem">
          <v-card>
            <v-card-title>
              <span class="text-h5">Confirm Deletion</span>
            </v-card-title>
            <v-card-text>
              This action will permanently delete the site along with all
              associated datastreams and observations
              <strong>for all users of this system</strong>. If you want to keep
              your data, you can backup to HydroShare or download a local copy
              before deletion. Alternatively, you can pass ownership of this
              site to someone else on the
              <v-btn @click="switchToAccessControlModal">Access Control</v-btn>
              page.
            </v-card-text>
            <v-card-text>
              Please type the site name (<strong>{{
                thingStore.things[thingId].name
              }}</strong
              >) to confirm deletion:
              <v-form>
                <v-text-field
                  v-model="deleteInput"
                  label="Site name"
                  solo
                  @keydown.enter.prevent="deleteThing"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-btn color="red darken-1" text @click="showDeleteModal = false"
                >Cancel</v-btn
              >
              <v-btn color="green darken-1" text @click="deleteThing"
                >Confirm</v-btn
              >
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
      <div
        v-else-if="
          isAuthenticated &&
          thingStore.things[thingId] &&
          !thingStore.things[thingId].owns_thing
        "
      >
        <input
          class="follow-checkbox"
          type="checkbox"
          :checked="thingStore.things[thingId].follows_thing"
          @change="updateFollow"
        />
        <label>Follow Thing</label>
      </div>
    </div>

    <div class="content-wrapper">
      <div class="table-container">
        <table>
          <tr>
            <td><i class="fas fa-id-badge"></i> ID</td>
            <td>{{ thingStore.things[thingId]?.id }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-barcode"></i> Site Code</td>
            <td>{{ thingStore.things[thingId]?.sampling_feature_code }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map"></i> Latitude</td>
            <td>{{ thingStore.things[thingId]?.latitude }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map"></i> Longitude</td>
            <td>{{ thingStore.things[thingId]?.longitude }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-mountain"></i> Elevation</td>
            <td>{{ thingStore.things[thingId]?.elevation }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-file-alt"></i> Description</td>
            <td>{{ thingStore.things[thingId]?.description }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map-marker-alt"></i> Sampling Feature Type</td>
            <td>{{ thingStore.things[thingId]?.sampling_feature_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-map-pin"></i> Site Type</td>
            <td>{{ thingStore.things[thingId]?.site_type }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-flag-usa"></i>State</td>
            <td>{{ thingStore.things[thingId]?.state }}</td>
          </tr>
          <tr>
            <td><i class="fas fa-flag-usa"></i>County</td>
            <td>{{ thingStore.things[thingId]?.county }}</td>
          </tr>
          <tr>
            <td>
              <i
                :class="
                  thingStore.things[thingId]?.is_private
                    ? 'fas fa-lock'
                    : 'fas fa-globe'
                "
              ></i>
              Privacy
            </td>
            <td>
              {{
                thingStore.things[thingId]?.is_private ? 'Private' : 'Public'
              }}
            </td>
          </tr>
          <tr>
            <td><i class="fas fa-user"></i>Site Owners</td>
            <td>
              <div v-for="owner in thingStore.things[thingId]?.owners">
                <ul>
                  <li style="list-style: none">
                    {{ owner.firstname }} {{ owner.lastname }}:
                    {{ owner.organization }}
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        </table>
      </div>
      <ImageCarousel :carousel-items="carouselItems" />
    </div>
  </div>

  <div class="site-information-container">
    <h2 class="site-information-title">Datastreams Available at this Site</h2>
    <v-btn
      v-if="thingStore.things[thingId]?.owns_thing"
      color="grey-lighten-2"
      :to="{
        name: 'SiteDatastreams',
        params: { id: thingStore.things[thingId].id },
      }"
      >Manage Datastreams</v-btn
    >
    <img src="@/assets/hydro.png" alt="hydro" class="site-information-image" />
    <v-btn color="grey-lighten-2" class="site-information-button"
      >Download Data from HydroShare</v-btn
    >
  </div>

  <v-row class="ma-2">
    <template
      v-for="datastream in datastreamStore.datastreams[thingId]"
      :key="datastream.id"
    >
      <v-col
        v-if="datastream.is_visible"
        md="3"
        class="pa-3 d-flex flex-column"
      >
        <v-card class="elevation-5 flex d-flex flex-column" outlined>
          <v-card-title
            >{{ datastream.observed_property_name }}
            <v-icon small class="mr-2">
              mdi-cloud-download-outline
            </v-icon></v-card-title
          >
          <v-card-item v-if="datastream.observations">
            <div v-for="observation in datastream.observations">
              {{ observation.result }}----{{ observation.result_time }}
            </div>
            {{ datastream.unit_name }}
            <br />
            {{
              (datastream.most_recent_observation as Observation).result_time
            }}
          </v-card-item>
          <v-card-item v-else>No data for this datastream</v-card-item>
        </v-card>
      </v-col>
    </template>
  </v-row>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import ImageCarousel from '@/components/ImageCarousel.vue'
import SiteAccessControl from '@/components/Site/SiteAccessControl.vue'
import SiteForm from '@/components/Site/SiteForm.vue'
import MoonIm1 from '@/assets/moon_bridge1.jpg'
import MoonIm2 from '@/assets/moon_bridge2.jpg'
import MoonIm3 from '@/assets/moon_bridge3.jpg'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/authentication'
import { useThingStore } from '@/store/things'
import router from '@/router/router'
import { useDatastreamStore } from '@/store/datastreams'
import { Observation } from '@/types'

const authStore = useAuthStore()
const thingStore = useThingStore()
const datastreamStore = useDatastreamStore()
const route = useRoute()
const thingId = route.params.id.toString()

const showRegisterSiteModal = ref(false)
const showDeleteModal = ref(false)
const showAccessControlModal = ref(false)

const deleteInput = ref('')
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
const mapOptions = computed(() => {
  if (thingStore.things[thingId])
    return {
      center: {
        lat: thingStore.things[thingId].latitude,
        lng: thingStore.things[thingId].longitude,
      },
      zoom: 16,
      mapTypeId: 'satellite',
    }
})

function updateFollow() {
  if (thingStore.things[thingId]) {
    thingStore.things[thingId].follows_thing =
      !thingStore.things[thingId].follows_thing
    thingStore.updateThingFollowership(thingStore.things[thingId])
  }
}

async function deleteThing() {
  if (!thingStore.things[thingId]) {
    console.error('Site could not be found.')
    return
  }
  if (deleteInput.value !== thingStore.things[thingId].name) {
    console.error('Site name does not match.')
    return
  }
  await thingStore.deleteThing(thingStore.things[thingId].id)
  await router.push('/sites')
}

onMounted(async () => {
  await thingStore.fetchThingById(thingId)
  await datastreamStore.fetchDatastreamsByThingId(thingId)
})

function switchToAccessControlModal() {
  showDeleteModal.value = false
  showAccessControlModal.value = true
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
