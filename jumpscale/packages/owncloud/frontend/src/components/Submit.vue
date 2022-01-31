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
            :src="require('../assets/logo.svg')"
            max-height="120"
            max-width="120"
          ></v-img>

          <v-card-title>
            <h2 class="pt-md-13 white--text">
              {{ title }}
            </h2>
          </v-card-title>
        </v-card>
      </v-col>
      <v-col
        cols="6"
        md="7"
        class="d-flex pa-md-16"
        style="flex-direction: column"
      >
        <v-card class="ma-md-16 mx-lg-auto align-center flex-grow-1">
          <p>
            Please enter your email to get creds and domain for you instance on.
            If not provided email TF connect will be used.
          </p>
          <v-form ref="form" v-model="valid" lazy-validation>
            <v-text-field
              v-model="email"
              :rules="emailRules"
              label="E-mail"
              required
            ></v-text-field>
            <v-input
              v-if="sent"
              :success-messages="['Mail sent successfully!']"
              success
            >
            </v-input>

            <v-checkbox
              v-model="checkbox"
              :rules="[(v) => !!v || 'You must agree to continue!']"
              label="Agree at Terms &amp; conditions"
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
    </v-row>
  </v-container>
</template>

<script>
import Service from "../services/Services";

export default {
  data: () => ({
    title: "Welcome to Owncloud Free Deployment",
    valid: false,
    email: "",
    emailRules: [
      (v) => !!v || "E-mail is required",
      (v) => /.+@.+\..+/.test(v) || "E-mail must be valid",
    ],
    checkbox: false,
    sent: false,
  }),

  methods: {
    validate() {
      this.$refs.form.validate();
    },
    submit() {
      this.validate();
      Service.sendMails(this.email)
        .then((response) => {
          console.log("response:" + response);
          this.valid = true;
        })
        .catch((error) => {
          console.log("error:" + error);
          if (error.response.status == 503) {
            console.log(error.response.data);
          } else if (error.response.status == 401) {
            console.log("Please contact Adminstrator");
          } else {
            console.log("Error! Could not reach the API. " + error);
          }
        });
    },
  },
  computed: {
    deviceHeight() {
      return this.$vuetify.breakpoint.height;
    },
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
