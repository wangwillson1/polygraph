# from src.definitions import ROOT_PATH
from src.assertion_finder import AssertionFinder
from src.textual_entailment import TextualEntailment
from src.wolfram import WolframAPI
import json

from flask import Flask, request, jsonify

class Polygraph:
    def __init__(self, top_n=10):
        self.top_n = top_n
        self.assertion_finder = AssertionFinder()
        self.wolfram_api = WolframAPI()
        self.hypothesis_tester = TextualEntailment()

    def run(self, captions: dict) -> dict:  # Both input and output must be dicts
        # captions = json.loads(captions)
        assertion_scores = self.assertion_finder.parse_captions(captions)
        print(assertion_scores)
        assertions = sorted(assertion_scores.items(), key=lambda x: x[1]["claim_score"], reverse=True)[:self.top_n]
        assertions = \
            {
                k: {
                    "score": v,
                    "claim": v["claim"],
                    "claim_score": v["claim_score"]
                } for (k, v) in assertions
            }

        for timestamp, assertion in assertions.items():
            assertion["wolfram_response"] = self.wolfram_api.query(assertion)
            assertion["is_factual"] = self.hypothesis_tester.run(assertion["wolfram_response"],
                                                                 assertion["claim"])

        invalid_assertions = {k: v for k, v in assertions if not assertions["is_factual"]}
        return invalid_assertions


# if __name__ == "__main__":
#     p = Polygraph()
#     with open(str(ROOT_PATH / "data/sample.json")) as file:
#         p.run(json.load(file))
#         file.close()


app = Flask(__name__)
p = Polygraph()

@app.route('/')
def hello_word():
    return 'Hello world'

@app.route('/analyze', methods=["POST"])
def get_polygraph():
    input_json = request.get_json(force=True)
    #result = p.run(input_json)
    # result = input_json
    return jsonify(result)
    