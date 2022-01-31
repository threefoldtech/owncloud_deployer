<template>
  <div>
    <h1 class="pa-5">Requests</h1>
    <v-data-table
      :headers="headers"
      :items="requests"
      :items-per-page="5"
    ></v-data-table>
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
          console.log(response);
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
  },
  mounted() {
    this.getRequests();
  },
};
</script>