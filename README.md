** **

## Orchestrating AI Applications Deployments on the Cloud

** **

## 1.   Vision and Goals Of The Project:

In recent years, the use of AI Applications for both interfering and training are becoming common workloads on the cloud platform. Many of the workloads follow a small number of typical deployment patterns; However, it is hard for developers to bootstrap and onboard their applications on cloud. There are few open-source initiatives that aim to handle certain aspects of this process, whether it be providing workflow automation, downloading dependencies, etc., but there is a gap in the market for a platform that handles the process from end-to-end. The Intel platform for AI deployment will be the infrastructure that AI/ML end-user developers that will handle this process, as part of the Intel Cloud. 

Key goals of the project include:

- Bridging the gap between applications such as Terraform/Ansible and full deployment
- Providing a hassle-free application that will allow developers to train models without knowing the intricacies of the cloud
- Offer a unified cloud environment that integrates all aspects of an AI/ML engineering project
- Streamline the process of resource allocation, dependency management, and model deployment


## 2. Users/Personas Of The Project:

The AI deployment platform will be used primarily by ML engineers and companies who do not have the resources to buy a large set of GPUs to train their models. User stories include:

- AI/ML engineers that possess the knowledge of optimization and models but without the GPUs to train their model(s).
- People unfamiliar with cloud processes who simply want to rent a platform to train their model without worrying about the underlying infrastructure and require a simple interface to manage cloud resources.
- People that want the capability of grabbing resources from a variety of different places (Ex. a particular PyTorch package, a dataset from another target, and a model from HuggingFace or some other website), and having someone else to figure out how to put everything together.
- People who have models with certain dependencies and want to have all the packages installed on the cloud without worrying about it.


** **

## 3.   Scope and Features Of The Project:

The AI Deployment Platform provides:

- Support for pulling target models from HuggingFace, datasets from Kaggle and libraries like PyTorch
- End-to-end training of AI models with automatic package installation and support
- Security of proprietary data such as data and models on cloud infrastructure
- An all-in-one frontend application for consumers to interact with their models in a user-friendly way


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

Stretch goals are:



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
