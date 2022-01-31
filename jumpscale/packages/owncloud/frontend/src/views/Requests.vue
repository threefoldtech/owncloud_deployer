<template>
  <div>
    <h1 class="pa-5">Requests</h1>
    <v-data-table
      :headers="headers"
      :items="data"
      :items-per-page="5"
      loading
      loading-text="Loading... Please wait"
    ></v-data-table>
    <div class="text-center pt-2 mt-10">
      <v-btn color="primary" class="mr-2"> btn 1 </v-btn>
      <v-btn color="primary"> btn 2 </v-btn>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      headers: [
        { text: "Name", value: "name" },
        { text: "Email", value: "email" },
        { text: "Status", value: "status" },
        { text: "Time", value: "time" },
      ],
      data: [
        {
          name: "Eaton Harmon",
          email: "et@google.ca",
          status: "New",
          time: 1643638522,
        },
        {
          name: "Cally Mitchell",
          email: "eget.odio@icloud.net",
          status: "New",
          time: 1643638522,
        },
        {
          name: "Cherokee Vance",
          email: "suspendisse@protonmail.edu",
          status: "New",
          time: 1643638522,
        },
        {
          name: "Signe Greer",
          email: "elit.pharetra@icloud.com",
          status: "New",
          time: 1643638522,
        },
        {
          name: "Harper Reilly",
          email: "arcu.eu@outlook.couk",
          status: "New",
          time: 1643638522,
        },
      ],
    };
  },
};
</script>