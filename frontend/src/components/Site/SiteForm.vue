<template>
  <v-card>
    <v-card-title class="text-h5"
      >{{ thingId ? 'Edit' : 'Register a' }} Site</v-card-title
    >
    <div v-if="thingId" class="flex-shrink-0" style="height: 20rem">
      <GoogleMap
        v-if="loaded"
        singleMarkerMode
        @location-clicked="onMapLocationClicked"
        :mapOptions="mapOptions"
        :things="[thing]"
      />
    </div>
    <div v-else class="flex-shrink-0" style="height: 20rem">
      <GoogleMap singleMarkerMode @location-clicked="onMapLocationClicked" />
    </div>
    <v-divider></v-divider>
    <v-card-text
      class="text-subtitle-2 text-medium-emphasis d-flex align-center"
    >
      <v-icon class="mr-1">mdi-information</v-icon>Click on the map to
      {{ thingId ? 'edit' : 'populate' }}
      site location data.
    </v-card-text>

    <v-card-text>
      <v-form
        ref="myForm"
        v-model="valid"
        validate-on="blur"
        @submit.prevent="uploadThing"
        enctype="multipart/form-data"
      >
        <v-row>
          <v-col cols="12" md="6">
            <h6 class="text-h6 my-4">Site Information</h6>
            <v-row>
              <v-col cols="12"
                ><v-text-field
                  label="Site Code *"
                  v-model="thing.sampling_feature_code"
                  :rules="rules.requiredCode"
              /></v-col>
              <v-col cols="12"
                ><v-text-field
                  label="Site Name *"
                  v-model="thing.name"
                  :rules="rules.requiredCode"
              /></v-col>
              <v-col cols="12"
                ><v-textarea
                  label="Site Description"
                  v-model="thing.description"
                  :rules="thing.description ? rules.description : []"
              /></v-col>
              <v-col cols="12"
                ><v-autocomplete
                  label="Select Site Type *"
                  :items="siteTypes"
                  v-model="thing.site_type"
                  :rules="rules.required"
                ></v-autocomplete
              ></v-col>
            </v-row>
          </v-col>
          <v-col cols="12" md="6">
            <h6 class="text-h6 my-4">Site Location</h6>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  label="Latitude *"
                  v-model="thing.latitude"
                  type="number"
                  :rules="rules.required"
              /></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  label="Longitude *"
                  v-model="thing.longitude"
                  type="number"
                  :rules="rules.required"
              /></v-col>
              <v-col cols="12" sm="6"
                ><v-text-field
                  label="Elevation *"
                  v-model="thing.elevation"
                  type="number"
                  :rules="rules.required"
              /></v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  label="State"
                  v-model="thing.state"
                  :rules="thing.state ? rules.name : []"
                />
              </v-col>
              <!--            <v-col cols="12" sm="6">-->
              <!--              <v-text-field-->
              <!--                disabled-->
              <!--                label="Elevation Datum"-->
              <!--                v-model="thing.elevation_datum"-->
              <!--              />-->
              <!--            </v-col>-->
              <v-col cols="12" sm="6">
                <v-text-field
                  label="County"
                  v-model="thing.county"
                  :rules="thing.state ? rules.name : []"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <h6 class="text-h6 mb-4 mt-7">Add Photos</h6>
                <v-card-text
                  id="drop-area"
                  @dragover.prevent
                  @drop="handleDrop"
                  class="drop-area text-subtitle-2 text-medium-emphasis d-flex mb-6"
                >
                  <v-icon class="mr-1">mdi-paperclip</v-icon>
                  Drag and drop your photos here, or
                  <span @click="triggerFileInput" class="ml-1 add-link"
                    >click to upload</span
                  >

                  <input
                    type="file"
                    ref="fileInput"
                    id="fileInput"
                    multiple
                    @change="
                      previewPhotos(($event.target as HTMLInputElement).files)
                    "
                    accept="image/jpeg, image/png"
                    style="display: none"
                  />
                </v-card-text>

                <div class="photo-container">
                  <div
                    v-if="props.thingId && photoStore.photos[props.thingId]"
                    v-for="photo in photoStore.photos[props.thingId]"
                    :key="photo.id"
                    class="photo-wrapper"
                  >
                    <img
                      v-if="!photosToDelete.includes(photo.id)"
                      :src="photo.url"
                      class="photo"
                    />
                    <v-icon
                      v-if="!photosToDelete.includes(photo.id)"
                      color="red-darken-1"
                      class="delete-icon"
                      @click="removeExistingPhoto(photo.id)"
                      >mdi-close-circle</v-icon
                    >
                  </div>

                  <div
                    v-for="(photo, index) in previewedPhotos"
                    :key="index"
                    class="photo-wrapper"
                  >
                    <img :src="photo" class="photo" />
                    <v-icon
                      color="red-darken-1"
                      class="delete-icon"
                      @click="removePhoto(index)"
                      >mdi-close-circle</v-icon
                    >
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn-cancel @click="closeDialog">Cancel</v-btn-cancel>
          <v-btn @click="uploadThing">Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import GoogleMap from '../GoogleMap.vue'
import { useThingStore } from '@/store/things'
import { usePhotosStore } from '@/store/photos'
import { Thing } from '@/types'
import { siteTypes } from '@/vocabularies'
import { VForm } from 'vuetify/components'
import { rules } from '@/utils/rules'
import Notification from '@/store/notifications'

const thingStore = useThingStore()
const photoStore = usePhotosStore()
const props = defineProps({ thingId: String })
const emit = defineEmits(['close'])
let loaded = ref(false)
const valid = ref(false)
const myForm = ref<VForm>()

const newPhotos = ref<File[]>([])
const photosToDelete = ref<string[]>([])
const previewedPhotos = ref<string[]>([])
const fileInput = ref<HTMLInputElement | null>(null)

const mapOptions = ref({
  center: { lat: 39, lng: -100 },
  zoom: 4,
  mapTypeId: 'roadmap',
})
const thing = reactive<Thing>(new Thing())

function handleDrop(e: DragEvent) {
  e.preventDefault()
  let files = e.dataTransfer?.files
  if (files) {
    let filteredFiles = Array.from(files).filter(
      (file) => file.type === 'image/jpeg' || file.type === 'image/png'
    )
    if (filteredFiles.length > 0) {
      previewPhotos(filteredFiles)
    } else {
      Notification.toast({
        message: 'only JPEG and PNG images are allowed',
        type: 'error',
      })
    }
  }
}

function previewPhotos(files: File[] | FileList | null) {
  if (files) {
    Array.from(files).forEach((photo) => {
      let reader = new FileReader()
      reader.onload = (e) => {
        if ((e.target as FileReader).result) {
          previewedPhotos.value.push((e.target as FileReader).result as string)
          newPhotos.value.push(photo)
        }
      }
      reader.readAsDataURL(photo)
    })
  }
}

function triggerFileInput() {
  if (fileInput.value) fileInput.value.click()
}

function removePhoto(index: number) {
  previewedPhotos.value.splice(index, 1)
  newPhotos.value.splice(index, 1)
}

function removeExistingPhoto(photoId: string) {
  photosToDelete.value.push(photoId)
}

async function populateThing(id: string) {
  await thingStore.fetchThings()
  Object.assign(thing, thingStore.things[id])
  mapOptions.value = {
    center: { lat: thing.latitude, lng: thing.longitude },
    zoom: 10,
    mapTypeId: 'satellite',
  }
  loaded.value = true
}

function closeDialog() {
  emit('close')
}

async function uploadThing() {
  await myForm.value?.validate()
  if (!valid.value) return

  emit('close')
  if (thing) {
    if (props.thingId) {
      await thingStore.updateThing(thing)
      await photoStore.updatePhotos(
        props.thingId,
        newPhotos.value,
        photosToDelete.value
      )
    } else {
      const newThing = await thingStore.createThing(thing)
      await photoStore.updatePhotos(newThing.id, newPhotos.value, [])
    }
  }
}

function onMapLocationClicked(locationData: Thing) {
  thing.latitude = locationData.latitude
  thing.longitude = locationData.longitude
  thing.elevation = locationData.elevation
  thing.state = locationData.state
  thing.county = locationData.county
}

onMounted(async () => {
  if (props.thingId) {
    await populateThing(props.thingId)
    await photoStore.fetchPhotos(props.thingId)
  }
})
</script>

<style scoped lang="scss">
.drop-area {
  border: 2px dashed #ccc;
}

.add-link {
  color: blue;
  text-decoration: underline;
  cursor: pointer;
}

.photo-container {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}

.photo-wrapper {
  position: relative;
  margin-right: 20px;
  width: 6rem;
  margin-bottom: 20px;
}

.photo {
  width: 100px;
  height: 100px;
  object-fit: cover;
}

.delete-icon {
  position: absolute;
  top: -20px;
  right: -20px;
}
</style>
