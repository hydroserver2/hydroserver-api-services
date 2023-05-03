<template>
  <v-parallax
    src="https://cdn.vuetifyjs.com/images/parallax/material.jpg"
    height="500"
  >
    <div
      class="d-flex text-white flex-column align-center text-center fill-height justify-space-between py-16 has-text-shadow"
    >
      <div>
        <h3 class="text-h3 mb-8">HydroServer</h3>
        <h4 class="text-h4 font-weight-thin mb-8">
          Collect and Manage Your Operational Hydrologic Data
        </h4>
      </div>

      <div>
        <h5 class="text-h5 mb-8">Create an account to get started</h5>
        <v-btn>Sign Up</v-btn>
      </div>
    </div>
  </v-parallax>

  <v-container v-bind="sectionAttrs">
    <div class="d-flex flex-column align-center text-center">
      <h2 class="text-h4 mb-4">Manage your Operation Data</h2>

      <p class="mb-8 text-body-1 text-medium-emphasis">
        The HydroServer Hydrologic Information System provides services and
        tools for collecting, storing, managing, and sharing your hydrologic
        observations collected from in situ monitoring sites.
      </p>
    </div>

    <v-row>
      <v-col cols="12" sm="6" class="mb-4">
        <div class="d-flex flex-column flex-sm-row gap-1">
          <div class="text-center">
            <v-icon icon="mdi-resistor" size="6rem" />
          </div>
          <div>
            <p class="text-body-1 font-weight-bold mb-2">
              Sensor Data Streaming
            </p>
            <p class="text-body-2 text-medium-emphasis mb-2">
              Stream sensor data directly from your Internet connected
              datalogger or load data using our Streaming Data Loader software.
            </p>
          </div>
        </div>
      </v-col>

      <v-col cols="12" sm="6" class="mb-4">
        <div class="d-flex flex-column flex-sm-row gap-1">
          <div class="text-center">
            <v-icon icon="mdi-database-outline" size="6rem" />
          </div>
          <div>
            <p class="text-body-1 font-weight-bold mb-2">
              Performant Data Storage
            </p>
            <p class="text-body-2 text-medium-emphasis mb-2">
              Using TimeScale DB with PostgreSQL, we provide a performant data
              store for your operational data.
            </p>
          </div>
        </div>
      </v-col>

      <v-col cols="12" sm="6" class="mb-4">
        <div class="d-flex flex-column flex-sm-row gap-1">
          <div class="text-center">
            <v-icon icon="mdi-cog-outline" size="6rem" />
          </div>
          <div>
            <p class="text-body-1 font-weight-bold mb-2">
              Easy Web Configuration
            </p>
            <p class="text-body-2 text-medium-emphasis mb-2">
              Create new monitoring locations, observed variables, sensors, and
              data streams through our web user interface.
            </p>
          </div>
        </div>
      </v-col>

      <v-col cols="12" sm="6" class="mb-4">
        <div class="d-flex flex-column flex-sm-row gap-1">
          <div class="text-center">
            <v-icon icon="mdi-lock-open-outline" size="6rem" />
          </div>
          <div>
            <p class="text-body-1 font-weight-bold mb-2">
              Public Access to Your Data
            </p>
            <p class="text-body-2 text-medium-emphasis mb-2">
              Provide convenient and simple access to the data from your
              monitoring sites.
            </p>
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>

  <v-divider></v-divider>

  <v-container v-bind="sectionAttrs">
    <v-row>
      <v-col class="text-center text-sm-right" cols="12" sm="4">
        <div>- Image Here -</div>
      </v-col>
      <v-col cols="12" sm="8">
        <h4 class="text-h4 mb-4">Operational Data for Modeling</h4>
        <h6 class="text-body-1 mb-2 font-weight-bold">
          Your data can improve NOAA's water prediction services
        </h6>
        <p class="text-body-1 text-medium-emphasis">
          NOAA's National Water Model can assimilate streamflow data from
          operational monitoring sites like yours. Contribute your streamflow
          data to make it available to support continental-scale hydrologic
          modeling and forecasting via the National Water Model.
        </p>
      </v-col>
    </v-row>
  </v-container>

  <v-divider></v-divider>

  <v-container v-bind="sectionAttrs">
    <v-row>
      <v-col cols="12" sm="6">
        <h4 class="text-h4 mb-8">Open Standards Data Sharing</h4>
        <p class="text-body-1 text-medium-emphasis">
          Share your data publicly using the latest Open Geospatial Consortium
          web services standard SensorThings.
        </p>
      </v-col>
      <v-col cols="12" sm="6" class="text-center">
        <div>- Image Here -</div>
        <h4 class="text-h4">SensorThings</h4>
      </v-col>
    </v-row>
  </v-container>

  <v-divider> </v-divider>

  <v-container v-bind="sectionAttrs" class="d-flex flex-column align-center">
    <div>- Image Here -</div>
    <p class="text-body-1 text-medium-emphasis text-center">
      This HydroServer instance is supported through the Cooperative Institute
      for Research to Operations in Hydrology (CIROH)
    </p>
  </v-container>
</template>

<script setup lang="ts">
import resistanceIcon from '@/assets/resistance.svg'
import gearIcon from '@/assets/gear.svg'
import dbIcon from '@/assets/db.svg'
import ogcIcon from '@/assets/ogc.png'

const sectionAttrs = {
  class: 'my-8',
}
</script>

<style scoped lang="scss">
p {
  max-width: 40rem;
}
</style>
