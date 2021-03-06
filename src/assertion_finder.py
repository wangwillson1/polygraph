import json

from src.definitions import ROOT_PATH, SETTINGS
import requests
from allennlp.data.tokenizers.sentence_splitter import SpacySentenceSplitter


class AssertionFinder:
    def __init__(self):
        self.base_url = "https://idir.uta.edu/claimbuster/api/v2/score/text/"

        self.headers = {
            'x-api-key': SETTINGS["assertion_finder"]["api_key"],
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "idir.uta.edu",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

    def assertion_likelihood(self, sentence: str) -> float:
        response = requests.request("GET", self.base_url + sentence.replace(" ", "%20"), headers=self.headers)
        res = json.loads(response.text)["results"][0]
        if res["result"] != "Check-worthy factual statement":
            return 0
        return res["score"]

    def parse_captions(self, captions: dict) -> dict:
        # full_text = " ".join(captions.values())
        # splitter = SpacySentenceSplitter()
        # sentences = splitter.split_sentences(full_text)
        # tmstmp_sentences = {k: {"claim": v} for k, v in zip(captions.keys(), sentences)}
        # for sentence in tmstmp_sentences.values():
        #     sentence["claim_score"] = self.assertion_likelihood(sentence["claim"])
        #
        # print(tmstmp_sentences)
        assertions = dict()
        c = sorted(list(captions.items()), key=lambda x: float(x[0]))
        for i in range(0, len(c), 3):
            if i + 2 >= len(c):
                break
            a = c[i][1] + " " + c[i + 1][1] + " " + c[i + 2][1]
            assertions[c[i][0]] = {"claim": a}
        for sentence in assertions.values():
            sentence["claim_score"] = self.assertion_likelihood(sentence["claim"])
        return assertions
        # return tmstmp_sentences
