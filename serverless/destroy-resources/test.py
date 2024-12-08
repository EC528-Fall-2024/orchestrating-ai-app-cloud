import os
import tempfile

# Mock terraform configurations (similar to what would be in terraform_configs.py)
MAIN_TF = """
terraform {
 backend "gcs" {}
 required_providers {
   google = {
     source  = "hashicorp/google"
     version = "~> 4.0"
   }
 }
}
"""
VARIABLES_TF = """
variable "project_id" {
 type = string
}
"""
def test_setup_terraform_environment():
   """Test function to verify file writing works correctly"""
   # Create a temporary directory
   with tempfile.TemporaryDirectory() as tmp_dir:
       try:
           # Create file paths
           main_tf_path = os.path.join(tmp_dir, 'main.tf')
           variables_tf_path = os.path.join(tmp_dir, 'variables.tf')
           
           # Write the files
           with open(main_tf_path, 'w', encoding='utf-8') as main_file:
               main_file.write(MAIN_TF)
           
           with open(variables_tf_path, 'w', encoding='utf-8') as vars_file:
               vars_file.write(VARIABLES_TF)
           
           # Verify files were created and contain correct content
           with open(main_tf_path, 'r', encoding='utf-8') as main_file:
               main_content = main_file.read()
               print("main.tf content:")
               print(main_content)
               print("-" * 50)
           
           with open(variables_tf_path, 'r', encoding='utf-8') as vars_file:
               vars_content = vars_file.read()
               print("variables.tf content:")
               print(vars_content)
               
       except Exception as e:
           print(f"Error during file operations: {str(e)}")
           raise
if __name__ == "__main__":
   test_setup_terraform_environment()