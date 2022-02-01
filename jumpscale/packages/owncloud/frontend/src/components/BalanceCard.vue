<template>
  <v-card class="ml-auto" max-width="344" outlined>
    <v-list-item>
      <v-list-item-content>
        <div class="text-overline mb-4">Current balance</div>
        <v-list-item-title class="text-h5 mb-1">
          {{ balance }}
        </v-list-item-title>
      </v-list-item-content>
    </v-list-item>
  </v-card>
</template>

<script>
import Service from "../services/Services";

export default {
  data() {
    return {
      balance: 0,
    };
  },
  methods: {
    getBalance() {
      Service.getBalance()
        .then((response) => {
          this.balance = response.data;
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
  },
  mounted() {
    this.getBalance();
  },
};
</script>