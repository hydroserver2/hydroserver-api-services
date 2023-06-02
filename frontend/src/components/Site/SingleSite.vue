<template>
  <v-container>
    <v-row v-if="thingStore.things[thingId]">
      <v-col>
        <h5 class="text-h5">{{ thingStore.things[thingId]?.name }}</h5>
      </v-col>
    </v-row>
    <v-row v-if="thingStore.things[thingId]" style="height: 25rem">
      <v-col>
        <GoogleMap
          :key="thing"
          :things="[thingStore.things[thingId]]"
          :mapOptions="mapOptions"
        />
      </v-col>
    </v-row>
    <v-row class="justify-start" align="center">
      <v-col cols="auto">
        <h5 class="text-h5">Site Information</h5>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn @click="showAccessControlModal = true">Access Control</v-btn>
        <v-dialog v-model="showAccessControlModal" width="60rem">
          <SiteAccessControl
            @close="showAccessControlModal = false"
            :thing-id="thingId"
          ></SiteAccessControl>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn @click="showRegisterSiteModal = true" color="green"
          >Edit Site Information</v-btn
        >
        <v-dialog v-model="showRegisterSiteModal" width="80rem">
          <SiteForm
            @close="showRegisterSiteModal = false"
            :thing-id="thingId"
          ></SiteForm>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
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
      </v-col>
      <v-col cols="auto" v-if="!is_owner">
        <v-switch
          color="green"
          hide-details
          v-if="isAuthenticated && thingStore.things[thingId]"
          v-model="thingStore.things[thingId].follows_thing"
          @change="updateFollow"
          label="Follow Site"
        ></v-switch>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="8">
        <v-data-table>
          <tbody>
            <tr v-for="property in thingProperties" :key="property.label">
              <td><i :class="property.icon"></i></td>
              <td>{{ property.label }}</td>
              <td>{{ property.value }}</td>
            </tr>
          </tbody>
          <template v-slot:bottom></template>
        </v-data-table>
      </v-col>

      <v-col cols="12" md="4">
        <v-carousel hide-delimiters>
          <v-carousel-item
            v-for="n in 5"
            :key="n"
            :src="'https://source.unsplash.com/featured/?nature,landscape' + n"
            cover
          >
          </v-carousel-item>
        </v-carousel>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <h5 class="text-h5">Datastreams Available at this Site</h5>
      </v-col>
      <v-col>
        <v-btn
          v-if="thingStore.things[thingId]?.owns_thing"
          color="grey-lighten-2"
          :to="{
            name: 'SiteDatastreams',
            params: { id: thingStore.things[thingId].id },
          }"
          >Manage Datastreams</v-btn
        >
      </v-col>
      <v-col>
        <img
          style="max-height: 30px"
          src="@/assets/hydro.png"
          alt="hydro"
          class="site-information-image"
        />
      </v-col>
      <v-col>
        <v-btn color="grey-lighten-2" class="site-information-button"
          >Download Data from HydroShare</v-btn
        >
      </v-col>
    </v-row>
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
  </v-container>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SiteAccessControl from '@/components/Site/SiteAccessControl.vue'
import SiteForm from '@/components/Site/SiteForm.vue'
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
const is_owner = computed(
  () =>
    isAuthenticated &&
    thingStore.things[thingId] &&
    thingStore.things[thingId].owns_thing
)
const thing = computed(
  () => thingStore.things[thingId] as unknown as string
)
const showRegisterSiteModal = ref(false)
const showDeleteModal = ref(false)
const showAccessControlModal = ref(false)

const deleteInput = ref('')
const thingProperties = computed(() => {
  if (!thingStore.things[thingId]) return []
  const {
    id,
    sampling_feature_code,
    latitude,
    longitude,
    elevation,
    description,
    sampling_feature_type,
    site_type,
    state,
    county,
    is_private,
    owners,
  } = thingStore.things[thingId]

  return [
    { icon: 'fas fa-id-badge', label: 'ID', value: id },
    {
      icon: 'fas fa-barcode',
      label: 'Site Code',
      value: sampling_feature_code,
    },
    { icon: 'fas fa-map', label: 'Latitude', value: latitude },
    { icon: 'fas fa-map', label: 'Longitude', value: longitude },
    { icon: 'fas fa-mountain', label: 'Elevation', value: elevation },
    { icon: 'fas fa-file-alt', label: 'Description', value: description },
    {
      icon: 'fas fa-map-marker-alt',
      label: 'Sampling Feature Type',
      value: sampling_feature_type,
    },
    { icon: 'fas fa-map-pin', label: 'Site Type', value: site_type },
    { icon: 'fas fa-flag-usa', label: 'State', value: state },
    { icon: 'fas fa-flag-usa', label: 'County', value: county },
    {
      icon: is_private ? 'fas fa-lock' : 'fas fa-globe',
      label: 'Privacy',
      value: is_private ? 'Private' : 'Public',
    },
    {
      icon: 'fas fa-user',
      label: 'Site Owners',
      value: owners
        .map(
          (owner) =>
            `${owner.firstname} ${owner.lastname}: ${owner.organization}`
        )
        .join(', '),
    },
  ]
})

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
