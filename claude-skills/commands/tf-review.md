Using the terraform-azure skill, review the following Terraform code for Azure best practices.

Check:
1. Provider version pinning
2. Remote state configuration
3. Resource naming convention (<type>-<workload>-<env>-<region>)
4. No hardcoded secrets
5. UAMI usage (not SP secrets where possible)
6. Resource tagging (environment, owner, costcenter)
7. Production resource locks
8. Diagnostic settings
9. Private endpoints for PaaS services
10. AKS: workload identity, azure policy addon, RBAC

Output: table of findings with severity, then corrected code blocks.

Terraform code:
$ARGUMENTS
