# dlt Pipelines - Zero Secrets Setup

This repository contains production-ready data pipelines using dlt hub that work with **default BigQuery settings** and require **no secrets configuration**.

## 🎯 **Zero Secrets Required!**

Both pipelines are configured to work with:
- ✅ **Default Cloud Run service account** for BigQuery authentication
- ✅ **Automatic project ID detection** from Cloud Build environment
- ✅ **Automatic authentication** via Google Cloud metadata service
- ✅ **Default BigQuery settings** for optimal performance
- ✅ **No secrets needed**: Uses Cloud Build's default service account

## 🚀 **Quick Start**

### 1. Prerequisites
- Google Cloud Project with APIs enabled:
  ```bash
  gcloud services enable run.googleapis.com
  gcloud services enable cloudbuild.googleapis.com
  gcloud services enable containerregistry.googleapis.com
  gcloud services enable bigquery.googleapis.com
  ```

### 2. Create BigQuery Datasets
```bash
bq mk --dataset --location=US pokemon_data
bq mk --dataset --location=US chess_data
```

### 3. Cloud Build Trigger Setup
- Push code to GitHub
- Set up Cloud Build trigger connected to your GitHub repository
- Trigger configured to build on push to `main` branch
- That's it! Project ID is automatically detected from Cloud Build environment.

### 4. Deploy
- Push to `main` branch
- Cloud Build trigger automatically builds and deploys both pipelines
- Pipelines start loading data to BigQuery immediately

## 📊 **Available Pipelines**

### 🎮 Pokemon Pipeline
- **Source**: Pokemon API (pokeapi.co)
- **Data**: Pokemon details, berries, abilities, moves, types
- **Dataset**: `pokemon_data`
- **Job**: `pokemon-pipeline-job`

### ♟️ Chess Pipeline
- **Source**: Chess.com API
- **Data**: Player profiles, games, online status, archives
- **Dataset**: `chess_data`
- **Job**: `chess-pipeline-job`

## ⚙️ **Configuration**

Both pipelines use environment variables for configuration - no secrets required:

### Pokemon Pipeline
- `POKEMON_RESOURCES`: Resources to load (default: `pokemon_details,berries`)
- `POKEMON_LIMIT`: Max Pokemon count (default: `50`)

### Chess Pipeline
- `CHESS_RESOURCES`: Resources to load (default: `players_profiles,players_online_status`)
- `CHESS_PLAYERS`: Player usernames (default: `magnuscarlsen,rpragchess,vincentkeymer,dommarajugukesh`)
- `CHESS_START_MONTH`: Start date YYYY/MM (default: `2024/01`)
- `CHESS_END_MONTH`: End date YYYY/MM (default: `2024/12`)

## 🏃 **Running Pipelines**

### Via Cloud Run Jobs
```bash
# Execute Pokemon pipeline
gcloud run jobs execute pokemon-pipeline-job --region us-central1

# Execute Chess pipeline
gcloud run jobs execute chess-pipeline-job --region us-central1
```

### Automatic Execution
Both jobs are automatically executed after deployment via Cloud Build trigger.

## 📈 **Monitoring**

### View Logs
```bash
# Pokemon pipeline logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=pokemon-pipeline-job" --limit 50

# Chess pipeline logs
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=chess-pipeline-job" --limit 50
```

### Query Data
```bash
# Pokemon data
bq query --use_legacy_sql=false "SELECT name, height, weight FROM \`pokemon_data.pokemon_details\` LIMIT 10"

# Chess data
bq query --use_legacy_sql=false "SELECT username, rating, title FROM \`chess_data.players_profiles\` LIMIT 10"
```

## 🔧 **Local Testing**

```bash
# Run verification script
chmod +x verify_setup.sh
./verify_setup.sh

# Test Pokemon pipeline locally
python pokemon_pipeline.py

# Test Chess pipeline locally
python chess_pipeline.py
```

## 🎉 **Why This Works**

1. **Cloud Run Default Service Account**: Automatically has BigQuery permissions
2. **Google Cloud Metadata Service**: Provides authentication tokens automatically
3. **dlt BigQuery Integration**: Uses Google Cloud client libraries with default credentials
4. **No Manual Configuration**: Everything works out of the box

## 📝 **Files Overview**

- `pokemon_pipeline.py` - Pokemon data pipeline
- `chess_pipeline.py` - Chess data pipeline
- `Dockerfile` - Multi-pipeline container
- `cloudbuild.yaml` - Cloud Build configuration
- `.github/workflows/deploy.yml` - GitHub Actions CI/CD
- `verify_setup.sh` - Setup verification script

## 🚨 **Troubleshooting**

### Common Issues
1. **Permission Denied**: Ensure Cloud Run service account has BigQuery permissions
2. **Dataset Not Found**: Create datasets with `bq mk` commands above
3. **API Not Enabled**: Enable required APIs in GCP console

### Debug Commands
```bash
# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Test BigQuery access
bq query --use_legacy_sql=false "SELECT 1"

# Check Cloud Run services
gcloud run services list --region us-central1
```

---

**🎯 Bottom Line**: Push to GitHub, set up Cloud Build trigger, and you're done! Everything is automatic.