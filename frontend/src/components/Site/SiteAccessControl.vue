<template>
  <v-card>
    <v-card-title class="text-h5">Access Control</v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4">
            Add a secondary owner to this site
            <v-tooltip>
              <template v-slot:activator="{ props }">
                <v-icon
                  small
                  class="ml-2"
                  color="grey lighten-1"
                  v-bind="props"
                >
                  mdi-help-circle-outline
                </v-icon>
              </template>
              <template v-slot:default>
                <p>
                  The new secondary owner will be given the following
                  permissions:
                </p>
                <ul>
                  <li class="v-list-item">CRUD for site and metadata</li>
                  <li class="v-list-item">CRUD for site datastreams</li>
                  <li class="v-list-item">Make site private or public</li>
                  <li class="v-list-item">Remove themselves as owner</li>
                </ul>
              </template>
            </v-tooltip>
          </h6>

          <v-text-field
            v-model="newOwnerEmail"
            label="Secondary Owner's Email"
            required
          ></v-text-field>
          <v-btn color="primary" @click="addSecondaryOwner">Submit</v-btn>
        </v-col>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4">
            Transfer Primary Ownership
            <v-tooltip>
              <template v-slot:activator="{ props }">
                <v-icon
                  small
                  class="ml-2"
                  color="grey lighten-1"
                  v-bind="props"
                >
                  mdi-help-circle-outline
                </v-icon>
              </template>
              <template v-slot:default>
                <p>
                  This action will de-elevate your permission level to owner and
                  elevate the chosen user's permission level to primary owner.
                </p>
                <p>Permissions unique to the primary owner are:</p>
                <ul>
                  <li class="v-list-item">Add secondary owners</li>
                  <li class="v-list-item">Remove secondary owners</li>
                  <li class="v-list-item">Transfer primary ownership</li>
                  <li class="v-list-item">
                    Edit contents of datastream units, observed properties,
                    processing levels, and sensors
                  </li>
                </ul>
              </template>
            </v-tooltip>
          </h6>
          <v-text-field
            v-model="newPrimaryOwnerEmail"
            label="New Primary Owner's Email"
            required
          ></v-text-field>
          <v-btn color="primary" @click="transferPrimaryOwnership"
            >Submit</v-btn
          >
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4">Current Owners</h6>
          <v-card-text>
            <ul>
              <li
                class="v-list-item"
                v-for="owner in thingStore.things[thingId].owners"
              >
                {{ owner.firstname }} {{ owner.lastname }} -
                {{ owner.organization }}
                <strong v-if="owner.is_primary_owner">(Primary)</strong>
              </li>
            </ul>
          </v-card-text>
        </v-col>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4">Toggle Site Privacy</h6>
          <v-card-text>
            <v-switch
              v-model="sitePrivacy"
              :label="sitePrivacy ? 'Site is private' : 'Site is public'"
              @change="toggleSitePrivacy"
            ></v-switch>
          </v-card-text>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn color="green darken-1" text @click="emitClose">Close</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted } from 'vue'
import { useThingStore } from '@/store/things'

const props = defineProps({
  thingId: String,
})

const emits = defineEmits(['close'])

const newOwnerEmail = ref('')
const newPrimaryOwnerEmail = ref('')
const sitePrivacy = ref(false)
const thingStore = useThingStore()
const addSecondaryOwner = () => {
  // Add secondary owner logic here
}

const transferPrimaryOwnership = () => {
  // Transfer primary ownership logic here
}

const toggleSitePrivacy = () => {
  // Toggle site privacy logic here
}

const emitClose = () => {
  emits('close')
}

onMounted(async () => {
  if (props.thingId) await thingStore.fetchThingById(props.thingId)
})
</script>
