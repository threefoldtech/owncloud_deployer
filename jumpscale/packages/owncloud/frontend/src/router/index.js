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

router.beforeEach((to, from, next) => {
  // Redirect if fullPath begins with a hash (ignore hashes later in path)
  if (to.fullPath.substring(0, 2) === "/#") {
    const path = to.fullPath.substring(2);
    next(path);
    return;
  }
  next();
});