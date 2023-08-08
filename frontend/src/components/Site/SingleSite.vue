<template>
  <v-container>
    <v-row v-if="thing">
      <v-col class="single-site-name">
        <h5 class="text-h5">{{ thing?.name }}</h5>
      </v-col>
    </v-row>
    <v-row v-if="thing" style="height: 25rem">
      <v-col>
        <GoogleMap
          :key="stringThing"
          :things="[thing]"
          :mapOptions="mapOptions"
        />
      </v-col>
    </v-row>
    <v-row class="justify-start" align="center">
      <v-col cols="auto">
        <h5 class="text-h5">Site Information</h5>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn class="access_control" @click="isAccessControlModalOpen = true"
          >Access Control</v-btn
        >
        <v-dialog
          class="access_control_dialog"
          v-model="isAccessControlModalOpen"
          width="60rem"
        >
          <SiteAccessControl
            @close="isAccessControlModalOpen = false"
            :thing-id="thingId"
          ></SiteAccessControl>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn @click="isRegisterModalOpen = true" color="secondary"
          >Edit Site Information</v-btn
        >
        <v-dialog v-model="isRegisterModalOpen" width="80rem">
          <SiteForm
            @close="isRegisterModalOpen = false"
            :thing-id="thingId"
          ></SiteForm>
        </v-dialog>
      </v-col>
      <v-col cols="auto" v-if="is_owner">
        <v-btn
          color="red-darken-3"
          style="margin-left: 1rem"
          @click="isDeleteModalOpen = true"
          >Delete Site</v-btn
        >
        <v-dialog v-model="isDeleteModalOpen" width="40rem">
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
              Please type the site name (<strong>{{ thing.name }}</strong
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
              <v-btn-cancel @click="isDeleteModalOpen = false"
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
          v-if="isAuthenticated && thing"
          v-model="thing.follows_thing"
          @change="updateFollow"
          :label="thing.follows_thing ? 'You Follow This site' : 'Follow Site'"
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
        <v-carousel
          hide-delimiters
          v-if="
            !photoStore.loading &&
            photoStore.photos[thingId] &&
            photoStore.photos[thingId].length > 0
          "
        >
          <v-carousel-item
            v-for="photo in photoStore.photos[thingId]"
            :key="photo.id"
            :src="photo.url"
            cover
          >
          </v-carousel-item>
        </v-carousel>
        <div v-else-if="photoStore.loading" class="text-center">
          <p>
            Your photos are being uploaded. They will appear once the upload is
            complete.
          </p>
          <v-progress-circular
            indeterminate
            color="primary"
          ></v-progress-circular>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="auto">
        <h5 class="text-h5">Datastreams Available at this Site</h5>
      </v-col>
      <v-spacer></v-spacer>
      <!-- <v-col cols="auto">
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
      </v-col> -->
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
            <router-link
              :to="{
                name: 'SiteVisualization',
                params: { id: thingId, datastreamId: item.raw.id },
              }"
            >
              <LineChart class="pt-2" :observations="item.raw.observations" />
            </router-link>
          </div>
          <div v-else>No data for this datastream</div>
          <!-- <div v-if="item.raw.stale">stale</div>
          <div v-else>not stale</div> -->
        </template>
        <template v-slot:item.last_observation="{ item }">
          <div v-if="item.raw.most_recent_observation">
            <v-row>
              {{
                formatDate(
                  (item.raw.most_recent_observation as Observation).result_time
                )
              }}
            </v-row>
            <v-row>
              {{ item.raw.unit_name }} -
              {{ (item.raw.most_recent_observation as Observation).result }}
            </v-row>
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
                @click="handleLinkDataSource(item.raw.id)"
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
                prepend-icon="mdi-chart-line"
                title="View Time Series Plot"
                :to="{
                  name: 'SiteVisualization',
                  params: { id: thingId, datastreamId: item.raw.id },
                }"
              />
              <v-list-item
                v-if="is_owner"
                prepend-icon="mdi-delete"
                title="Delete Datastream"
                @click="openDeleteModal(item.raw)"
              />
              <!-- <v-list-item prepend-icon="mdi-download" title="Download Data" /> -->
            </v-list>
          </v-menu>
        </template>
      </v-data-table>
      <v-dialog
        v-if="selectedDatastream"
        v-model="isDSDeleteModalOpen"
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
            <v-btn-cancel @click="isDSDeleteModalOpen = false"
              >Cancel</v-btn-cancel
            >
            <v-btn color="delete" @click="deleteDatastream">Confirm</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-dialog v-model="dataSourceDialogOpen" persistent>
        <DataSourceForm
          @close-dialog="dataSourceDialogOpen = false"
          :datastreamId="dataSourceDatastream"
        />
      </v-dialog>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import GoogleMap from '@/components/GoogleMap.vue'
import SiteAccessControl from '@/components/Site/SiteAccessControl.vue'
import SiteForm from '@/components/Site/SiteForm.vue'
import DataSourceForm from '@/components/DataSource/DataSourceForm.vue'
import LineChart from '@/components/LineChart.vue'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Observation } from '@/types'
import { usePhotosStore } from '@/store/photos'
import { useThing } from '@/composables/useThing'
import { useAuthentication } from '@/composables/useAuthentication'
import { useDatastreams } from '@/composables/useDatastreams'
import { format } from 'date-fns'

const photoStore = usePhotosStore()
const thingId = useRoute().params.id.toString()

const {
  thing,
  stringThing,
  mapOptions,
  updateFollow,
  is_owner,
  deleteInput,
  deleteThing,
  thingProperties,
  isRegisterModalOpen,
  isDeleteModalOpen,
  isAccessControlModalOpen,
  switchToAccessControlModal,
} = useThing(thingId)
const {
  visibleDatastreams,
  toggleVisibility,
  selectedDatastream,
  openDeleteModal,
  deleteDatastream,
  isDeleteModalOpen: isDSDeleteModalOpen,
} = useDatastreams(thingId)
const { isAuthenticated } = useAuthentication()

const headers = [
  { title: 'Observed Property', key: 'observed_property_name', sortable: true },
  { title: 'Observations', key: 'observations', sortable: false },
  { title: 'Last Observation', key: 'last_observation' },
  { title: 'Sampled Medium', key: 'sampled_medium' },
  { title: 'Sensor', key: 'method_name' },
  { title: 'Actions', key: 'actions', sortable: false },
]

const dataSourceDatastream = ref()
const dataSourceDialogOpen = ref(false)

function handleLinkDataSource(datastreamId: string) {
  dataSourceDatastream.value = datastreamId
  dataSourceDialogOpen.value = true
}

function formatDate(dateString: string) {
  const date = new Date(dateString)
  return format(date, 'MMM dd, yyyy HH:mm')
}

onMounted(async () => {
  await photoStore.fetchPhotos(thingId)
})
</script>
