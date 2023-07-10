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
        <v-btn-primary to="/SignUp">Sign Up</v-btn-primary>
      </div>
    </div>
  </v-parallax>

  <v-container class="my-8">
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
        <div
          class="d-flex flex-column flex-sm-row gap-1 text-center text-sm-left"
        >
          <div class="text-center">
            <v-icon icon="mdi-resistor" size="4rem" />
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
        <div
          class="d-flex flex-column flex-sm-row gap-1 text-center text-sm-left"
        >
          <div class="text-center">
            <v-icon icon="mdi-database-outline" size="4rem" />
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
        <div
          class="d-flex flex-column flex-sm-row gap-1 text-center text-sm-left"
        >
          <div class="text-center">
            <v-icon icon="mdi-cog-outline" size="4rem" />
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
        <div
          class="d-flex flex-column flex-sm-row gap-1 text-center text-sm-left"
        >
          <div class="text-center">
            <v-icon icon="mdi-lock-open-outline" size="4rem" />
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

  <v-container class="my-8">
    <v-row>
      <v-col
        class="d-flex flex-column justify-center align-center gap-2"
        cols="12"
        sm="5"
        order="last"
        order-sm="first"
      >
        <v-img
          :src="noaaLogo"
          max-width="12rem"
          class="fill-width"
          alt="NOAA Logo"
        ></v-img>
        <v-img
          :src="owpLogo"
          max-width="18rem"
          class="fill-width"
          alt="OWP Logo"
        ></v-img>
      </v-col>
      <v-col class="d-flex justify-center flex-column" cols="12" sm="7">
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

  <v-container class="my-8">
    <v-row>
      <v-col class="d-flex flex-column justify-center" cols="12" sm="6">
        <h4 class="text-h4 mb-8">Open Standards Data Sharing</h4>
        <p class="text-body-1 text-medium-emphasis">
          Share your data publicly using the latest Open Geospatial Consortium
          web services standard SensorThings.
        </p>
        <div>
          <v-img
            :src="ogcLogo"
            max-width="26rem"
            height="auto"
            alt="OGC Logo"
          ></v-img>
        </div>
      </v-col>
      <v-col cols="12" sm="6" class="d-flex flex-column align-center gap-2">
        <v-img
          :src="sensorThingsLogo"
          class="fill-width"
          max-width="35rem"
          alt="SensorThings Database Schema"
        ></v-img>
        <h4 class="text-h4">SensorThings</h4>
      </v-col>
    </v-row>
  </v-container>

  <v-divider> </v-divider>

  <v-container class="d-flex flex-column align-center my-8 gap-2">
    <v-img
      :src="cirohLogo"
      class="fill-width"
      max-width="14rem"
      alt="CIROH Logo"
    ></v-img>
    <p class="text-body-1 text-medium-emphasis text-center">
      This HydroServer instance is supported through the Cooperative Institute
      for Research to Operations in Hydrology (CIROH)
    </p>
  </v-container>
</template>

<script setup lang="ts">
import noaaLogo from '@/assets/noaa.svg'
import owpLogo from '@/assets/owp.png'
import ogcLogo from '@/assets/ogc.svg'
import cirohLogo from '@/assets/ciroh.png'
import sensorThingsLogo from '@/assets/sensorThings.png'
</script>

<style scoped lang="scss">
.v-container {
  max-width: 1200px;
}

p {
  max-width: 40rem;
}
</style>
