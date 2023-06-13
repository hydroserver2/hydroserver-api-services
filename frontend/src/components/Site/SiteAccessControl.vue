<template>
  <v-card>
    <v-card-title class="text-h5">Access Control</v-card-title>
    <v-card-text>
      <v-row v-if="thingStore.things[thingId]?.is_primary_owner">
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
                <p style="max-width: 35rem">
                  This action will de-elevate your permission level to owner and
                  elevate the chosen user's permission level to primary owner.
                  Permissions unique to the primary owner are:
                </p>
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
                <div v-else style="text-align: right">
                  <v-btn
                    color="delete"
                    v-if="
                      thingStore.things[thingId]?.is_primary_owner ||
                      owner.email == authStore.user.email
                    "
                    @click="removeOwner(owner.email)"
                  >
                    Remove
                  </v-btn>
                </div>
              </li>
            </ul>
          </v-card-text>
        </v-col>
        <v-col cols="12" md="6">
          <h6 class="text-h6 my-4" v-if="thingStore.things[props.thingId]">
            Toggle Site Privacy
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
                <p
                  v-if="thingStore.things[props.thingId].is_private"
                  style="max-width: 25rem"
                >
                  Setting your site to public will make it visible to all users
                  and guests of the system. They will be able to follow your
                  site and download its data
                </p>
                <p v-else style="max-width: 25rem">
                  setting your site to private will make it visible to only you
                  and other owners of your site. Anyone who is currently
                  following your site who is not an owner will be removed as a
                  follower
                </p>
              </template>
            </v-tooltip>
          </h6>
          <v-card-text v-if="thingStore.things[props.thingId]">
            <v-switch
              v-model="thingStore.things[props.thingId].is_private"
              :label="
                thingStore.things[props.thingId].is_private
                  ? 'Site is private'
                  : 'Site is public'
              "
              color="primary"
              @change="toggleSitePrivacy"
            ></v-switch>
          </v-card-text>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn-cancel text @click="emitClose">Close</v-btn-cancel>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useThingStore } from '@/store/things'
import { useAuthStore } from '@/store/authentication'

const props = defineProps<{
  thingId: string
}>()

const emits = defineEmits(['close'])

const newOwnerEmail = ref('')
const newPrimaryOwnerEmail = ref('')
const thingStore = useThingStore()
const authStore = useAuthStore()

async function addSecondaryOwner() {
  if (props.thingId && newOwnerEmail.value)
    await thingStore.addSecondaryOwner(props.thingId, newOwnerEmail.value)
}

async function transferPrimaryOwnership() {
  if (props.thingId && newPrimaryOwnerEmail.value)
    await thingStore.transferPrimaryOwnership(
      props.thingId,
      newPrimaryOwnerEmail.value
    )
}

async function removeOwner(email: string) {
  if (props.thingId && email) await thingStore.removeOwner(props.thingId, email)
}

async function toggleSitePrivacy() {
  if (!props.thingId) return
  await thingStore.updateThingPrivacy(
    props.thingId,
    thingStore.things[props.thingId].is_private
  )
}

const emitClose = () => {
  emits('close')
}

onMounted(async () => {
  if (props.thingId) await thingStore.fetchThingById(props.thingId)
})
</script>
