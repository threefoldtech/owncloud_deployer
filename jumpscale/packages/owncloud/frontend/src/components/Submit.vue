<template>
  <v-container>
    <v-row
      :style="{
        height: deviceHeight * 0.6 + 'px',
        marginTop: (deviceHeight * 0.6) / 4 + 'px',
      }"
      class="outlined"
      no-gutters
    >
      <v-col
        cols="12"
        sm="6"
        md="5"
        class="d-flex"
        style="flex-direction: column"
      >
        <v-card class="pa-md-13 mx-lg-auto bg-blue flex-grow-1">
          <v-img
            :src="require('../assets/tft_and_owncloud.png')"
            height="auto"
            max-width="300"
          ></v-img>

          <v-card-title>
            <h2 class="pt-md-13 white--text">
              {{ title }}
            </h2>
          </v-card-title>
        </v-card>
      </v-col>
      <v-col cols="6" md="7" class="d-flex" style="flex-direction: column">
        <v-card class="ma-md-16 pa-md-16 mx-lg-auto align-center flex-grow-1">
          <p>
            {{ tfmail }} will be used to send you your deployment information.
            If you prefer to receive emails on a different address, fill in
            below
          </p>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-text-field
              v-model="email"
              :rules="emailRules"
              label="E-mail (optional)"
            ></v-text-field>

            <v-checkbox
              v-model="checkbox"
              :rules="[(v) => !!v || 'You must agree to continue!']"
              label="I have read and I accept the terms and conditions"
              required
            ></v-checkbox>

            <v-btn
              :disabled="!valid"
              class="mr-4 bg-blue white--text"
              @click="submit"
            >
              Submit
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
      <v-col cols="auto">
        <v-dialog
          transition="dialog-top-transition"
          v-model="dialog"
          max-width="600"
        >
          <template>
            <v-card>
              <v-card-text>
                <div class="text-h5 pa-12">{{ message }}</div>
              </v-card-text>
              <v-card-actions class="justify-end">
                <v-btn text @click="dialog = false">Close</v-btn>
              </v-card-actions>
            </v-card>
          </template>
        </v-dialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Service from "../services/Services";

export default {
  data: () => ({
    title: "Welcome to the Freemium Owncloud Deployer",
    tfmail: "TF-Connect Email",
    valid: true,
    email: "",
    emailRules: [
      (v) =>
        !v ||
        /^\S+@\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b$/.test(v) ||
        "E-mail must be valid",
    ],
    checkbox: null,
    dialog: false,
    message: "",
  }),

  methods: {
    validate() {
      this.$refs.form.validate();
    },
    submit() {
      Service.sendMails(this.email)
        .then((response) => {
          this.dialog = true;
          this.message = response.data;
          this.reset();
        })
        .catch((error) => {
          this.dialog = true;
          this.message = error.response.data;
        });
    },
    getCurrentUserEmail() {
      Service.getCurrentUser()
        .then((response) => {
          this.tfmail = response.data.email;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    reset() {
      this.$refs.form.reset();
    },
  },
  computed: {
    deviceHeight() {
      return this.$vuetify.breakpoint.height;
    },
  },
  mounted() {
    this.getCurrentUserEmail();
  },
};
</script>

<style>
.bg-blue {
  background-color: #041e42 !important;
}
.v-card__text,
.v-card__title {
  line-height: normal !important;
  padding-left: 0 !important;
  word-break: normal !important;
}
.v-card:not(.v-sheet--outlined) {
  box-shadow: none !important;
}
.outlined {
  box-shadow: 0px 3px 1px -2px rgb(0 0 0 / 20%),
    0px 2px 2px 0px rgb(0 0 0 / 14%), 0px 1px 5px 0px rgb(0 0 0 / 12%);
}
</style>
