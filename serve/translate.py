from __future__ import unicode_literals, print_function, division

import re
import torch.nn.functional as F
from flask import Flask, jsonify
from flask_cors import CORS
from io import open
import unicodedata
import torch
import torch.nn as nn
import os

# 评估优化
import heapq
from queue import Queue, PriorityQueue


class Node:
    def __init__(self, gailv, input, hidden, seq):
        self.gailv = gailv
        self.input = input
        self.hidden = hidden
        self.seq = seq

    def __lt__(self, other):
        return self.gailv > other.gailv

    def __cmp__(self, other):
        if self.gailv < other.gailv:
            return -1
        else:
            return 1

    def gethidden(self):
        return self.hidden


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

SOS_token = 0
EOS_token = 1


class Lang:
    def __init__(self, name):
        # 初始化 加入EOS和SOS
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)


def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def normalizeString(s):
    s = unicodeToAscii(s.lower().strip())
    s = re.sub(r"([.!?])", r" \1", s)
    s = re.sub(r"[^a-zA-Z.!?]+", r" ", s)
    return s


def readLangs(lang1, lang2, reverse=False):
    lines = open('data/eng-fra.txt', encoding='utf-8').read().strip().split('\n')
    pairs = [[normalizeString(s) for s in l.split('\t')] for l in lines]
    if reverse:
        pairs = [list(reversed(p)) for p in pairs]
        input_lang = Lang(lang2)
        output_lang = Lang(lang1)
    else:
        input_lang = Lang(lang1)
        output_lang = Lang(lang2)
    return input_lang, output_lang, pairs


MAX_LENGTH = 10
eng_prefixes = (
    "i am ", "i m ",
    "he is", "he s ",
    "she is", "she s ",
    "you are", "you re ",
    "we are", "we re ",
    "they are", "they re "
)


def filterPair(p):
    return len(p[0].split(' ')) < MAX_LENGTH and len(p[1].split(' ')) < MAX_LENGTH and p[1].startswith(eng_prefixes)


def filterPairs(pairs):
    list = [pair for pair in pairs if filterPair(pair)]
    return list


def prepareData(lang1, lang2, reverse=False):
    input_lang, output_lang, pairs = readLangs(lang1, lang2, reverse)
    pairs = filterPairs(pairs)
    for pair in pairs:
        input_lang.addSentence(pair[0])
        output_lang.addSentence(pair[1])
    return input_lang, output_lang, pairs


input_lang, output_lang, pairs = prepareData('eng', 'fra', True)


# encoder
class EncoderRNN(nn.Module):
    def __init__(self, input_size, hidden_size):
        super(EncoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(input_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)

    def forward(self, input, hidden):
        embedded = self.embedding(input).view(1, 1, -1)
        output = embedded
        output, hidden = self.gru(output, hidden)
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)


# decoder
class DecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size):
        super(DecoderRNN, self).__init__()
        self.hidden_size = hidden_size

        self.embedding = nn.Embedding(output_size, hidden_size)
        self.gru = nn.GRU(hidden_size, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, input, hidden):
        output = self.embedding(input).view(1, 1, -1)
        output = F.relu(output)
        output, hidden = self.gru(output, hidden)
        output = self.softmax(self.out(output[0]))
        return output, hidden

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)


# attention
class AttnDecoderRNN(nn.Module):
    def __init__(self, hidden_size, output_size, dropout_p=0.1, max_length=MAX_LENGTH):
        super(AttnDecoderRNN, self).__init__()
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.dropout_p = dropout_p
        self.max_length = max_length

        self.embedding = nn.Embedding(self.output_size, self.hidden_size)
        self.attn = nn.Linear(self.hidden_size * 2, self.max_length)
        self.attn_combine = nn.Linear(self.hidden_size * 2, self.hidden_size)
        self.dropout = nn.Dropout(self.dropout_p)
        self.gru = nn.GRU(self.hidden_size, self.hidden_size)
        self.out = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, input, hidden, encoder_outputs):
        embedded = self.embedding(input).view(1, 1, -1)
        embedded = self.dropout(embedded)

        attn_weights = F.softmax(
            self.attn(torch.cat((embedded[0], hidden[0]), 1)), dim=1)
        attn_applied = torch.bmm(attn_weights.unsqueeze(0),
                                 encoder_outputs.unsqueeze(0))

        output = torch.cat((embedded[0], attn_applied[0]), 1)
        output = self.attn_combine(output).unsqueeze(0)

        output = F.relu(output)
        output, hidden = self.gru(output, hidden)

        output = F.log_softmax(self.out(output[0]), dim=1)
        return output, hidden, attn_weights

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=device)


def indexedFromSentence(lang, sentence):
    return [lang.word2index[word] for word in sentence.split(' ')]


def tensorFromSentence(lang, sentence):
    indexes = indexedFromSentence(lang, sentence)
    indexes.append(EOS_token)
    return torch.tensor(indexes, dtype=torch.long, device=device).view(-1, 1)


def tensorsFromPair(pair):
    input_tensor = tensorFromSentence(input_lang, pair[0])
    target_tensor = tensorFromSentence(output_lang, pair[1])
    return input_tensor, target_tensor


# 评估
def evaluateFra2Eng(encoder, decoder, sentence, max_length=MAX_LENGTH):
    with torch.no_grad():
        input_tensor = tensorFromSentence(input_lang, sentence)
        input_length = input_tensor.size()[0]
        encoder_hidden = encoder.initHidden()

        encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)

        for ei in range(input_length):
            encoder_output, encoder_hidden = encoder(input_tensor[ei],
                                                     encoder_hidden)
            encoder_outputs[ei] += encoder_output[0, 0]

        decoder_input = torch.tensor([[SOS_token]], device=device)  # SOS

        decoder_hidden = encoder_hidden

        decoded_words = []
        decoder_attentions = torch.zeros(max_length, max_length)

        for di in range(max_length):
            decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
            decoder_attentions[di] = decoder_attention.data
            topv, topi = decoder_output.data.topk(1)
            if topi.item() == EOS_token:
                decoded_words.append('<EOS>')
                break
            else:
                decoded_words.append(output_lang.index2word[topi.item()])

            decoder_input = topi.squeeze().detach()

        return decoded_words, decoder_attentions[:di + 1]

def evaluateEng2Fra(encoder, decoder, sentence, max_length=MAX_LENGTH):
    with torch.no_grad():
        input_tensor = tensorFromSentence(output_lang, sentence)
        input_length = input_tensor.size()[0]
        encoder_hidden = encoder.initHidden()

        encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)

        for ei in range(input_length):
            encoder_output, encoder_hidden = encoder(input_tensor[ei],encoder_hidden)
            encoder_outputs[ei] += encoder_output[0, 0]

        decoder_input = torch.tensor([[SOS_token]], device=device)  # SOS

        decoder_hidden = encoder_hidden

        decoded_words = []
        decoder_attentions = torch.zeros(max_length, max_length)

        for di in range(max_length):
            decoder_output, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
            decoder_attentions[di] = decoder_attention.data
            topv, topi = decoder_output.data.topk(1)
            if topi.item() == EOS_token:
                decoded_words.append('<EOS>')
                break
            else:
                decoded_words.append(input_lang.index2word[topi.item()])

            decoder_input = topi.squeeze().detach()

        return decoded_words, decoder_attentions[:di + 1]

# 新评估
def evaluate2(encoder, decoder, sentence, max_length=MAX_LENGTH, beamsize=5):
    print('evaluate2')
    with torch.no_grad():
        input_tensor = tensorFromSentence(input_lang, sentence)
        input_length = input_tensor.size()[0]
        encoder_hidden = encoder.initHidden()

        encoder_outputs = torch.zeros(max_length, encoder.hidden_size, device=device)
        for ei in range(input_length):
            encoder_output, encoder_hidden = encoder(input_tensor[ei],
                                                     encoder_hidden)
            encoder_outputs[ei] += encoder_output[0, 0]

        decoder_input = torch.tensor([[SOS_token]], device=device)  # SOS

        decoder_hidden = encoder_hidden

        decoded_words = []
        decoder_attentions = torch.zeros(max_length, max_length)

        pq = PriorityQueue()
        pq.put(Node(1, decoder_input, decoder_hidden, []))
        for di in range(max_length):
            pq2 = PriorityQueue()

            while pq.qsize() != 0:
                curr = pq.get_nowait()
                if len(curr.seq) != 0 and curr.seq[-1] == '<EOS>':
                    pq2.put(curr)
                    continue
                input = curr.input
                hidden = curr.hidden
                gailv = curr.gailv
                seq = curr.seq
                decoder_output, curr_hidden, decoder_attention = decoder(
                    input, hidden, encoder_outputs)
                topv, topi = torch.topk(decoder_output.view(-1).data, k=beamsize)
                for v, i in zip(topv, topi):
                    info = ''
                    if i.item() == EOS_token:
                        info = ('<EOS>')
                    else:
                        info = (output_lang.index2word[i.item()])
                    mylist = [t for t in seq]
                    mylist.append(info)
                    pq2.put(Node(gailv * v.item(), i.squeeze().detach(), curr_hidden, mylist))
            for i in range(beamsize):
                pq.put(pq2.get_nowait())
        ans = pq.get_nowait()
        return ans.seq


# while True:
#     fraSentence = input('FRA-> ')
#     fraSentence = normalizeString(fraSentence)
#     try:
#         output, attn = evaluate(encoder1, attn_decoder1, fraSentence)
#         output[len(output)-1] = ''
#         engSentence = ''
#         for word in output:
#             engSentence += (word + ' ')
#         print('ENG -> ', engSentence,'\n')
#     except:
#         print('unknown word')


DEBUG = True
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})


def loadModels():
    # load
    hidden_size = 256

    # fra => eng
    encoder1 = EncoderRNN(input_lang.n_words, hidden_size).to(device)
    attn_decoder1 = AttnDecoderRNN(hidden_size, output_lang.n_words, dropout_p=0.1).to(device)
    map_location = torch.device('cpu')
    encoder_param = torch.load('./models/oldModels/encoder.m', map_location=map_location)
    attn_decoder_param = torch.load('./models/oldModels/attnDecoder.m', map_location=map_location)
    encoder1.load_state_dict(encoder_param)
    attn_decoder1.load_state_dict(attn_decoder_param)

    # eng => fra
    encoder2 = EncoderRNN(output_lang.n_words, hidden_size).to(device)
    attn_decoder2 = AttnDecoderRNN(hidden_size, input_lang.n_words, dropout_p=0.1).to(device)
    encoder_param2 = torch.load('./models/eng2fra/encoder_ENG.m', map_location=map_location)
    attn_decoder_param2 = torch.load('./models/eng2fra/attnDecoder_ENG.m', map_location=map_location)
    encoder2.load_state_dict(encoder_param2)
    attn_decoder2.load_state_dict(attn_decoder_param2)

    return encoder1, attn_decoder1,encoder2,attn_decoder2


@app.route('/translate/<text>/<lang>', methods=['GET'])
def translate(text,lang):
    sentence = normalizeString(text)
    print(sentence,lang)

    error = False
    error_message = ''
    eng_sentence = ''
    if lang == 'fra':
        encoder = encoder1
        attn_decoder = attn_decoder1
        try:
            output, attn = evaluateFra2Eng(encoder, attn_decoder, sentence)
            # output = evaluate2(encoder, attn_decoder, sentence)
            output[len(output) - 1] = ''
            for word in output:
                eng_sentence += (word + ' ')
        except:
            error = True
            error_message = 'unknown words'
    else:
        encoder = encoder2
        attn_decoder = attn_decoder2
        try:
            output, attn = evaluateEng2Fra(encoder, attn_decoder, sentence)
            # output = evaluate2(encoder, attn_decoder, sentence)
            output[len(output) - 1] = ''
            for word in output:
                eng_sentence += (word + ' ')
        except:
            error = True
            error_message = 'unknown words'

    return jsonify([eng_sentence, error, error_message])


if __name__ == '__main__':
    encoder1, attn_decoder1,encoder2, attn_decoder2 = loadModels()
    app.run()
