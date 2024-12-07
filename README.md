** **
# Orchestrating AI Applications Deployments on the Cloud

** **
## Team

| Name         | Github Handle | Email           |
| :----------- | ------------- | --------------- |
| Ryan Darrow  | darrowball13  | darrowry@bu.edu |
| Peter Gu     | peterguzw0927 | petergu@bu.edu  |
| Harlan Jones | harlanljones  | hljones@bu.edu  |
| Kris Patel   | Kris7180      | krispat@bu.edu  |
| Jimmy Sui    | gimmymansui   | suijs@bu.edu    |
| Thai Nguyen  | ThaiNguyen03  | quocthai@bu.edu |

Mentorship provided by Shripad Nadgowda at Intel

** **
## Sprint Presentations:

Sprint Demo Videos:
- [Sprint 1 Demo](https://drive.google.com/file/d/1Y6o8N7rpiolrclTE44CY9-EwQOUWCRaX/view?usp=sharing)
- [Sprint 2 Demo](https://drive.google.com/file/d/1r7dno8U-bDXu80lfAFVU6rA1jhGb-X1e/view?usp=sharing)
- [Sprint 3 Demo](https://drive.google.com/file/d/1eMly8_TVdyiS4ya3N4kQN-CgwZXLV_Ih/view?usp=drive_link)
- [Sprint 4 Demo](https://drive.google.com/file/d/1AdgprASdOFpZCtCDNqXb6F9QehCVZP5h/view?usp=drive_link)
- [Sprint 5 Demo](https://drive.google.com/file/d/1y8o_gFfOZSBZpkKAB7xoacds8kDNdQWs/view?usp=sharing)



Sprint Slides:
- [Sprint 1 Slides](https://docs.google.com/presentation/d/1z4AoG5UfYQ2fszpIUro6hpWGW8rE3Tl7FR-4X7SHE4k/edit?usp=sharing)
- [Sprint 2 Slides](https://docs.google.com/presentation/d/1mee4V68epsujxqhAZcVs1ev7JTiomgGfhy8vQIwue3M/edit?usp=sharing)
- [Sprint 3 Slides](https://docs.google.com/presentation/d/14hvVDBF61SQPKwuKxjp6b9_vxLr4BHbKBmncmGk4YH4/edit?usp=sharing)
- [Sprint 4 Slides](https://docs.google.com/presentation/d/1qjwYTIiLE6tRwIy_jwnmzikNkbKiSh1vVd72R9W0bHg/edit?usp=sharing)
- [Sprint 5 Slides](https://docs.google.com/presentation/d/1ku1LTP_kWTvcnEp0mIy9HmjLlY67A9Ctv_QcTRNJHqQ/edit?usp=sharing)

Final Presentation:
- [Final Presentation](https://docs.google.com/presentation/d/1oEVWBWb2RCjHnjuXlV53RF1UR75O6lgDaAwiJFKLADU/edit?usp=sharing)

** **

## 1.   Vision and Goals Of The Project:

Cynthus aims to simplify the deployment of AI applications on cloud platforms. While initially designed for Intel Developer Cloud (IDC), the project currently operates on Google Cloud Platform (GCP) due to accessibility considerations. The platform addresses the challenges developers face when deploying AI workloads by providing automated solutions for resource management, dependency handling, and deployment orchestration.
Key goals of the project include:

- Creating a simplified command-line interface for end-to-end AI application deployment
- Automating resource allocation and dependency management through Terraform and Ansible
- Providing seamless integration with public datasets and models from sources like HuggingFace and Kaggle
- Implementing secure containerized deployments using Docker
- Managing cloud infrastructure through automated scripts and serverless functions
- Supporting scalable and maintainable AI workload deployments


## 2. Users/Personas Of The Project:

The platform serves various users in the AI development ecosystem:

- AI developers who need an efficient way to deploy models without managing complex infrastructure
- Engineers requiring specific hardware configurations for AI model deployment
- Newcomers to cloud computing who want to explore AI capabilities without deep cloud expertise
- Teams needing secure and scalable infrastructure for AI workloads
- Developers working with custom models who need flexible deployment options
- Organizations requiring automated resource management and cost optimization

** **

## 3.   Scope and Features Of The Project:

The AI Deployment Platform provides:

- Command-line interface with:
  - User authentication via Firebase
  - Project initialization and configuration
  - Automated deployment to cloud storage
  - Resource management and monitoring

- Cloud Infrastructure:
  - Serverless functions for VM provisioning
  - MySQL database for logging and state management
  - Cloud Storage buckets for project data and source code
  - Docker containerization for application deployment

- Integration Features:
  - Support for HuggingFace and Kaggle datasets
  - Automated dependency management
  - Version control for containers and deployments

- Security Features:
  - Firebase authentication
  - Resource tagging for access control
  - Secure secret management
  - Service account management

** **

## 4. Solution Concept

![Architecture](https://github.com/user-attachments/assets/c5fdc6d3-1cc0-4f9d-8a4c-61d0807b5ef6)


The solution architecture consists of several key components working together to provide end-to-end AI application deployment:

### Client Layer
- Command Line Interface (CLI)
  - Primary user interaction point
  - Handles authentication through Firebase
  - Manages project initialization and configuration
  - Builds and uploads Docker containers
  - Monitors deployment status and results

### Data Management Layer
- Dataset Downloader
  - Integrates with Kaggle and HuggingFace
  - Manages dataset versioning and storage
  - Handles data preprocessing requirements

- Bucket Builder
  - Creates and manages GCP storage buckets
  - Generates requirements.txt automatically
  - Handles input/output storage configuration

### Storage Layer
- Input Object Storage (GCP Bucket)
  - Stores user data, requirements.txt, and source code
  - Triggers deployment workflows
  - Manages access control through Firebase authentication

- Output Object Storage (GCP Bucket)
  - Stores computation results
  - Maintains execution logs
  - Provides secure access to processed data

### Processing Layer
- Cloud Run Functions
  - Handles VM provisioning and configuration
  - Manages container deployment
  - Coordinates with orchestrator for deployment status
  - Processes authentication and authorization

### Management Layer
- SQL Database
  - Tracks deployment metadata:
    - Run ID and User ID
    - Resource paths and states
    - Deployment configurations
  - Maintains system state information

- Orchestrator Server
  - Monitors VM health through heartbeats
  - Manages container lifecycle
  - Handles failure recovery
  - Updates deployment states
  - Coordinates between components

### Container Registry Layer
- Artifacts Registry
  - Stores Docker container images
  - Manages image versions
  - Provides secure container distribution
  - Integrates with VM deployment

### Compute Layer
- VM Bare Metal
  - Executes containerized AI workloads
  - Reports health status to orchestrator
  - Manages data processing
  - Handles output generation

### Key Workflows:
1. Authentication Flow:
   - User authenticates via Firebase
   - Access tokens manage resource permissions
   - Secure communication between components

2. Deployment Flow:
   - Container image built and pushed to Artifacts Registry
   - Cloud Run Functions provision VM resources
   - Orchestrator manages deployment lifecycle
   - System state tracked in SQL database

3. Data Management Flow:
   - Dataset Downloader fetches external data
   - Bucket Builder creates storage infrastructure
   - Input/Output buckets manage data lifecycle

4. Execution Flow:
   - VM pulls container from Artifacts Registry
   - Workload processes data
   - Results stored in output bucket
   - Status updates maintained in database

5. Monitoring Flow:
   - Orchestrator tracks VM health
   - System handles failure recovery
   - Metrics and logs collected
   - State management maintained

** **

## 5. Acceptance criteria

Minimum acceptance criteria includes:

- Functional CLI for end-to-end deployment:
  - User authentication and project management
  - Automated resource provisioning
  - Container deployment and monitoring

- Cloud Infrastructure Setup:
  - Successful VM provisioning with Terraform
  - Automated configuration with Ansible
  - Docker container deployment

- External Integrations:
  - Working connections to HuggingFace and Kaggle
  - Successful data and model management

- Security Implementation:
  - User authentication
  - Resource access control
  - Secure deployment pipeline

** **

## 6.  Release Planning:

Current Progress:
- All functional requirements met
- Persisted through a Cloud Platform migration and a major architecture redesign

Stretch Goals:
- Queueing system for async operations
- Enhanced secret management
- Multi-tenancy support
- Distributed ML training/inference
- GPU support
- CLI refinements
- Billing managemet
- GUI tracking
** **

Previous team worked with supervisor:
https://github.com/BU-CLOUD-F20/Securing_MS_Integrity
