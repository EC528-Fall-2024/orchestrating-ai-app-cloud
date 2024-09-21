** **

## Orchestrating AI Applications Deployments on the Cloud

** **

## 1.   Vision and Goals Of The Project:

In recent years, the use of AI Applications for both interfering and training are becoming common workloads on the cloud platform. Many of the workloads follow a small number of typical deployment patterns; However, it is hard for developers to bootstrap and onboard their applications on cloud. There are few open-source initiatives that aim to handle certain aspects of this process, whether it be providing workflow automation, downloading dependencies, etc., but there is a gap in the market for a platform that handles the process from end-to-end. The Intel platform for AI deployment will be the infrastructure that AI/ML end-user developers that will handle this process, as part of the Intel Cloud. Goals include:

- Bridging the gap between applications such as Terraform/Ansible and full deployment
- Providing a hassle-free application that will allow developers to train models without knowing the intricacies of the cloud
- Allow users to bring all aspects of an engineer’s project together in an single cloud environment


## 2. Users/Personas Of The Project:

The AI deployment platform will be used primarily by ML engineers and companies who do not have the resources to buy a large set of GPUs to train their models. User stories include:

- AI/ML engineers with knowledge of optimization and models but without the GPUs to train their model(s).
- People unfamiliar with cloud processes who simply want to rent a platform to train their model.
- People that want the capability of grabbing resources from a variety of different places (Ex. a particular PyTorch package, a dataset from another target, and a model from HuggingFace or some other website), and having someone else to figure out how to put everything together.
- People who have models with certain dependencies and  want to have all the packages installed on the cloud without worrying about it.


** **

## 3.   Scope and Features Of The Project:

The AI Deployment Platform provides:

- Support for pulling target models from HuggingFace, datasets from Kaggle and libraries like PyTorch
- End-to-end training of AI models with automatic package installation and support
- Security of proprietary data such as data and models on cloud infrastructure
- An all-in-one frontend application for consumers to interact with their models in a user-friendly way


** **

## 4. Solution Concept

- Intel Developer Cloud used to train models and process computations
- HuggingFace used for model/dataset targeting
- Kaggle used for dataset targeting
- PyTorch/Tensorflow used as inbuilt packages for developers to utilize from within environment
- Private consumer infrastructure utilized in secure manner alongside public infrastructure


## 5. Acceptance criteria

Minimum acceptance criteria is
 
- Successfully deploy a basic AI model on IDC using the platform
- Demonstrate automated setup of PyTorch environment
- Show integration with at least one external resource (e.g. HuggingFace)

Stretch goals are:


## 6.  Release Planning:

Release 1:
- User stories for the project
- Learn about Ansible, Terraform and OPEA
- Utilize IDC to learn usage and application intricacies 

Release 2:
- Use Terraform to provision resources
- Begin managing AI workloads on IDC
- Configure cloud resources with Ansible (Setup libraries such as PyTorch, TensorFlow etc.)

Release 3:
- Define a method to target third party sources (HuggingFace, Kaggle, Github)

Release 4:
- Provide capability to integrate cloud infrastructure with proprietary consumer data

Release 5:
- Merge, test and optimize all functionality

** **
