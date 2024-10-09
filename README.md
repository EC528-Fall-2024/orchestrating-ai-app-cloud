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

Sprint Slides:
- [Sprint 1 Slides](https://docs.google.com/presentation/d/1z4AoG5UfYQ2fszpIUro6hpWGW8rE3Tl7FR-4X7SHE4k/edit?usp=sharing)
- [Sprint 2 Slides](https://docs.google.com/presentation/d/1mee4V68epsujxqhAZcVs1ev7JTiomgGfhy8vQIwue3M/edit?usp=sharing)

** **

## 1.   Vision and Goals Of The Project:

In recent years, the use of AI Applications have become common workloads on the cloud platform. Many of the workloads follow a small number of typical deployment patterns; However, it is hard for developers to bootstrap and onboard their applications on cloud without prior experience or knowledge. There are a few open-source initiatives that aim to handle certain aspects of this process, whether it be providing workflow automation, downloading dependencies, etc., but there is a gap in the market for a platform that handles the process from end-to-end. We look to provide the infrastructure that end-user developers need to successfully deploy and monitor AI applications through a simple command-line interface. 

Key goals of the project include:

- Streamlining the process of resource allocation, dependency management, and model deployment
- Integrating public and private sources of data, models, and dependencies into the cloud platform
- Leveraging Terraform and Ansible to autonomously deploy cloud instances
- Providing a reliable and intuitive command-line interface to programmatically interact with the product


## 2. Users/Personas Of The Project:

The AI deployment platform will be used by developers who look to host AI applications on the cloud without the requirement of hardware or extensive prior knowledge. User stories may include:

- Engineers who look to leverage hardware-dependent AI models will be automatically provided with an infrastructure with properly allocated hardware and resources such as memory, storage and computing.
- People unfamiliar with cloud computing who look to explore AI capability will be able to deploy AI models on the cloud without needing to specify techincal requirements. Data sourcing, dependency installation and model training will be accomplished autonomously on the cloud.

** **

## 3.   Scope and Features Of The Project:

The AI Deployment Platform provides:

- Support for sourcing models, datasets, and libraries from public and private sources
- Automatic cloud instance generation with proper hardware and resource allocation
- End-to-end training of AI models with automatic package installation and support
- Security of proprietary data such as data and models on cloud infrastructure

** **

## 4. Solution Concept

![User](https://github.com/user-attachments/assets/f8f9d610-5022-4f57-9a3d-359243f91373)

- Cloud Infrastructure:
  - Primary compute platform: Intel Developer Cloud (IDC)
  - Support for hybrid and multi-cloud deployments to leverage best-of-breed services

- Infrastructure:
  - Terraform for provisioning and managing cloud resources
  - Ansible for configuration management and application deployment

- AI/ML Frameworks:
  - Native support for popular frameworks like PyTorch and TensorFlow

- Model and Data Management:
  - Integration with HuggingFace for access to pre-trained models and datasets
  - Support for Kaggle datasets
  - Custom data connectors for proprietary data sources

- Security and Privacy:
  - Encryption mechanisms for data and model protection
  - Integration with cloud-native identity and access management services
  - Secure enclaves for handling sensitive data

- User Interface:
  - React-based web application for the front-end
  - RESTful API backend for programmatic access

** **

## 5. Acceptance criteria

Minimum acceptance criteria is
 
- Successfully deploy a basic AI model on IDC using the platform
  - Demonstrate end-to-end workflow from model selection to deployment
  - Show automated resource provisioning and configuration

- Automated setup of PyTorch environment

  - Correctly install PyTorch and its dependencies
  - Provide a reproducible environment across different deployments


- Integration with at least one external resource

  - Successfully pull a model or dataset from HuggingFace
  - Demonstrate proper versioning and caching of external resources


- Basic user interface for project management

  - Allow users to create, monitor, and manage AI projects
  - Provide real-time status updates on training and deployment processes


- Implement core security features

  - Secure user authentication and authorization
  - Data encryption for storage and transmission

** **

## 6.  Release Planning:

Release 1 (Foundation):
- Develop comprehensive user stories and requirements
- Research and prototype key technologies (Ansible, Terraform, OPEA)
- Set up development environment on IDC
- Implement basic user authentication and project creation

Release 2 (Core Infrastructure):
- Use Terraform to provision resources
- Begin managing AI workloads on IDC
- Configure cloud resources with Ansible playbooks (Setup libraries such as PyTorch, TensorFlow etc.)
- Develop initial CLI for platform interactions

Release 3 (External Integrations):
- Implement connectors for HuggingFace and Kaggle
- Develop a version control system for models and datasets
- Enhance CLI with data and model management commands

Release 4 (Security and Privacy):
- Implement end-to-end encryption for data and models
- Develop access control and permission management system
- Create secure integration methods for proprietary consumer data

Release 5 (User Interface and Optimization):
- Develop web-based user interface for project management
- Implement real-time monitoring and logging features
- Optimize resource allocation and scaling algorithms
- Conduct comprehensive testing and performance tuning

** **

Previous team worked with supervisor:
https://github.com/BU-CLOUD-F20/Securing_MS_Integrity
