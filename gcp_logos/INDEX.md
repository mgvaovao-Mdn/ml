# Logos GCP — Slide de formation MGVaovao

Icônes officielles Google Cloud (PNG 256×256) — un fichier par service utilisé dans l'architecture.

| Logo | Service GCP | Rôle dans MGVaovao | Où dans le projet |
|------|-------------|--------------------|-------------------|
| `01_cloud_run.png` | **Cloud Run (CPU)** | Service de signaling WebRTC / WebSocket entre le client web et le GPU | `README` §archi · `cloudbuild.yaml` |
| `02_cloud_run_gpu.png` | **Cloud Run GPU (NVIDIA L4)** | Pipeline d'inférence temps réel : VAD → ASR (Whisper) → MT (NLLB) → TTS (MMS) | `cloudbuild.yaml` (`--gpu nvidia-l4`) · `deploy/cloudrun_inference.yaml` |
| `03_cloud_storage.png` | **Cloud Storage (GCS)** | Stockage des modèles (`gs://mgvaovao-models`) et datasets (`gs://mgvaovao-datasets`), versioning activé | `deploy/vertex_training.yaml` · `scripts/init_gcs_checkpoints.py` |
| `04_vertex_ai.png` | **Vertex AI** | Custom Training Jobs, Pipelines (Kubeflow), Model Registry, Monitoring (drift chrF++/UTMOS) | `deploy/vertex_training.yaml` |
| `05_cloud_build.png` | **Cloud Build** | CI/CD : build + push des images Docker, déploiement Blue/Green zéro downtime | `cloudbuild.yaml` |
| `06_artifact_registry.png` | **Artifact Registry** | Registre des images Docker (`*-docker.pkg.dev/.../mgvaovao`) | `cloudbuild.yaml` |
| `07_pubsub.png` | **Pub/Sub** | Déclenchement du training sur évènement d'upload dataset (GCS → Pub/Sub → Vertex Pipeline) | `README` §archi · `trigger.yaml` |
| `08_cloud_logging.png` | **Cloud Logging** | Logs centralisés du build et des services (`CLOUD_LOGGING_ONLY`) | `cloudbuild.yaml` |
| `09_cloud_monitoring.png` | **Cloud Monitoring** | Supervision des services et des métriques d'inférence | `README` §archi |
| `10_iam.png` | **IAM** | Service accounts et rôles (`run.admin`, `iam.serviceAccountUser`) pour le pipeline | `cloudbuild.yaml` (iam-policy-binding) |
| `11_compute_engine.png` | **Compute Engine** | Machines GPU sous-jacentes : T4 (Vertex Training) / L4 (Cloud Run inférence) | `deploy/vertex_training.yaml` (`n1-standard-8` + `NVIDIA_TESLA_T4`) |

> Note : `06_artifact_registry.png` utilise l'icône Container Registry du jeu officiel (Artifact Registry est son successeur ; Google partage la même famille visuelle).

Source : jeu d'icônes officiel Google Cloud.
