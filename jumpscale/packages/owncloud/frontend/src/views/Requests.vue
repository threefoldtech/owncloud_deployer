<template>
  <div>
    <h1 class="pa-5">Requests</h1>
    <BalanceCard />
    <v-data-table
      class="ma-5"
      :headers="headers"
      :items="requests"
      v-model="selected"
      item-key="name"
      :items-per-page="5"
    >
      <template v-slot:item.email="{ item }">{{
        item.email == "" ? "-" : item.email
      }}</template>
      <template v-slot:item.status="{ item }">
        <td>
          <v-chip class="status" :class="item.status">{{ item.status }}</v-chip>
        </td>
      </template>
      <template v-slot:item.time="{ item }">{{ time(item.time) }}</template>
      <template v-slot:item.admin_selection="{ item }">
        <v-checkbox v-model="item.admin_selection" />
      </template>
    </v-data-table>
    <div class="text-right pt-2 mt-10">
      <v-btn color="primary" class="mr-2"
        ><v-icon dark left> mdi-cloud-upload</v-icon> Deploy</v-btn
      >
      <v-btn color="primary" class="mr-2"
        ><v-icon dark left> mdi-reload</v-icon>Redeploy</v-btn
      >
      <v-btn color="primary" @click="exportData()"
        ><v-icon dark left> mdi-export-variant</v-icon>Export</v-btn
      >
    </div>
  </div>
</template>

<script>
import BalanceCard from "@/components/BalanceCard.vue";
import Service from "../services/Services";
import moment from "moment";
export default {
  components: {
    BalanceCard,
  },
  data() {
    return {
      headers: [
        { text: "#", value: "id" },
        { text: "Name", value: "tname" },
        { text: "Email", value: "email" },
        { text: "Status", value: "status" },
        { text: "Time", value: "time" },
        { text: "Admin Selection", value: "admin_selection", sortable: false },
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
    exportData() {
      Service.exportData()
        .then((response) => {
          var json = $.parseJSON(response.data);
          var csv = this.JSON2CSV(json);
          var downloadLink = document.createElement("a");
          var blob = new Blob(["\ufeff", csv]);
          var url = URL.createObjectURL(blob);
          downloadLink.href = url;
          downloadLink.download = "data.csv";
          document.body.appendChild(downloadLink);
          downloadLink.click();
          document.body.removeChild(downloadLink);
        })
        .catch((error) => {
          console.log("Error! Could not reach the API. " + error);
        });
    },
    JSON2CSV(objArray) {
      var array = typeof objArray != "object" ? JSON.parse(objArray) : objArray;
      var str = "";
      var line = "";

      if ($("#labels").is(":checked")) {
        var head = array[0];
        if ($("#quote").is(":checked")) {
          for (var index in array[0]) {
            var value = index + "";
            line += '"' + value.replace(/"/g, '""') + '",';
          }
        } else {
          for (var index in array[0]) {
            line += index + ",";
          }
        }

        line = line.slice(0, -1);
        str += line + "\r\n";
      }

      for (var i = 0; i < array.length; i++) {
        var line = "";

        if ($("#quote").is(":checked")) {
          for (var index in array[i]) {
            var value = array[i][index] + "";
            line += '"' + value.replace(/"/g, '""') + '",';
          }
        } else {
          for (var index in array[i]) {
            line += array[i][index] + ",";
          }
        }

        line = line.slice(0, -1);
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
</style>