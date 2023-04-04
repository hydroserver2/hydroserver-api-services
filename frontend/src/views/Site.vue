<template>
  <h1>Site: {{ siteName }}</h1>
</template>

<script>
export default {
  name: "SingleSite",
  data() {
    return {
      siteName: "",
    };
  },
  created() {
    const siteId = this.$route.params.id;
    // make an API call to retrieve site name using the siteId
    // then set the siteName property to the retrieved site name
    this.siteName = "Site " + siteId;
  },
};
</script>