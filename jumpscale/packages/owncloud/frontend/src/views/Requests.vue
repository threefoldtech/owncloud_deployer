<template>
  <div>
    <h1 class="pa-5">Requests</h1>
    <v-data-table
      :headers="headers"
      :items="requests"
      :items-per-page="5"
      v-if="loading"
      loading-text="Loading... Please wait"
    >
      <template v-slot:item.email="{ item }">{{
        item.email == "" ? "-" : item.email
      }}</template>
      <template v-slot:item.time="{ item }">{{ time(item.time) }}</template>
    </v-data-table>
    <div class="text-center pt-2 mt-10">
      <v-btn color="primary" class="mr-2"> btn 1 </v-btn>
      <v-btn color="primary"> btn 2 </v-btn>
    </div>
  </div>
</template>

<script>
import Service from "../services/Services";
import moment from "moment";
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
      loading: true,
    };
  },
  methods: {
    getRequests() {
      Service.getRequests()
        .then((response) => {
          this.requests = response.data;
          this.loading = false;
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
    time(ts) {
      var timestamp = moment.unix(ts);
      var now = new Date();
      return timestamp.to(now);
    },
  },
  mounted() {
    this.getRequests();
  },
};
</script>