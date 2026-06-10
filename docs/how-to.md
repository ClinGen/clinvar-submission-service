# How-To Guides

## Prerequisites for Setting Up Infrastructure

- Make sure the S3 bucket for the Terraform state file exists. The "path" (intermediate
  folders/directories) to the state file doesn't need to exist. Just make sure the
  bucket exists.
- Create a DynamoDB table for the lock file. It needs a partition key named "LockID" of
  type `String`. (That's the key name Terraform expects).
- Create your Ansible SSH keys using `ssh-keygen`.