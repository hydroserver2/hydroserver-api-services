<template>
  <v-footer>
    <v-container class="py-8">
      <v-row>
        <v-col>
          <h5 class="text-h5 mb-4">Contact Us</h5>
          <a class="d-block" href="#">Contact</a>
          <div>Learn more about <a href="#">CIROH</a></div>
        </v-col>
        <v-col>
          <h5 class="text-h5 mb-4">Policies</h5>
          <a class="d-block" href="#">Terms of Use</a>
          <a class="d-block" href="#">Privacy</a>
        </v-col>
        <v-col>
          <h5 class="text-h5 mb-4">Developed By</h5>
          <v-img
            :src="uwrlLogo"
            alt="UWRL Logo"
            max-width="20rem"
            class="fill-width"
          ></v-img>
        </v-col>
        <v-col>
          <h5 class="text-h5 mb-4">Open Source</h5>
          <p>
            HydroServer is open Source. Find us on
            <a href="https://github.com/hydroserver2/hydroserver">GitHub.</a>
          </p>
          <p>
            Report a bug
            <a href="https://github.com/issues" target="_blank">here.</a>
          </p>
          <p>
            This is Version {{ version }} of the Hydroserver web application.
          </p>
        </v-col>
        <v-col cols="12" class="text-center mt-4"
          ><p class="d-inline-block text-body-2">
            (c) Utah Water Research Laboratory (UWRL). This material is based on
            work supported by the Cooperative Institute for Research to
            Operations in Hydrology (CIROH). Funding was awarded to CIROH
            through the NOAA Cooperative Agreement with the University of
            Alabama (NA22NWS4320003)
          </p></v-col
        >
      </v-row>
    </v-container>
  </v-footer>
</template>

<script setup lang="ts">
import uwrlLogo from '@/assets/UWRL.png'

const version = import.meta.env.VITE_APP_VERSION || '0.0.1'
</script>

<style scoped>
.v-footer {
  background-color: #f5f5f5;
  color: #333;
}

p {
  max-width: 75rem;
}
</style>
