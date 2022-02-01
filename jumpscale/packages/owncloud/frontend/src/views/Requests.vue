<template>
  <div>
    <h1 class="pa-5">Requests</h1>
    <v-data-table
      :headers="headers"
      :items="requests"
      :items-per-page="5"
      loading
      loading-text="Loading... Please wait"
    >
      <template v-slot:item.email="{ item }">{{
        item.email == "" ? "-" : item.email
      }}</template>
      <template v-slot:item.time="{ item }">{{ timeSince(item) }}</template>
    </v-data-table>
    <div class="text-center pt-2 mt-10">
      <v-btn color="primary" class="mr-2"> btn 1 </v-btn>
      <v-btn color="primary"> btn 2 </v-btn>
    </div>
  </div>
</template>

<script>
import Service from "../services/Services";

export default {
  data() {
    return {
      headers: [
        { text: "Name", value: "tname" },
        { text: "Email", value: "email" },
        { text: "Status", value: "status" },
        { text: "Time", value: "time" },
      ],
      requests: [],
    };
  },
  methods: {
    getRequests() {
      Service.getRequests()
        .then((response) => {
          this.requests = response.data;
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
    timeSince(date) {
      var seconds = Math.floor((new Date() - date) / 1000);

      var interval = seconds / 31536000;

      if (interval > 1) {
        return Math.floor(interval) + " years";
      }
      interval = seconds / 2592000;
      if (interval > 1) {
        return Math.floor(interval) + " months";
      }
      interval = seconds / 86400;
      if (interval > 1) {
        return Math.floor(interval) + " days";
      }
      interval = seconds / 3600;
      if (interval > 1) {
        return Math.floor(interval) + " hours";
      }
      interval = seconds / 60;
      if (interval > 1) {
        return Math.floor(interval) + " minutes";
      }
      return Math.floor(seconds) + " seconds";
    },
  },
  mounted() {
    this.getRequests();
  },
};
</script>