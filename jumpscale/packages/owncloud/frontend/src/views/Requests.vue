<template>
  <div>
    <h1 class="pa-5">Requests</h1>
    <v-data-table
      :headers="headers"
      :items="requests"
      :items-per-page="5"
      :loading="loading"
      loading-text="Loading... Please wait"
    >
      <template v-slot:item.email="{ item }">{{
        item.email == "" ? "-" : item.email
      }}</template>
      <template
        v-slot:item.status="{ item }"
        class="status"
        :class="{
          available: item.status == 'new',
          disabled: item.status == 'pending',
          normal: item.status == 'done',
          failure: item.status == 'failure',
        }"
        >{{ status }}></template
      >
      <template v-slot:item.time="{ item }">{{ time(item.time) }}</template>
      <template v-slot:item.selected="{ item }">
        <v-checkbox v-model="selected" :value="item.selected"></v-checkbox>
      </template>
    </v-data-table>
    <div class="text-right pt-2 mt-10">
      <v-btn color="primary" class="mr-2">Deploy</v-btn>
      <v-btn color="primary" class="mr-2">Redeploy</v-btn>
      <v-btn color="primary">Export</v-btn>
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
        { text: "#", value: "id" },
        { text: "Name", value: "tname" },
        { text: "Email", value: "email" },
        { text: "Status", value: "status" },
        { text: "Time", value: "time" },
        { text: "Admin Selection", value: "selected" },
      ],
      requests: [],
      loading: true,
      selected: [],
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

<style >
.status {
  color: #fff;
}
.available {
  background-color: #2dccff;
}
.disabled {
  background-color: #9ea7ad;
}
.normal {
  background-color: #56f000;
}
.failure {
  background-color: #ff3838;
}
</style>