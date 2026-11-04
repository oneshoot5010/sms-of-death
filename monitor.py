import time
import os
import requests
import zipfile
import io

# إعدادات المستودع الخاص بك
REPO = "oneshoot5010/sms-of-death"
# إذا كان لديك GitHub Personal Access Token ضعه هنا لتفادي حدود الاستعلام (اختياري ولكن مُفضل)
TOKEN = "" 

HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

def get_latest_workflow_run():
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        runs = response.json().get("runs", [])
        if runs:
            return runs[0]
    return None

def get_job_logs(job_id):
    url = f"https://api.github.com/repos/{REPO}/actions/jobs/{job_id}/logs"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    return "Could not fetch logs."

def get_artifact_url(run_id):
    url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/artifacts"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        artifacts = response.json().get("artifacts", [])
        if artifacts:
            return artifacts[0]["archive_download_url"]
    return None

def main():
    print(f"[*] Starting GitHub Build Monitor for {REPO}...")
    print("[*] Waiting for active workflow run...")
    
    last_run_id = None
    
    while True:
        run = get_latest_workflow_run()
        if not run:
            time.sleep(10)
            continue
            
        run_id = run["id"]
        status = run["status"]      # queued, in_progress, completed
        conclusion = run["conclusion"] # success, failure, cancelled, etc.
        
        if run_id != last_run_id:
            print(f"\n[+] Detected Run ID: {run_id} | Status: {status}")
            last_run_id = run_id

        if status == "completed":
            if conclusion == "success":
                print("\n[+] Build Success! Downloading APK...")
                artifact_url = get_artifact_url(run_id)
                if artifact_url:
                    res = requests.get(artifact_url, headers=HEADERS)
                    if res.status_code == 200:
                        # فك الضغط وحفظ ملف الـ APK في التنزيلات
                        z = zipfile.ZipFile(io.BytesIO(res.content))
                        download_path = "/data/data/com.termux/files/home/storage/downloads"
                        if not os.path.exists(download_path):
                            os.makedirs(download_path, exist_ok=True)
                        z.extractall(download_path)
                        print(f"[✔] APK downloaded successfully to your Downloads folder! ({download_path})")
                    else:
                        print("[-] Failed to download artifact archive.")
                else:
                    print("[-] No artifacts found for this run.")
                break
                
            elif conclusion == "failure":
                print("\n[❌] Build Failed! Fetching error logs...\n")
                # جلب الـ Jobs الخاصة بهذا الـ Run لمعرفة الـ ID الخاص بالفشل
                jobs_url = f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}/jobs"
                jobs_res = requests.get(jobs_url, headers=HEADERS)
                if jobs_res.status_code == 200:
                    jobs = jobs_res.json().get("jobs", [])
                    for job in jobs:
                        if job["conclusion"] == "failure":
                            logs = get_job_logs(job["id"])
                            # طباعة آخر أسطر الخطأ لتوضيح سبب السقوط
                            lines = logs.splitlines()
                            print("\n".join(lines[-30:])) # طباعة آخر 30 سطر من الخطأ
                break
        
        time.sleep(15) # التحقق كل 15 ثانية

if __name__ == "__main__":
    main()
