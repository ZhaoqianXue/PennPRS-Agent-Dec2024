import requests
import pandas as pd
import os
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
BASE_URL = "https://rest.omicspred.org/api/score/all/"
OUTPUT_FILE = "data/omicspred/omicspred_scores_full.tsv"
PROGRESS_FILE = "data/omicspred/download_progress.json"
BATCH_SIZE = 100
MAX_WORKERS = 5  # Increased for speed
TEST_MODE = False  # SET TO FALSE FOR FULL DOWNLOAD

# Rate limiting protection
RATE_LIMIT_DELAY = 0.5  # Reduced delay

# Thread-safe writing lock
file_lock = threading.Lock()

def get_total_rows():
    """Dynamically get the total count of scores from the API."""
    try:
        response = requests.get(f"{BASE_URL}?limit=1", timeout=30)
        if response.status_code == 200:
            count = response.json().get('count', 0)
            if count > 0:
                return count
    except Exception as e:
        print(f"[!] Error detecting total rows: {e}")
    return 304391  # Fallback

def fetch_datasets():
    """Fetch all dataset metadata once to map URLs and Study Design info."""
    try:
        # OmicsPred has ~56 datasets as per inventory
        url = "https://rest.omicspred.org/api/dataset/all"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            results = response.json().get('results', [])
            ds_map = {}
            for d in results:
                ds_id = d['id']
                
                # Extract Study Design Summaries
                def summarize_samples(samples):
                    if not samples: return 0, "", ""
                    total_n = sum([s.get('sample_number') or 0 for s in samples])
                    cohorts = []
                    ancestries = []
                    for s in samples:
                        c_list = [c.get('name_short') for c in s.get('cohorts', []) if c.get('name_short')]
                        cohorts.extend(c_list)
                        if s.get('ancestry_broad'): ancestries.append(s.get('ancestry_broad'))
                    return total_n, "|".join(sorted(list(set(cohorts)))), "|".join(sorted(list(set(ancestries))))

                train_n, train_c, train_a = summarize_samples(d.get('samples_training', []))
                valid_n, valid_c, valid_a = summarize_samples(d.get('samples_validation', []))

                ds_map[ds_id] = {
                    "urls": d.get('scoring_files_urls', {}),
                    "study_info": {
                        "train_n": train_n,
                        "train_cohorts": train_c,
                        "train_ancestries": train_a,
                        "valid_n": valid_n,
                        "valid_cohorts": valid_c,
                        "valid_ancestries": valid_a,
                        "omics_type": d.get("omics_type"),
                        "omics_count": d.get("omics_count")
                    }
                }
            return ds_map
    except Exception as e:
        print(f"[!] Critical: Could not fetch dataset metadata: {e}")
    return {}

def fetch_batch_strictly(offset, batch_size):
    """Fetch a batch of data, retrying with exponential backoff."""
    url = f"{BASE_URL}?limit={batch_size}&offset={offset}"

    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    headers = {
        'Accept': 'application/json',
        'User-Agent': user_agents[offset % len(user_agents)],
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    print(f"\n[*] Fetching offset {offset}...")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30, headers=headers)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if not results and offset < 300000: # Sanity check for empty results in middle
                     print(f"\n[!] Warning: Empty results for offset {offset}. Retrying...")
                     time.sleep(2)
                     continue
                return offset, results
            elif response.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"\n[!] Rate limited (429) for offset {offset}, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"\n[!] HTTP {response.status_code} for offset {offset}, retrying...")
                time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"\n[!] error for offset {offset}: {e}, retrying...")
            time.sleep(5 * (attempt + 1))
    
    return offset, []

def flatten_item(item, datasets_map):
    """Deeply flatten the JSON item into a flat dictionary containing ALL available API fields."""
    flat = {}
    
    # 1. Base Fields & Web URL
    sid = item.get("id")
    flat["id"] = sid
    flat["score_web_url"] = f"https://www.omicspred.org/scores/{sid}"
    flat["name"] = item.get("name")
    flat["trait_reported"] = item.get("trait_reported")
    flat["trait_reported_id"] = item.get("trait_reported_id")
    flat["method_name"] = item.get("method_name")
    flat["method_params"] = item.get("method_params")
    flat["dataset_id"] = item.get("dataset_id")
    flat["dataset_name"] = item.get("dataset_name")
    flat["variants_number"] = item.get("variants_number")
    flat["variants_interactions"] = item.get("variants_interactions")
    flat["variants_genomebuild"] = item.get("variants_genomebuild")
    flat["comment"] = item.get("comment")
    flat["license"] = item.get("license")

    # 2. Publication
    pub = item.get("publication") or {}
    flat["pub_id"] = pub.get("id")
    flat["pub_title"] = pub.get("title")
    flat["pub_doi"] = pub.get("doi")
    flat["pub_pmid"] = pub.get("pmid")
    flat["pub_journal"] = pub.get("journal")
    flat["pub_firstauthor"] = pub.get("firstauthor")
    flat["pub_date"] = pub.get("date_publication")

    # 3. Platform
    plat = item.get("platform") or {}
    flat["platform_name"] = plat.get("name")
    flat["platform_full_name"] = plat.get("full_name")
    flat["platform_version"] = plat.get("version")
    flat["platform_technic"] = plat.get("technic")
    flat["platform_type"] = plat.get("type")

    # 4. Tissue
    tis = item.get("tissue") or {}
    flat["tissue_id"] = tis.get("id")
    flat["tissue_label"] = tis.get("label")
    flat["tissue_description"] = tis.get("description")
    flat["tissue_type"] = tis.get("type")
    flat["tissue_url"] = tis.get("url")

    # 5. Genes
    genes = item.get("genes") or []
    flat["genes_names"] = "|".join([str(x.get("name") or "") for x in genes])
    flat["genes_external_ids"] = "|".join([str(x.get("external_id") or "") for x in genes])
    flat["genes_biotypes"] = "|".join([str(x.get("biotype") or "") for x in genes])
    flat["genes_synonyms"] = "|".join([",".join(x.get("synonyms") or []) for x in genes])
    flat["genes_descriptions"] = "|".join(["; ".join(x.get("descriptions") or []) for x in genes])

    # 6. Proteins
    prots = item.get("proteins") or []
    flat["proteins_names"] = "|".join([str(x.get("name") or "") for x in prots])
    flat["proteins_external_ids"] = "|".join([str(x.get("external_id") or "") for x in prots])
    flat["proteins_synonyms"] = "|".join([",".join(x.get("synonyms") or []) for x in prots])
    flat["proteins_descriptions"] = "|".join(["; ".join(x.get("descriptions") or []) for x in prots])

    # 7. Dataset URLs & Study Design (The missing pieces)
    ds_data = datasets_map.get(flat["dataset_id"], {})
    ds_urls = ds_data.get("urls", {})
    ds_study = ds_data.get("study_info", {})

    flat["url_gwas_sumstats"] = ds_urls.get("gwas_sumstats")
    flat["url_scoring_files"] = ds_urls.get("scoring_files")
    flat["url_validation_results"] = ds_urls.get("validation_results")

    flat["study_train_n"] = ds_study.get("train_n")
    flat["study_train_cohorts"] = ds_study.get("train_cohorts")
    flat["study_train_ancestries"] = ds_study.get("train_ancestries")
    flat["study_valid_n"] = ds_study.get("valid_n")
    flat["study_valid_cohorts"] = ds_study.get("valid_cohorts")
    flat["study_valid_ancestries"] = ds_study.get("valid_ancestries")
    flat["study_omics_type"] = ds_study.get("omics_type")

    return flat

def save_data(offset, results, finished_offsets, datasets_map):
    if not results:
        return

    flat_rows = [flatten_item(item, datasets_map) for item in results]
    df = pd.DataFrame(flat_rows)
    
    # Define exact output order for final CSV
    cols = ["id", "score_web_url", "name", "trait_reported", "trait_reported_id", 
            "method_name", "method_params", "variants_number", "variants_genomebuild",
            "dataset_id", "study_train_n", "study_train_cohorts", "study_train_ancestries",
            "study_valid_n", "study_valid_cohorts", "study_valid_ancestries", "study_omics_type",
            "platform_name", "platform_full_name", "platform_technic", "tissue_label", 
            "genes_names", "genes_external_ids", "proteins_names", "proteins_external_ids",
            "pub_title", "pub_journal", "pub_doi", "pub_pmid", "pub_date",
            "url_gwas_sumstats", "url_scoring_files", "url_validation_results", "license"]
    
    # Check if cols exist in df (some might be missing in a specific batch if empty)
    missing = [c for c in cols if c not in df.columns]
    for c in missing: df[c] = ""
    df = df[cols]
    
    with file_lock:
        header = not os.path.exists(OUTPUT_FILE)
        df.to_csv(OUTPUT_FILE, sep='\t', index=False, mode='a', header=header)

        if offset is not None:
            finished_offsets.add(offset)
            temp_progress = list(finished_offsets)
            with open(PROGRESS_FILE + ".tmp", 'w') as f:
                json.dump(temp_progress, f)
            os.replace(PROGRESS_FILE + ".tmp", PROGRESS_FILE)

    # Small delay between writes if needed, but per-worker delay is better
    time.sleep(RATE_LIMIT_DELAY) 

def main():
    print("[DEBUG] Script started...")

    # 0. Dynamic Row Detection
    total_rows = get_total_rows()
    print(f"[*] Detected total rows: {total_rows}")

    # 1. Skip dataset mapping for now to avoid blocking (can be added back later)
    # print("[*] Fetching dataset metadata...")
    datasets_map = {} # fetch_datasets() 

    if TEST_MODE:
        print("[!] TEST MODE: Fetching first 10 rows ONLY.")
        if os.path.exists(OUTPUT_FILE):
             os.remove(OUTPUT_FILE)
        _, results = fetch_batch_strictly(0, 10)
        save_data(None, results, set(), datasets_map)
        print(f"[+] Test successful. Result saved to {OUTPUT_FILE}")
        return

    # 2. Load progress
    finished_offsets = set()
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                finished_offsets = set(json.load(f))
                print(f"[*] Found existing progress: {len(finished_offsets)} batches.")
        except Exception:
            finished_offsets = set()
    
    # 3. Prepare task list
    all_offsets = list(range(0, total_rows, BATCH_SIZE))
    todo_offsets = [o for o in all_offsets if o not in finished_offsets]
    
    if not todo_offsets:
        print("[+] All data downloaded.")
        return

    print(f"[*] Total Target Rows: {total_rows}")
    print(f"[*] Remaining Batches: {len(todo_offsets)} (Batch Size: {BATCH_SIZE})")
    print(f"[*] Parallel Workers: {MAX_WORKERS}")
    print("-" * 50)

    # 4. Run multi-threaded download
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_offset = {executor.submit(fetch_batch_strictly, o, BATCH_SIZE): o for o in todo_offsets}
        try:
            for future in as_completed(future_to_offset):
                offset, results = future.result()
                save_data(offset, results, finished_offsets, datasets_map)
                
                # Progress Reporting
                done = len(finished_offsets)
                total_batches = len(all_offsets)
                percent = (done / total_batches) * 100
                elapsed = time.time() - start_time
                avg_time_per_batch = elapsed / (done - (len(all_offsets) - len(todo_offsets)) + 1e-9)
                eta_min = (avg_time_per_batch * (total_batches - done)) / 60 if done > 0 else 0
                
                if done % 5 == 0: # Print every 5 batches to avoid flooding but show movement
                    print(f"\n[+] PROGRESS: {percent:6.2f}% | Done: {done}/{total_batches} | Last Offset: {offset} | ETA: {eta_min:4.1f} min")
                else:
                    print(f"\r[+] PROGRESS: {percent:6.2f}% | Done: {done}/{total_batches} | ETA: {eta_min:4.1f} min", end="")
        except KeyboardInterrupt:
            print("\n[!] Suspended. Progress saved.")
            return

    total_time = (time.time() - start_time) / 60
    print(f"\n[+] Global Download Complete in {total_time:.1f} minutes. File: {OUTPUT_FILE}")

    # Optional: Deduplicate final file
    print("[*] Deduplicating final file...")
    try:
        df_final = pd.read_csv(OUTPUT_FILE, sep='\t')
        df_final = df_final.drop_duplicates(subset=['id'], keep='first')
        df_final.to_csv(OUTPUT_FILE, sep='\t', index=False)
        print(f"[+] Final deduplicated file saved. Total rows: {len(df_final)}")
    except Exception as e:
        print(f"[!] Could not deduplicate: {e}")


if __name__ == "__main__":
    main()
