import Vue from "vue";
import VueRouter from "vue-router";
import Home from "../views/Home.vue";
import Requests from "../views/Requests.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/requests",
    name: "Requests",
    component: Requests,
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
