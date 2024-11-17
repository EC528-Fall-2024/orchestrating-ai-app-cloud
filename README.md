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



Sprint Slides:
- [Sprint 1 Slides](https://docs.google.com/presentation/d/1z4AoG5UfYQ2fszpIUro6hpWGW8rE3Tl7FR-4X7SHE4k/edit?usp=sharing)
- [Sprint 2 Slides](https://docs.google.com/presentation/d/1mee4V68epsujxqhAZcVs1ev7JTiomgGfhy8vQIwue3M/edit?usp=sharing)
- [Sprint 3 Slides](https://docs.google.com/presentation/d/14hvVDBF61SQPKwuKxjp6b9_vxLr4BHbKBmncmGk4YH4/edit?usp=sharing)
- [Sprint 4 Slides](https://docs.google.com/presentation/d/1qjwYTIiLE6tRwIy_jwnmzikNkbKiSh1vVd72R9W0bHg/edit?usp=sharing)


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

![Architecture](https://github.com/user-attachments/assets/cd56583e-ad03-487c-89a6-f423d75a4865)

The solution architecture consists of several key components working together to provide end-to-end AI application deployment:

### Client Layer
- Command Line Interface (CLI)
  - Primary user interaction point
  - Handles data and source code uploads
  - Generates requirements.txt through pipreqs function
  - Monitors output storage for results

### Storage Layer
- Input Object Storage (S3 or Equivalent)
  - Stores three key components:
    - User data
    - requirements.txt
    - Source code
  - Acts as the trigger point for deployment pipeline

- Output Object Storage (S3 or Equivalent)
  - Stores computation results
  - Contains processed data and source code outputs
  - Accessible by clients for retrieving results

### Processing Layer
- Serverless Function (Lambda Equivalent)
  - Triggered by updates to input storage
  - Responsible for VM creation and setup
  - Handles three main tasks:
    - Installing requirements
    - Copying source code
    - Getting data from object storage
  - Creates and manages VM instances

### Management Layer
- SQL Database
  - Tracks key metadata:
    - Run ID
    - User ID
    - Path to Data
    - Path to Source Code
    - State
  - Maintains deployment state information

- Orchestrator Server
  - Monitors VM health through heartbeat mechanism
  - Manages state updates
  - Handles failure recovery
  - Coordinates between components
  - Updates database status

### Compute Layer
- VM Bare Metal
  - Executes AI workloads
  - Processes data
  - Reports status to orchestrator
  - Writes results to output storage

### Key Workflows:
1. Data Ingestion Flow:
   - Client uploads data and code
   - Pipreqs generates requirements
   - Materials stored in input storage

2. Deployment Flow:
   - Serverless function detects new input
   - Creates and configures VM
   - Orchestrator monitors deployment
   - Database tracks state changes

3. Execution Flow:
   - VM processes workload
   - Results written to output storage
   - Client notified of completion
   - State updated in database

4. Monitoring Flow:
   - Orchestrator receives VM heartbeats
   - Triggers rerun upon failures
   - Updates deployment state
   - Maintains system reliability

This architecture provides a scalable, reliable, and automated pipeline for AI application deployment, with clear separation of concerns and robust monitoring capabilities.

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

Current Progress (Through Sprint 4):
- Implemented basic CLI functionality
- Established GCP infrastructure
- Created containerized deployment pipeline
- Integrated authentication and security features
- Developed logging and monitoring systems

Next Steps:
- Deploy orchestrator
- Implement VM health checks
- Enhance dataset API integration
- Improve bucket management
- Add containerized source code security
- Implement dynamic resource allocation
- Create real AI workload demonstrations

Stretch Goals:
- Queueing system for async operations
- Enhanced secret management
- Multi-tenancy support
- Distributed ML training/inference

** **

Previous team worked with supervisor:
https://github.com/BU-CLOUD-F20/Securing_MS_Integrity
