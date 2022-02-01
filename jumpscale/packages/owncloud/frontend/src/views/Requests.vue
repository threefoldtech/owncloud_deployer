<template>
  <div>
    <Navbar />
    <BalanceCard />
    <h4 class="h4 pa-5">Requests:</h4>
    <v-data-table
      class="ma-5 elevation-1"
      :headers="headers"
      :items="requestsWithIndex"
      item-key="tname"
      show-select
      :loading="isLoading"
      loading-text="Loading... Please wait"
      v-model="selected"
      :items-per-page="5"
    >
      <template v-slot:item.index="{ item }">{{ item.index }}</template>
      <template v-slot:item.email="{ item }">{{
        item.email == "" ? "-" : item.email
      }}</template>
      <template v-slot:item.status="{ item }">
        <td>
          <v-chip class="status" :class="item.status">{{ item.status }}</v-chip>
        </td>
      </template>
      <template v-slot:item.time="{ item }">{{ time(item.time) }}</template>
    </v-data-table>
    <div class="text-center pt-2 mt-10">
      <v-btn class="mr-2 bg-blue white--text" @click="deploy(selected)"
        ><v-icon left> mdi-cloud-upload</v-icon> Deploy</v-btn
      >
      <v-btn class="mr-2 bg-blue white--text" @click="deploy(selected)"
        ><v-icon left> mdi-reload</v-icon>Redeploy</v-btn
      >
      <v-btn class="bg-blue white--text" @click="exportData()"
        ><v-icon left> mdi-export-variant</v-icon>Export</v-btn
      >
    </div>
  </div>
</template>

<script>
import Navbar from "@/components/Navbar.vue";
import BalanceCard from "@/components/BalanceCard.vue";
import Service from "../services/Services";
import moment from "moment";
export default {
  components: {
    BalanceCard,
    Navbar,
  },
  data() {
    return {
      headers: [
        { text: "#", value: "index" },
        { text: "Name", value: "tname" },
        { text: "Email", value: "email" },
        { text: "Status", value: "status" },
        { text: "Time", value: "time" },
        {
          text: "Admin Selection",
          value: "data-table-select",
          sortable: false,
        },
      ],
      isLoading: true,
      requests: [],
      selected: [],
    };
  },
  methods: {
    getRequests() {
      Service.getRequests()
        .then((response) => {
          this.requests = response.data;
          this.isLoading = false;
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
    deploy(name) {
      this.isLoading = true;
      Service.deploy(name)
        .then(() => {
          this.getRequests();
          this.isLoading = true;
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
    exportData() {
      Service.exportData()
        .then((response) => {
          this.exportCSVFile(response.data);
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },

    exportCSVFile(items) {
      // Convert Object to JSON
      var jsonObject = JSON.stringify(items);

      var csv = this.convertToCSV(jsonObject);

      var exportedFilenmae = "data.csv";

      var blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
      if (navigator.msSaveBlob) {
        // IE 10+
        navigator.msSaveBlob(blob, exportedFilenmae);
      } else {
        var link = document.createElement("a");
        if (link.download !== undefined) {
          // feature detection
          // Browsers that support HTML5 download attribute
          var url = URL.createObjectURL(blob);
          link.setAttribute("href", url);
          link.setAttribute("download", exportedFilenmae);
          link.style.visibility = "hidden";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
      }
    },

    convertToCSV(objArray) {
      var array = typeof objArray != "object" ? JSON.parse(objArray) : objArray;
      var str = "";

      for (var i = 0; i < array.length; i++) {
        var line = "";
        for (var index in array[i]) {
          if (line != "") line += ",";

          line += array[i][index];
        }

        str += line + "\r\n";
      }

      return str;
    },
    time(ts) {
      var timestamp = moment.unix(ts);
      var now = new Date();
      return timestamp.to(now);
    },
  },
  computed: {
    requestsWithIndex() {
      return this.requests.map((requests, index) => ({
        ...requests,
        index: index + 1,
      }));
    },
  },
  mounted() {
    this.getRequests();
  },
};
</script>

<style >
.v-chip {
  color: #fff !important;
}
.v-chip.v-size--default {
  border-radius: 2px;
  height: 25px;
}
.v-chip.NEW {
  background-color: #2dccff !important;
}
.v-chip.PENDING {
  background-color: #9ea7ad !important;
}
.v-chip.DONE {
  background-color: #56f000 !important;
}
.v-chip.FAILURE {
  background-color: #ff3838 !important;
}
.bg-blue {
  background-color: #041e42 !important;
}
</style>