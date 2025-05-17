# NIQ Innovation Enablement – Challenge 1: Object Counting

## 🚀 Overview

This project implements a scalable object counting system for images via a Flask-based API, TensorFlow Serving, and containerized microservices.

---

### ✨ Features

* Flask REST API for image processing
* TensorFlow Serving for high-performance model inference
* PostgreSQL and MongoDB integration
* Dockerized microservices
* Clean, modular architecture
* Environment-based configuration
* One-click setup script

---

## 🧩 Architecture

The project is structured with a clean, layered architecture:

* **Entrypoints**: Exposes APIs, handles input validation and HTTP routing
* **Adapters**: Interfaces with databases and inference engines
* **Domain**: Contains core business logic and orchestration rules

---
## 📁 Folder Structure
```aiignore
NielsenIQ_MLOps
├── alembic.ini
├── archive
│ └── requirements.txt
├── counter
│ ├── adapters
│ │ ├── count_repo.py
│ │ ├── helpers.py
│ │ ├── __init__.py
│ │ ├── models.py
│ │ ├── mscoco_label_map.json
│ │ └── object_detector.py
│ ├── config.py
│ ├── constants.py
│ ├── debug.py
│ ├── domain
│ │ ├── actions.py
│ │ ├── __init__.py
│ │ ├── models.py
│ │ ├── ports.py
│ │ └── predictions.py
│ ├── entrypoints
│ │ ├── __init__.py
│ │ ├── main.py
│ │ └── webapp.py
│ ├── __init__.py
│ └── resources
│     └── arial.ttf
├── data
├── docker-compose.yml
├── Dockerfile
├── migrations
│ ├── env.py
│ ├── README
│ ├── script.py.mako
│ └── versions
│     └── ae2870447b2b_initial_schema.py
├── poetry.lock
├── pyproject.toml
├── README.md
├── resources
│ └── images
│     ├── boy.jpg
│     ├── cat.jpg
│     └── food.jpg
├── setup.sh
├── tests
│ ├── adapters
│ │ └── test_count_repo.py
│ ├── conftest.py
│ ├── domain
│ │ ├── helpers.py
│ │ ├── __init__.py
│ │ ├── test_actions.py
│ │ └── test_predictions.py
│ ├── entrypoints
│ │ └── test_webapp.py
│ └── __init__.py
└── tmp
    ├── debug
    └── model
```

---

## 🛠️ Prerequisites

* Docker & Docker Compose
* Python 3.12 or higher
* Git
* (Windows users) WSL2 or Git Bash to run the setup script

---

## ⚙️ Setup Options

### ✅ Option 1: One-Click Script (Recommended)

```bash
git clone https://github.com/Joish/NielsenIQ_MLOps.git
cd NielsenIQ_MLOps
sudo ./setup.sh
```

This script will:

* Download and extract the RFCN pre-trained model
* Configure permissions and environment variables
* Spin up all required Docker containers

**Flags:**

```bash
./setup.sh --force     # Force model re-download
./setup.sh --build     # Rebuild Docker images
./setup.sh --down      # Stop all containers
./setup.sh --help      # Show usage
```

---

### 📦 Option 2: Docker Compose (Manual Alternative)

1. **Prepare the RFCN model** (see [Shared Step](#shared-step-download-and-prepare-rfcn-model))
2. Ensure `.env` is properly set
3. Launch services:

```bash
docker compose up --build
```

**Common commands:**

```bash
docker compose down                  # Stop and remove containers
docker compose logs -f               # View logs in real-time
docker compose restart <service>     # Restart a single service
docker compose ps                    # View container statuses
```

---

### 🛠️ Option 3: Fully Manual Setup

1. **Prepare the RFCN model** (see [Shared Step](#shared-step-download-and-prepare-rfcn-model))
2. Manually run services:

#### PostgreSQL

```bash
docker run --name demo-postgres \
  -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=demo_db -p 5432:5432 -d postgres:15
```

#### TensorFlow Serving (Linux)

```bash
num_physical_cores=$(lscpu | awk '/Core\(s\) per socket/ {c=$4} /Socket\(s\)/ {s=$2} END {print c * s}')

docker rm -f tfserving
docker run --name=tfserving \
  -p 8500:8500 -p 8501:8501 \
  -v "$(pwd)/tmp/model:/models" \
  -e OMP_NUM_THREADS=$num_physical_cores \
  -e TENSORFLOW_INTER_OP_PARALLELISM=2 \
  -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores \
  intel/intel-optimized-tensorflow-serving:2.8.0 \
  --model_config_file=/models/model_config.config
```

#### TensorFlow Serving (Windows PowerShell)

```powershell
$num_physical_cores=(Get-WmiObject Win32_Processor).NumberOfCores

docker rm -f tfserving
docker run `
  --name=tfserving `
  -p 8500:8500 -p 8501:8501 `
  -v "$pwd\tmp\model:/models" `
  -e OMP_NUM_THREADS=$num_physical_cores `
  -e TENSORFLOW_INTER_OP_PARALLELISM=2 `
  -e TENSORFLOW_INTRA_OP_PARALLELISM=$num_physical_cores `
  intel/intel-optimized-tensorflow-serving:2.8.0 `
  --model_config_file=/models/model_config.config
```

---

### 📁 Shared Step: Download and Prepare RFCN Model

```bash
wget https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz
tar -xzvf rfcn_resnet101_fp32_coco_pretrained_model.tar.gz -C tmp
chmod -R 777 tmp/rfcn_resnet101_coco_2018_01_28
mkdir -p tmp/model/rfcn/1
mv tmp/rfcn_resnet101_coco_2018_01_28/saved_model/saved_model.pb tmp/model/rfcn/1
rm -rf tmp/rfcn_resnet101_coco_2018_01_28
```

---

## 🔐 Environment Variables

Update your `.env` or environment accordingly:

```env
# Model Configuration
MODEL_URL="https://storage.googleapis.com/intel-optimized-tensorflow/models/v1_8/rfcn_resnet101_fp32_coco_pretrained_model.tar.gz"
MODEL_NAME="rfcn_resnet101_coco_2018_01_28"
MODEL_PATH="tmp/model/rfcn/1"

# PostgreSQL
POSTGRES_HOST="postgres"
POSTGRES_PORT="5432"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
POSTGRES_DB="counter_db"

# MongoDB
MONGODB_HOST="mongodb"
MONGODB_PORT="27017"

# TensorFlow Serving
TFS_HOST="localhost"
TFS_PORT="8500"
RFCN_MODEL_NAME="rfcn"
```

---

## 🧪 Run the Tests

```bash
docker exec -it counter-app bash
pytest
(or)
pytest --cov --cov-report term-missing # with coverage
```

---

## 📡 API Usage

Call the service to count objects in an image:

```bash
curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://0.0.0.0:5000/v1/object-count
curl -F "threshold=0.9" -F "file=@resources/images/food.jpg" -F "return_total=true" http://0.0.0.0:5000/v1/object-count
curl -F "threshold=0.9" -F "file=@resources/images/food.jpg" -F "model_name=fake" http://0.0.0.0:5000/v1/object-count
```

---

## 🧯 Troubleshooting

* **Containers not starting**

  ```bash
  ./setup.sh --down
  ./setup.sh --build
  ```

* **Logs**

  ```bash
  docker compose logs -f
  ```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---