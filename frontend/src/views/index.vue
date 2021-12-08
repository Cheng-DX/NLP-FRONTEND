<template>
  <div class="root">
    <h2 class="title">英法互译</h2>
    <div class="main">
      <textarea class="textarea" autofocus v-model="msg" />
      <div class="button-group">
        <el-button
          class="button"
          icon="el-icon-data-analysis"
          :loading="loading"
          @click="translate"
          >{{ buttonText }}</el-button
        >
        <el-button class="button" style="background: rgb(219, 91, 17)" icon='el-icon-refresh' @click="changeText">换一个示例</el-button>
      </div>

      <textarea class="textarea" autofocus v-model="result" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
document.title = "Translation";
export default {
  data() {
    return {
      baseUrl: "http://localhost:5000",
      msg: "je mon",
      result: "",
      loading: false,
      candicateText: [],
    };
  },
  computed: {
    buttonText() {
      return this.loading ? "翻译中" : "翻译";
    },
  },
  methods: {
    translate() {
      this.loading = true;
      let url = "/analyze";
      axios
        .get(this.baseUrl + url + "/" + this.msg)
        .then((res) => {
          console.log(res.data);
        })
        .catch((err) => {
          console.log(err);
          this.$message.error(err);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    changeText() {
      this.msg =
        this.candicateText[
          Math.floor(Math.random() * this.candicateText.length)
        ];
    },
  },
};
</script>

<style scoped>
.root {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #161623;
}
.root::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(#f00, #f0f);
  clip-path: circle(40% at right 70%);
}
.root::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(#2196f3, #e91e63);
  clip-path: circle(20% at 10% 10%);
}
.textarea {
  position: relative;
  width: 50vw;
  height: 30vh;
  padding: 10px;
  color: rgba(255, 255, 255, 0.705);
  border: none;
  overflow: hidden;
  border-radius: 15px;
  background: #ffffff09;
  box-shadow: 20px 20px 10px rgba(0, 0, 0, 0.116);
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(5px);
  z-index: 1;

  font-size: 20px;
  font-family: "Roboto", sans-serif;
}

.title {
  display: flex;
  text-align: center;
  color: #ffffffa1;
  justify-content: center;
}
.button {
  height: 10%;
  width: auto;
  background: #2195f3;
  color: white;
  font-size: 20px;
  border: none;
  border-radius: 5px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.116);
  z-index: 1;
}
.main {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.button-group{
  display: flex;
  justify-content: center;
  margin: 20px;
}
</style>