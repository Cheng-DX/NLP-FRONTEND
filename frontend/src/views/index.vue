<template>
  <div>
    <div id="visiless">
      <el-dialog :visible.sync="showHistory" width="60%" top="10vh">
        <el-table :data="history" height="70vh" center>
          <el-table-column
            align="center"
            type="index"
            label="INDEX"
            width="100px"
          />
          <el-table-column align="center" prop="input" label="输入" />
          <el-table-column align="center" prop="output" label="结果" />
        </el-table>
      </el-dialog>
      <el-dialog :visible.sync="showChart1" width="70%" top="5vh">
        <div style="height: 75vh" :key="index">
          <v-chart :option="chart1" />
        </div>
      </el-dialog>
      <el-dialog :visible.sync="showChart2" width="70%" top="5vh">
        <div style="height: 75vh" :key="index">
          <v-chart :option="chart2" />
        </div>
      </el-dialog>
    </div>
    <el-container>
      <el-header style="padding: 0px">
        <div class="toolbar">
          <div class="logo">
            {{ mode }}
          </div>
          <el-button
            v-for="(item, index) in toolbarButtons"
            :key="index"
            @click="item.method"
            type="text"
            class="button-toolbar"
            >{{ item.name }}</el-button
          >
        </div>
      </el-header>
      <el-main>
        <div class="root">
          <div class="main">
            <textarea class="textarea" autofocus v-model="msg" />
            <div class="button-group">
              <el-tooltip
                effect="dark"
                v-for="(item, index) in centerButtons"
                :content="item.tooltipContent"
                placement="top"
                :open-delay="1000"
                :key="index"
              >
                <el-button
                  v-if="item.isBindLoading"
                  class="button"
                  :icon="item.icon"
                  :loading="loading"
                  @click="handleClick(item.method)"
                />
                <el-button
                  v-else
                  class="button"
                  :icon="item.icon"
                  @click="handleClick(item.method)"
                />
              </el-tooltip>
            </div>
            <textarea class="textarea" v-model="result" />
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from "axios";
import Toolbar from "../components/Toolbar.vue";
document.title = "Translation";
export default {
  components: { Toolbar },
  data() {
    return {
      baseUrl: "http://localhost:5000",
      msg: "je suis juste paresseux .",
      result: "",
      loading: false,
      candicateText: [
        [
          "vous etes probablement trop jeune pour le comprendre .",
          "you re probably too young to understand this .",
        ],
        [
          "tu es probablement trop jeune pour le comprendre .",
          "you re probably too young to understand this .",
        ],
        [
          "je pense apprendre le coreen le semestre prochain .",
          "i m thinking of learning korean next semester .",
        ],
        [
          "elle trouve toujours a redire aux autres .",
          "she is always finding fault with other people .",
        ],
        [
          "elle est tres receptive a la suggestion hypnotique .",
          "she s very susceptible to hypnotic suggestion .",
        ],
        [
          "nous enquetons sur le meurtre de tom jackson .",
          "we re investigating the murder of tom jackson .",
        ],
        [
          "elle est non seulement belle mais aussi intelligente .",
          "she is not only beautiful but also intelligent .",
        ],
        [
          "il entreprend des experiences dans son laboratoire .",
          "he is carrying out experiments in his laboratory .",
        ],
        [
          "j ai quelques difficultes a compiler ce programme .",
          "i m having some problems compiling this software .",
        ],
        [
          "ils collectent des dons pour l eglise .",
          "they are collecting contributions for the church .",
        ],
        [
          "il est un des candidats aux presidentielles americaines .",
          "he is one of the american presidential candidates .",
        ],
        ["je suis chez moi tom .", "i m home tom ."],
        ["j ai mal au c ur .", "i m hung over ."],
        ["je suis impatient .", "i m impatient ."],
        ["je suis impatiente .", "i m impatient ."],
        ["je suis important .", "i m important ."],
        ["je suis impressionnee .", "i m impressed ."],
        ["je suis impulsif .", "i m impulsive ."],
        ["je suis impulsive .", "i m impulsive ."],
        ["je suis a boston .", "i m in boston ."],
        ["je suis en danger .", "i m in danger ."],
        ["je suis intrigue .", "i m intrigued ."],
        ["je suis intriguee .", "i m intrigued ."],
        ["cela m intrigue .", "i m intrigued ."],
        ["je suis juste paresseux .", "i m just lazy ."],
        ["je suis juste paresseuse .", "i m just lazy ."],
        ["j ecoute .", "i m listening ."],
        ["je suis motivee .", "i m motivated ."],
        ["je suis motive .", "i m motivated ."],
        ["je ne suis pas un expert .", "i m no expert ."],
        ["je ne suis pas flic .", "i m not a cop ."],
        ["je ne fais pas partie de ses admirateurs .", "i m not a fan ."],
        ["je ne fais pas partie de leurs admirateurs .", "i m not a fan ."],
        ["je ne suis pas seul .", "i m not alone ."],
        ["je ne suis pas seule .", "i m not alone ."],
        ["je ne suis pas en colere !", "i m not angry !"],
        ["je ne suis pas en colere .", "i m not angry ."],
        ["je ne suis pas arme .", "i m not armed ."],
        ["je ne suis pas armee .", "i m not armed ."],
        ["je ne suis pas aveugle .", "i m not blind ."],
        ["je ne suis pas fou .", "i m not crazy ."],
        ["je ne suis pas folle .", "i m not crazy ."],
      ],
      lang: "fra",
      showHistory: false,
      showChart1: false,
      showChart2: false,
      eng: "",
      toolbarButtons: [
        {
          name: "切换语言",
          method: () => {
            this.lang = this.lang === "fra" ? "eng" : "fra";
          },
        },
        {
          name: "beamsize",
          method: () => {
            this.showChart1 = true;
          },
        },
        {
          name: "训练量",
          method: () => {
            this.showChart2 = true;
          },
        },
        {
          name: "ABOUT",
          method: () => {
            window.open("https://github.com/Cheng-DX/NLP-FRONTEND");
          },
        },
      ],
      centerButtons: [
        {
          name: "TRANSLATE",
          method: "translate",
          isBindLoading: true,
          tooltipContent: "翻译",
          icon: "el-icon-right",
        },
        {
          name: "CHANGETEXT",
          method: "changeText",
          isBindLoading: false,
          tooltipContent: "换一个示例",
          icon: "el-icon-refresh",
        },
        {
          name: "SHOWENG",
          method: "showEng",
          isBindLoading: false,
          tooltipContent: "提示",
          icon: "el-icon-magic-stick",
        },
      ],
      history: [],
      xData: ["sentence1", "sentence2", "sentence3", "sentence4", "sentence5"],
      chart1yData1: [0.178, 0.234, 0.452, 0.091, 0.233],
      chart1yData2: [1, 0.479, 1, 1, 0.783],
      chart2yData1: [1, 0.479, 1, 1, 0.783],
      chart2yData2: [1, 1, 1, 1, 1],
    };
  },
  created() {
    this.chart1 = {
      title: {
        text: "beamsize=1与beamsize=5的对比",
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      legend: {},
      grid: {
        left: "3%",
        right: "4%",
        bottom: "3%",
        containLabel: true,
      },
      xAxis: {
        type: "value",
        boundaryGap: [0, 0.01],
      },
      yAxis: {
        type: "category",
        data: this.xData,
      },
      toolbox: {
        feature: {
          show: true,
          restore: {},
          saveAsImage: {
            pixelRatio: 5,
          },
        },
      },
      series: [
        {
          name: "beamsize=1",
          type: "bar",
          data: this.chart1yData1,
        },
        {
          name: "beamsize=5",
          type: "bar",
          data: this.chart1yData2,
        },
      ],
    };
    this.chart2 = {
      title: {
        text: "训练量不同模型对比 beamsize=5",
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow",
        },
      },
      legend: {},
      grid: {
        left: "3%",
        right: "4%",
        bottom: "3%",
        containLabel: true,
      },
      toolbox: {
        feature: {
          show: true,
          restore: {},
          saveAsImage: {
            pixelRatio: 5,
          },
        },
      },
      xAxis: {
        type: "value",
        boundaryGap: [0, 0.01],
      },
      yAxis: {
        type: "category",
        data: this.xData,
      },
      series: [
        {
          name: "1万条数据 训练7万次",
          type: "bar",
          data: this.chart2yData1,
        },
        {
          name: "6万条训练40万次 ",
          type: "bar",
          data: this.chart2yData2,
        },
      ],
    };
  },
  computed: {
    mode: function () {
      return this.lang === "fra" ? "GERMAN ➡ ENGLISH" : "ENGLISH ➡ GERMAN";
    },
  },
  methods: {
    handleClick(method) {
      let methods = this.$options.methods;
      let _this = this;
      methods[method](_this);
    },
    translate(_this) {
      _this.loading = true;
      let url = "/translate";
      axios
        .get(_this.baseUrl + url + "/" + _this.msg + "/" + _this.lang)
        .then((res) => {
          let result = res.data[0];
          let hasError = res.data[1];
          let errorMsg = res.data[2];

          if (hasError === false) {
            _this.result = result;
            _this.history.push({
              fra: _this.msg,
              eng: result,
            });
          } else {
            _this.$message({
              type: "error",
              message: errorMsg,
            });
          }
        })
        .catch((err) => {
          console.log(err);
          _this.$message.error(err);
        })
        .finally(() => {
          _this.loading = false;
        });
    },
    changeText(_this) {
      let choice =
        _this.candicateText[
          Math.floor(Math.random() * _this.candicateText.length)
        ];
      if (_this.lang === "fra") {
        _this.msg = choice[0];
        _this.eng = choice[1];
      } else {
        _this.msg = choice[1];
        _this.eng = choice[0];
      }
    },
    showEng(_this) {
      _this.$message({
        type: "info",
        message: _this.eng,
      });
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
  background-image: "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.freepik.com%2Fphotos%2Fbackground&psig=AOvVaw1BQ-496e4SMqwKvawfPVVo&ust=1639028800436000&source=images&cd=vfe&ved=0CAgQjRxqFwoTCMinwZ7A0_QCFQAAAAAdAAAAABAI";
  /* background: #fafafa; */
}
.textarea {
  width: 40vw;
  height: 40vh;
  padding: 10px;
  overflow: hidden;
  border-radius: 15px;
  background: transparent;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
  z-index: 1;
  font-size: 20px;
  font-family: "Roboto", sans-serif;
}
.button {
  height: 10%;
  background: #ffffff00;
  border: none;
  color: rgb(0, 0, 0);
  margin: 20px;
  font-size: 20px;
  /* border: none; */
  border-radius: 5px;
  z-index: 1;
}
.main {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-top: 6%;
}
.button-group {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #2269c5cb;
  height: 100%;
  padding: 0 10px;
  margin-left: auto;
  font-family: -webkit-pictograph;
}
.button-toolbar {
  margin: 10px;
  font-size: 15px;
  border: none;
  color: #fff;
}
.logo {
  display: flex;
  /* justify-content: space-evenly; */
  text-align: center;
  height: 80%;
  width: 80%;
  color: white;
  font-size: 30px;
  align-content: stretch;
}
</style>