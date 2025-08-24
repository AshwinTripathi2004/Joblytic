from apify_client import ApifyClient
import os
from dotenv import load_dotenv

load_dotenv()

# Support both env names: APIFY_API_TOKEN (common) or APIFY_API_KEY (user-provided)
apify_token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
if not apify_token:
    raise RuntimeError(
        "Apify API token not set. Add APIFY_API_TOKEN=<your_token> (or APIFY_API_KEY=<your_token>) to .env or environment."
    )

apify_client = ApifyClient(apify_token)

# Fetch LinkedIn jobs based on search query and location
def fetch_linkedin_jobs(search_query, location = "india", rows=60):
    run_input = {
            "title": search_query,
            "location": location,
            "rows": rows,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"],
            }
        }
    run = apify_client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs


# Fetch Naukri jobs based on search query and location
def fetch_naukri_jobs(search_query, location = "india", rows=60):
    run_input = {
        "keyword": search_query,
        "maxJobs": 60,
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
    }
    run = apify_client.actor("alpcnRV9YI9lYVPWk").call(run_input=run_input)
    jobs = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
    return jobs