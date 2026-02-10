#!/usr/bin/env python3
"""
Test script for async optimization of PRS model fetching.
Tests the performance improvement with "breast cancer" query.
"""

import requests
import time
import json
import sys
from typing import Dict, Any

API_BASE = "http://localhost:8000"
TEST_TRAIT = "breast cancer"


def test_recommendation_api():
    """Test the /agent/recommend endpoint with progress tracking."""
    print("=" * 80)
    print(f"Testing PRS Model Fetching Optimization")
    print(f"Trait: {TEST_TRAIT}")
    print("=" * 80)
    
    # Generate request ID for progress tracking
    import uuid
    request_id = str(uuid.uuid4())
    
    print(f"\n[1] Starting recommendation request...")
    print(f"    Request ID: {request_id}")
    
    # Start the recommendation request in background
    start_time = time.time()
    
    try:
        # Make the POST request
        response = requests.post(
            f"{API_BASE}/agent/recommend",
            json={"trait": TEST_TRAIT, "request_id": request_id},
            timeout=300  # 5 minute timeout (increased due to retry mechanism)
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[2] Request completed successfully!")
            print(f"    Total time: {total_time:.2f} seconds")
            print(f"    Recommendation type: {result.get('recommendation_type', 'N/A')}")
            
            # Check direct match evidence
            direct_evidence = result.get('direct_match_evidence', {})
            models_evaluated = direct_evidence.get('models_evaluated', 0)
            print(f"    Models evaluated: {models_evaluated}")
            
            return {
                "success": True,
                "total_time": total_time,
                "models_evaluated": models_evaluated,
                "recommendation_type": result.get('recommendation_type')
            }
        else:
            print(f"\n[ERROR] Request failed with status {response.status_code}")
            print(f"    Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request timed out after 120 seconds")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        print(f"\n[ERROR] Exception occurred: {e}")
        return {"success": False, "error": str(e)}


def monitor_progress(request_id: str, duration: int = 120):
    """Monitor progress updates during the request."""
    print(f"\n[Progress Monitor] Tracking progress for request {request_id[:8]}...")
    
    progress_updates = []
    start_time = time.time()
    last_fetched = 0
    
    while time.time() - start_time < duration:
        try:
            response = requests.get(
                f"{API_BASE}/agent/search_progress/{request_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                progress = response.json()
                
                if progress.get("status") == "unknown":
                    # Not initialized yet
                    time.sleep(0.5)
                    continue
                
                current_time = time.time() - start_time
                fetched = progress.get("fetched", 0)
                total = progress.get("total", 0)
                current_action = progress.get("current_action", "")
                status = progress.get("status", "")
                
                # Only log when fetched count changes
                if fetched != last_fetched:
                    progress_updates.append({
                        "time": current_time,
                        "fetched": fetched,
                        "total": total,
                        "action": current_action,
                        "status": status
                    })
                    
                    if total > 0:
                        percentage = (fetched / total) * 100
                        print(f"    [{current_time:6.2f}s] {fetched}/{total} ({percentage:5.1f}%) - {current_action}")
                    else:
                        print(f"    [{current_time:6.2f}s] {current_action}")
                    
                    last_fetched = fetched
                
                if status == "completed":
                    print(f"\n[Progress Monitor] Completed!")
                    break
                    
            time.sleep(0.3)  # Poll every 300ms
            
        except Exception as e:
            print(f"    [Error polling progress] {e}")
            time.sleep(1)
    
    return progress_updates


def main():
    """Main test function."""
    print("\n" + "=" * 80)
    print("PRS Model Fetching Optimization Test")
    print("=" * 80)
    
    # Check if server is running
    try:
        health_check = requests.get(f"{API_BASE}/", timeout=10)
        if health_check.status_code != 200:
            print(f"\n[ERROR] Server is not responding correctly at {API_BASE}")
            print("        Please make sure the server is running.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to server at {API_BASE}")
        print("        Please start the server first:")
        print("        cd src/server && python main.py")
        sys.exit(1)
    
    print(f"\n[✓] Server is running at {API_BASE}")
    
    # Run the test
    import uuid
    request_id = str(uuid.uuid4())
    
    # Start progress monitoring in a separate thread
    import threading
    progress_thread = threading.Thread(
        target=monitor_progress,
        args=(request_id, 120),
        daemon=True
    )
    progress_thread.start()
    
    # Run the actual test
    result = test_recommendation_api()
    
    # Wait a bit for progress thread to finish
    progress_thread.join(timeout=5)
    
    # Print summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    if result.get("success"):
        print(f"✓ Test completed successfully")
        print(f"  Total time: {result.get('total_time', 0):.2f} seconds")
        print(f"  Models evaluated: {result.get('models_evaluated', 0)}")
        print(f"  Recommendation type: {result.get('recommendation_type', 'N/A')}")
        
        # Performance assessment
        total_time = result.get('total_time', 0)
        if total_time < 5:
            print(f"\n🚀 Excellent performance! (< 5 seconds)")
        elif total_time < 10:
            print(f"\n✅ Good performance! (< 10 seconds)")
        elif total_time < 15:
            print(f"\n⚠️  Acceptable performance (< 15 seconds)")
        else:
            print(f"\n❌ Performance needs improvement (> 15 seconds)")
    else:
        print(f"✗ Test failed: {result.get('error', 'Unknown error')}")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
