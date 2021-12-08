from flask import Flask, jsonify
from flask_cors import CORS
import random

from transformers import pipeline
import os

DEBUG = True

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# 文本摘要
# summarizer = pipeline("summarization")
# 情感分析
# classifier = pipeline("sentiment-analysis")

app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

# 预留的接口
@app.route('/analyze/<text>', methods=['GET'])
def analyze(text):
    print("载荷文本:" + text)

    result = classifier(text)[0]
    # 处理文本
    # ...
    # 最终结果 positive 和 negative
    print(result)
    label = result['label']
    score = result['score']
    return jsonify([label,score])

if __name__ == '__main__':
    app.run()
