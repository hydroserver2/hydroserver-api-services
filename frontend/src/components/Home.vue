<template>
  <v-parallax
    src="https://cdn.vuetifyjs.com/images/parallax/material.jpg"
    height="500"
  >
    <div
      class="d-flex flex-column fill-height justify-center align-center text-white"
    >
      <h1 class="text-h4 font-weight-thin mb-8">
        Collect and Manage Your Operational Hydrologic Data
      </h1>

      <h2 class="text-h5 mb-8">Create an account to get started</h2>
      <v-btn>Sign Up</v-btn>
    </div>
  </v-parallax>

  <v-container>
    <div class="my-8 d-flex flex-column align-center">
      <h2 class="text-center mb-4">Manage your Operation Data</h2>

      <p class="text-center mb-4 text-subtitle-2">
        The HydroServer Hydrologic Information System provides services and
        tools for collecting, storing, managing, and sharing your hydrologic
        observations collected from in situ monitoring sites.
      </p>

      <div>
        <h3>Sensor Data Streaming</h3>
        <p>
          Stream sensor data directly from your Internet connected datalogger or
          load data using our Streaming Data Loader software.
        </p>

        <h3>Easy Web Configuration</h3>
        <p>
          Create new monitoring locations, observed variables, sensors, and data
          streams through our web user interface.
        </p>

        <h3>Performant Data Storage</h3>
        <p>
          Using TimeScale DB with PostgreSQL, we provide a performant data store
          for your operational data.
        </p>

        <h3>Open Standards Data Sharing</h3>
        <p>
          Share your data publicly using the latest Open Geospatial Consortium
          web services standard SensorThings.
        </p>
      </div>
    </div>

    <div class="my-8">
      <h2>Operational Data for Modeling</h2>
      <h4>Your data can improve NOAA's water prediction services</h4>
      <p>
        NOAA's National Water Model can assimilate streamflow data from
        operational monitoring sites like yours. Contribute your streamflow data
        to make it available to support continental-scale hydrologic modeling
        and forecasting via the National Water Model.
      </p>

      <h2>Open Standards Data Sharing</h2>
      <p>
        Share your data publicly using the latest Open Geospatial Consortium web
        services standard SensorThings.
      </p>
    </div>

    <div class="my-8">
      <p>
        This HydroServer instance is supported through the Cooperative Institute
        for Research to Operations in Hydrology (CIROH)
      </p>
    </div>
  </v-container>

  <hr />
  <h2 style="margin-bottom: 1.5rem; margin-top: 3rem">
    Open Standards Data Sharing
  </h2>
  <p style="margin-bottom: 5rem">
    Share your data publicly using the latest Open Geospatial Consortium web
    services standard SensorThings.
  </p>
</template>

<script setup lang="ts">
import resistanceIcon from '@/assets/resistance.svg'
import gearIcon from '@/assets/gear.svg'
import dbIcon from '@/assets/db.svg'
import ogcIcon from '@/assets/ogc.png'
</script>

<style scoped lang="scss">
p {
  max-width: 40rem;
}
</style>
