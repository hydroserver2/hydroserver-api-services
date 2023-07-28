<template>
  <v-container>
    <v-row class="mb-4">
      <v-col cols="auto">
        <h5 class="text-h5">Download HydroLoader</h5>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-btn
          size="large"
          variant="elevated"
          prepend-icon="mdi-apple"
          :href="macosLink"
        >
          Download for MacOS
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-btn
          size="large"
          variant="elevated"
          prepend-icon="mdi-microsoft-windows"
          :href="windowsLink"
        >
          Download for Windows
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">

let version = 'v0.1.6' // TODO: Add this as an environment variable
let macosLink = `https://sdl-dist.s3.amazonaws.com/${version}/macos/HydroLoader.dmg`
let windowsLink = `https://sdl-dist.s3.amazonaws.com/${version}/windows/HydroLoader.zip`

</script>

<style scoped>

</style>