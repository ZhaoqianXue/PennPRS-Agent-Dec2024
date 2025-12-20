
import requests
import io
import gzip
import zipfile
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def inspect_file():
    # Example ID found in previous steps
    file_id = "GCST90032275" 
    url = f"https://pennprs.org/api/download_result?filename={file_id}"
    
    print(f"Downloading stream from {url}...")
    try:
        # Download first 1MB to try and open zip central directory (might fail if at end, but usually works for small zips)
        # Actually, for zip we ideally need the whole file or seek support.
        # Let's download the whole thing into memory (assuming < 100MB, usually 5-50MB for GWAS)
        print("Downloading full file into memory for inspection...")
        resp = requests.get(url, verify=False, timeout=60)
        
        if resp.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(resp.content))
            print(f"\n--- Zip Contents ---")
            for n in z.namelist():
                print(f"- {n}")
                
            # Find the training info file
            info_file = next((n for n in z.namelist() if "PRS_model_training_info" in n), None)
            
            if info_file:
                print(f"\n--- Output of {info_file} ---")
                with z.open(info_file) as f:
                    print(f.read().decode('utf-8'))
            else:
                print("No training info file found.")
                
            # Also peek at one of the model files to see if it has a header
            model_file = next((n for n in z.namelist() if "lassosum2.PRS.txt" in n), None)
            if model_file:
                 print(f"\n--- Head of {model_file} ---")
                 with z.open(model_file) as f:
                    for _ in range(10):
                        print(f.readline().decode('utf-8').strip())
        else:
             print(f"Failed: {resp.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_file()
