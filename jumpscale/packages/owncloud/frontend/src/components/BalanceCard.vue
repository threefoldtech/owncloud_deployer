<template>
  <div>
    <v-card v-if="balance" class="mt-16 mx-auto" max-width="344" outlined>
      <v-list-item>
        <v-list-item-content>
          <div class="text-center text-overline mb-4">Current balance</div>
          <v-list-item-title v-if="balance" class="text-center text-h5 mb-1">
            {{ balance }} <span class="price">TFT</span>
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-card>
    <v-alert
      v-if="balance && balance < 1000"
      class="mb-16 mx-auto"
      max-width="344"
      dense
      outlined
      type="error"
    >
      {{ message }}
    </v-alert>
  </div>
</template>

<script>
import Service from "../services/Services";

export default {
  props: ["setBalance"],
  data() {
    return {
      balance: null,
      message: "New deployments have been disabled because balance < 1000",
      timer: "",
    };
  },
  methods: {
    getBalance() {
      Service.getBalance()
        .then((response) => {
          this.balance = response.data.balance;
        })
        .then(() => this.$emit("setBalance", this.balance))
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
    cancelAutoUpdate () {
            clearInterval(this.timer);
            this.timer = "";
    },
  },
  created() {
    this.getBalance();
    this.timer = setInterval(this.getBalance, 10000);
  },
  destroyed() {
    this.cancelAutoUpdate();
  },
};
</script>

<style >
.price {
  font-size: 1rem;
}
</style>