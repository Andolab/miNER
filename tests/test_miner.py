import unittest

from miner import Miner


class TestMiner(unittest.TestCase):
    def setUp(self):
        # 花子さんは東京に行きました(IOB2)
        # 山田太郎くんは東京駅に向かいました(IOB2)
        # 花子さんとボブくんは東京スカイツリーに行きました(BIOES)
        self.answers = [
            "B-PSN O O B-LOC O O O O".split(" "),
            "B-PSN I-PSN O O B-LOC I-LOC O O O O".split(" "),
            "S-PSN O O S-PSN O O B-LOC I-LOC E-LOC O O O O".split(" "),
        ]
        self.predicts = [
            "B-PSN O O B-LOC O B-LOC O O".split(" "),
            "B-PSN B-PSN O O B-LOC I-LOC O O O O".split(" "),
            "O O O O O O B-LOC I-LOC E-LOC O B-PSN O O".split(" "),
        ]
        self.sentences = [
            "花子 さん は 東京 に 行き まし た".split(" "),
            "山田 太郎 君 は 東京 駅 に 向かい まし た".split(" "),
            "花子 さん と ボブ くん は 東京 スカイ ツリー に 行き まし た".split(" "),
        ]

        self.knowns = {"PSN": ["花子"], "LOC": ["東京"]}

        self.miner = Miner(self.answers, self.predicts, self.sentences, self.knowns)

    def test_initialize(self):

        self.assertEqual(self.miner.answers, self.answers)
        self.assertEqual(self.miner.predicts, self.predicts)
        self.assertEqual(self.miner.sentences, self.sentences)
        self.assertEqual(self.miner.known_words, self.knowns)
        # check no setting known words
        m = Miner(self.answers, self.predicts, self.sentences)
        self.assertEqual(m.known_words, {"PSN": [], "LOC": [], "overall": []})

    def test_default_report(self):

        result = self.miner.default_report(False)
        self.assertTrue(
            all([k in ["PSN", "LOC", "overall"] for k, v in result.items()])
        )
        self.assertEqual(
            [k for k, v in result["PSN"].items()],
            ["precision", "recall", "f1_score", "num"],
        )
        self.assertEqual(
            {
                "LOC": {
                    "f1_score": 0.8571428571428571,
                    "num": 3,
                    "precision": 0.75,
                    "recall": 1.0,
                },
                "PSN": {"f1_score": 0.25, "num": 4, "precision": 0.25, "recall": 0.25},
                "overall": {
                    "f1_score": 0.5333333333333333,
                    "num": 7,
                    "precision": 0.5,
                    "recall": 0.5714285714285714,
                },
            },
            result,
        )

    def test_known_only_report(self):

        result = self.miner.known_only_report(False)
        self.assertTrue(
            all([k in ["PSN", "LOC", "overall"] for k, v in result.items()])
        )
        self.assertEqual(
            [k for k, v in result["PSN"].items()],
            ["precision", "recall", "f1_score", "num"],
        )

        self.assertEqual(
            {
                "LOC": {"f1_score": 1.0, "num": 1, "precision": 1.0, "recall": 1.0},
                "PSN": {
                    "f1_score": 0.6666666666666666,
                    "num": 2,
                    "precision": 1.0,
                    "recall": 0.5,
                },
                "overall": {
                    "f1_score": 0.8,
                    "num": 3,
                    "precision": 1.0,
                    "recall": 0.6666666666666666,
                },
            },
            result,
        )

    def test_unknown_only_report(self):

        result = self.miner.unknown_only_report(False)
        self.assertTrue(
            all([k in ["PSN", "LOC", "overall"] for k, v in result.items()])
        )
        self.assertEqual(
            [k for k, v in result["PSN"].items()],
            ["precision", "recall", "f1_score", "num"],
        )
        self.assertEqual(
            {
                "LOC": {"f1_score": 0.8, "num": 2, "precision": 2 / 3, "recall": 1.0},
                "PSN": {"f1_score": 0, "num": 2, "precision": 0.0, "recall": 0.0},
                "overall": {
                    "f1_score": 0.4,
                    "num": 4,
                    "precision": 0.3333333333333333,
                    "recall": 0.5,
                },
            },
            result,
        )

    def test__entity_indexes(self):

        result = self.miner._entity_indexes(self.answers, "PSN")
        expect = [("PSN", 0, 0), ("PSN", 9, 10), ("PSN", 20, 20), ("PSN", 23, 23)]
        self.assertEqual(result, expect)
        result = self.miner._entity_indexes(self.answers, "LOC")
        expect = [("LOC", 3, 3), ("LOC", 13, 14), ("LOC", 26, 28)]
        self.assertEqual(result, expect)

    def test__return_named_entities(self):

        result = self.miner._return_named_entities(self.answers)
        expect = {
            "known": {"PSN": ["花子"], "LOC": ["東京"]},
            "unknown": {"PSN": ["山田太郎", "ボブ"], "LOC": ["東京スカイツリー", "東京駅"]},
        }
        for (rk, rv), (ek, ev) in zip(result.items(), expect.items()):
            self.assertTrue(set(rv["PSN"]) & set(ev["PSN"]))
            self.assertTrue(set(rv["LOC"]) & set(ev["LOC"]))

    def test_return_miss_labelings(self):

        result = self.miner.return_miss_labelings()
        expect = [
            {
                "answer": self.answers[0],
                "predict": self.predicts[0],
                "sentence": self.sentences[0],
            },
            {
                "answer": self.answers[1],
                "predict": self.predicts[1],
                "sentence": self.sentences[1],
            },
            {
                "answer": self.answers[2],
                "predict": self.predicts[2],
                "sentence": self.sentences[2],
            },
        ]
        self.assertEqual(result, expect)

    def test_return_answer_named_entities(self):

        result = self.miner.return_answer_named_entities()
        expect = self.miner._return_named_entities(self.answers)
        for (rk, rv), (ek, ev) in zip(result.items(), expect.items()):
            self.assertTrue(set(rv["PSN"]) & set(ev["PSN"]))
            self.assertTrue(set(rv["LOC"]) & set(ev["LOC"]))

    def test_return_predict_named_entities(self):

        result = self.miner.return_predict_named_entities()
        expect = self.miner._return_named_entities(self.predicts)
        for (rk, rv), (ek, ev) in zip(result.items(), expect.items()):
            self.assertTrue(set(rv["PSN"]) & set(ev["PSN"]))
            self.assertTrue(set(rv["LOC"]) & set(ev["LOC"]))

    def test_segmentation_score(self):

        result = self.miner.segmentation_score("default", False)
        self.assertEqual(
            result,
            {
                "f1_score": 0.5333333333333333,
                "num": 7,
                "precision": 0.5,
                "recall": 0.5714285714285714,
            },
        )
        result = self.miner.segmentation_score("unknown", False)
        self.assertEqual(
            result,
            {"f1_score": 0.4, "num": 4, "precision": 0.3333333333333333, "recall": 0.5},
        )
        result = self.miner.segmentation_score("known", False)
        self.assertEqual(
            result,
            {"f1_score": 0.8, "num": 3, "precision": 1.0, "recall": 0.6666666666666666},
        )

    def test__check_add_entity(self):

        # assert all
        self.miner.check_known = True
        self.miner.check_unknown = True
        self.assertTrue(self.miner._check_add_entity("", ""))
        self.assertTrue(self.miner._check_add_entity("花子", "PSN"))
        # assert known
        self.miner.check_known = True
        self.miner.check_unknown = False
        self.assertTrue(self.miner._check_add_entity("花子", "PSN"))
        self.assertTrue(self.miner._check_add_entity("東京", "LOC"))
        self.assertFalse(self.miner._check_add_entity("ボブ", "PSN"))
        # assert unknown
        self.miner.check_known = False
        self.miner.check_unknown = True
        self.assertTrue(self.miner._check_add_entity("ボブ", "PSN"))
        self.assertTrue(self.miner._check_add_entity("東京スカイツリー", "LOC"))
        self.assertFalse(self.miner._check_add_entity("東京", "LOC"))
