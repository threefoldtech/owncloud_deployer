<template>
  <v-app-bar color="blue" dense elevation="4" flat outlined rounded shaped>
    <v-img
      :src="require('../assets/logo.svg')"
      max-height="60"
      max-width="75"
    ></v-img
  ></v-app-bar>
</template>

<style scoped>
.v-application .blue {
  background-color: #041e42 !important;
}

.v-image {
    margin: auto;
}
</style>