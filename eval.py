import json
import time
from tqdm import tqdm

from src.addresschecker import AddressChecker

TEST_FILE_PATH = "data/test_6000.json"
FN_FILE_PATH = "fn.txt"
FP_FILE_PATH = "fp.txt"

sp = AddressChecker()

fn_writer = open(FN_FILE_PATH, "w")
fp_writer = open(FP_FILE_PATH, "w")

with open(TEST_FILE_PATH, "r") as reader:
    items = json.load(reader)
    
    tp = tn = fp = fn = 0
    total_combs = 0
    timer = 0
    for idx, item in tqdm(items.items()):
        gt = item["correct"].lower().split(" ")
        
        errs = [item["tran_0"], item["tran_1"], item["typo_0"], item["typo_1"], item["orth_0"], item["orth_1"]]
        
        for err in errs:
            query = err["query"]
            tokens = query.lower().split(" ")
            pos = err["pos"]
            
            combs = 1
            for i, word in enumerate(tokens):
                start = time.time()
                candidates = sp.corrections(word, k=5, method="naive")
                timer += (time.time() - start)
                candidates = set(x[0] for x in candidates)
                
                if i == pos: # This is the misspelling
                    if gt[i] in candidates:
                        tn += 1
                    else:
                        fn += 1
                        fn_writer.write("{} => {}\n".format(word, candidates))
                else:
                    if word in candidates:
                        tp += 1
                    else:
                        fp += 1
                        # if len(word) < 5:
                        fp_writer.write("{} => {}\n".format(word, candidates))
                
                num_candidates = len(candidates)
                if word in candidates:
                    num_candidates = 1                
                                
                combs *= num_candidates

            total_combs += (combs / len(tokens))

        
    print("TP: {}, FP: {}, TN: {}, FN: {}".format(tp, fp, tn, fn))
    print("Correct Word Acc: {:.2f}%".format(tp / (tp + fp) * 100))
    print("Misspellings Acc: {:.2f}%".format(tn / (tn + fn) * 100))

    print("Average solution of a word: {:2f}".format(total_combs / 6000))

    print("Average elapsed time for a word: {:2f} ms".format(1000 * timer / (tp + fp + tn + fn)))

fn_writer.close()
fp_writer.close()




