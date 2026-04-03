#!/usr/bin/env python3
import sys
import pandas as pd
import glob
from sklearn.metrics import roc_auc_score

def main(prs_dir, trait_file, output_file):
    trait_df = pd.read_csv(trait_file)

    covars = ["person_id", "age_2025", "sex_at_birth"] + [f"PC{i}" for i in range(1, 11)]
    all_trait = [col for col in trait_df.columns if col not in covars]

    prs_files = glob.glob(f"{prs_dir}/*.sscore")

    results = []
    for f in prs_files:
        prs_name = f.split("/")[-1].replace(".sscore", "")
        print(f"Processing {prs_name}")

        # read prs score
        prs_df = pd.read_csv(f, delim_whitespace=True, usecols=["IID", "SCORE1_SUM"])
        prs_df = prs_df.rename(columns={"IID": "person_id"})
        df = trait_df.merge(prs_df, on="person_id", how="left")

        # calculate roc for each trait
        for trait in all_trait:
            y_true = df[trait]
            y_score = df["SCORE1_SUM"]

            # handle missing data
            mask = y_true.notnull() & y_score.notnull()
            if mask.sum() == 0:
                auc_val = None
            else:
                try:
                    auc_val = roc_auc_score(y_true[mask], y_score[mask])
                except ValueError:
                    # 只有一个类别，AUC 无法计算
                    auc_val = None

            results.append({
                "prs": prs_name,
                "trait": trait,
                "auc": auc_val
            })

    # write outcome
    final_df = pd.DataFrame(results)
    final_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python auc_compute.py <prs_dir> <trait_file> <output_file>")
        sys.exit(1)

    prs_dir = sys.argv[1]
    trait_file = sys.argv[2]
    output_file = sys.argv[3]

    main(prs_dir, trait_file, output_file)
