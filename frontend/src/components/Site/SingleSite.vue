<template>
  <v-container>
    <v-row v-if="thingStore.things[thingId]">
      <v-col class="single-site-name">
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
        <v-btn @click="dialogs.accessControl = true">Access Control</v-btn>
        <v-dialog v-model="dialogs.accessControl" width="60rem">
          <SiteAccessControl
            @close="dialogs.accessControl = false"
            :thing-id="thingId"
          ></SiteAccessControl>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn @click="dialogs.registerSite = true" color="secondary"
          >Edit Site Information</v-btn
        >
        <v-dialog v-model="dialogs.registerSite" width="80rem">
          <SiteForm
            @close="dialogs.registerSite = false"
            :thing-id="thingId"
          ></SiteForm>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn
          color="red-darken-3"
          style="margin-left: 1rem"
          @click="dialogs.deleteSite = true"
          >Delete Site</v-btn
        >
        <v-dialog v-model="dialogs.deleteSite" width="40rem">
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
              <v-spacer></v-spacer>
              <v-btn-cancel @click="dialogs.deleteSite = false"
                >Cancel</v-btn-cancel
              >
              <v-btn color="delete" @click="deleteThing">Delete</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="!is_owner">
        <v-switch
          color="secondary"
          hide-details
          v-if="isAuthenticated && thingStore.things[thingId]"
          v-model="thingStore.things[thingId].follows_thing"
          @change="updateFollow"
          :label="
            thingStore.things[thingId].follows_thing
              ? 'You Follow This site'
              : 'Follow Site'
          "
        ></v-switch>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="8">
        <v-data-table class="elevation-2">
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
      <v-col cols="auto">
        <h5 class="text-h5">Datastreams Available at this Site</h5>
      </v-col>
      <v-spacer></v-spacer>
      <v-col cols="auto">
        <img
          style="max-height: 1.5rem"
          src="@/assets/hydro.png"
          alt="hydro share logo"
          class="site-information-image"
        />
      </v-col>
      <v-col cols="auto">
        <v-btn color="grey" class="site-information-button"
          >Download Data from HydroShare</v-btn
        >
      </v-col>
    </v-row>
    <v-row class="pb-2" v-if="is_owner">
      <v-col>
        <v-btn-secondary
          prependIcon="mdi-plus"
          variant="elevated"
          :to="{ name: 'DatastreamForm', params: { id: thingId } }"
          >Add New Datastream</v-btn-secondary
        >
      </v-col>
    </v-row>
    <v-row class="pb-5">
      <v-data-table
        class="elevation-3"
        :headers="headers"
        :items="visibleDatastreams"
      >
        <template v-slot:item.observations="{ item }">
          <div v-if="item.raw.observations">
            <LineChart class="pt-2" :observations="item.raw.observations" />
          </div>
          <div v-else>No data for this datastream</div>
          <!-- <div v-if="item.raw.stale">stale</div>
          <div v-else>not stale</div> -->
        </template>
        <template v-slot:item.last_observation="{ item }">
          <div v-if="item.raw.most_recent_observation">
            {{ (item.raw.most_recent_observation as Observation).result_time }}
          </div>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-tooltip bottom :openDelay="500" v-if="item.raw.is_visible">
            <template v-slot:activator="{ props }" v-if="is_owner">
              <v-icon
                small
                color="grey"
                v-bind="props"
                @click="toggleVisibility(item.raw)"
              >
                mdi-eye
              </v-icon>
            </template>
            <span
              >Hide this datastream from guests of your site. Owners will still
              see it</span
            >
          </v-tooltip>
          <v-tooltip bottom :openDelay="500" v-else>
            <template v-slot:activator="{ props }" v-if="is_owner">
              <v-icon
                small
                color="grey-lighten-1"
                v-bind="props"
                @click="toggleVisibility(item.raw)"
              >
                mdi-eye-off
              </v-icon>
            </template>
            <span>Make this datastream publicly visible</span>
          </v-tooltip>

          <v-menu>
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" icon="mdi-dots-vertical" />
            </template>
            <v-list>
              <v-list-item
                v-if="is_owner"
                prepend-icon="mdi-link-variant"
                title="Link Data Source"
                :to="{
                  name: 'DataSourceForm',
                  params: { id: thingId, datastreamId: item.raw.id },
                }"
              />
              <v-list-item
                v-if="is_owner"
                prepend-icon="mdi-pencil"
                title="Edit Datastream Metadata"
                :to="{
                  name: 'DatastreamForm',
                  params: { id: thingId, datastreamId: item.raw.id },
                }"
              />
              <v-list-item
                v-if="is_owner"
                prepend-icon="mdi-delete"
                title="Delete Datastream"
                @click="showDeleteDatastreamModal(item.raw)"
              />
              <v-list-item prepend-icon="mdi-download" title="Download Data" />
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
      <v-dialog
        v-if="selectedDatastream"
        v-model="dialogs.deleteDatastream"
        width="40rem"
      >
        <v-card>
          <v-card-title>
            <span class="text-h5">Confirm Deletion</span>
          </v-card-title>
          <v-card-text>
            Are you sure you want to permanently delete the this datastream and
            all the observations associated with it?
            <br />
            <br />
            <strong>ID:</strong> {{ selectedDatastream.id }} <br />
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn-cancel @click="dialogs.deleteDatastream = false"
              >Cancel</v-btn-cancel
            >
            <v-btn color="delete" @click="deleteDatastream">Confirm</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SiteAccessControl from '@/components/Site/SiteAccessControl.vue'
import SiteForm from '@/components/Site/SiteForm.vue'
import { computed, onMounted, ref, reactive, Ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/authentication'
import { useThingStore } from '@/store/things'
import router from '@/router/router'
import { useDatastreamStore } from '@/store/datastreams'
import { Observation, Datastream } from '@/types'
import LineChart from '@/components/LineChart.vue'

const authStore = useAuthStore()
const thingStore = useThingStore()
const datastreamStore = useDatastreamStore()
const route = useRoute()
const thingId = route.params.id.toString()

const is_owner = computed(() => {
  if (isAuthenticated && thingStore.things[thingId]) {
    return thingStore.things[thingId].owns_thing
  }
  return false
})

const thing = computed(() => thingStore.things[thingId] as unknown as string)

const visibleDatastreams = computed(() => {
  if (!datastreamStore.datastreams[thingId]) return []
  return datastreamStore.datastreams[thingId].filter(
    (datastream) => datastream.is_visible || is_owner.value
  )
})

const headers = [
  { title: 'Unit Name', key: 'unit_name', sortable: true },
  { title: 'Observations', key: 'observations', sortable: false },
  { title: 'Last Observation', key: 'last_observation' },
  { title: 'Sampled Medium', key: 'sampled_medium' },
  { title: 'Sensor', key: 'method_name' },
  { title: 'Actions', key: 'actions', sortable: false },
]

const dialogs: {
  [key: string]: boolean
} = reactive({
  registerSite: false,
  deleteSite: false,
  accessControl: false,
  deleteDatastream: false,
})

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
  await thingStore.deleteThing(thingId)
  await router.push('/sites')
}

const selectedDatastream: Ref<Datastream | null> = ref(null)

function showDeleteDatastreamModal(datastream: Datastream) {
  selectedDatastream.value = datastream
  dialogs.deleteDatastream = true
}

async function toggleVisibility(datastream: Datastream) {
  datastream.is_visible = !datastream.is_visible
  await datastreamStore.setVisibility(datastream.id, datastream.is_visible)
}

async function deleteDatastream() {
  dialogs.deleteDatastream = false
  if (selectedDatastream.value) {
    await datastreamStore.deleteDatastream(selectedDatastream.value.id, thingId)
  }
}

onMounted(async () => {
  await thingStore.fetchThingById(thingId)
  await datastreamStore.fetchDatastreamsByThingId(thingId)
})

function switchToAccessControlModal() {
  dialogs.deleteSite = false
  dialogs.accessControl = true
}
</script>
