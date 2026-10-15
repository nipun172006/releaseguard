# ReleaseGuard Environment Preflight

Checked on 16 October 2026 on macOS ARM64.

## Local toolchain

| Requirement | Result | Version or decision |
| --- | --- | --- |
| Git | Ready | 2.50.1 |
| Git identity | Ready | Global name and email are configured |
| Python | Ready | Use `python3.12` explicitly; 3.12.15 is installed |
| pip | Ready | Python 3.12 pip 26.2.1 |
| Node.js | Ready | Local Node 26.8.2; container and CI will use Node 22 |
| npm | Ready | 11.19.1 |
| Docker CLI | Ready | 28.5.1 |
| Docker daemon | Ready | Docker Desktop server 28.5.1 |
| Docker Compose | Ready | 2.40.3 |
| Terraform | Ready | 1.15.8 |
| kubectl | Ready with compatibility check pending | Client 1.37.1; final client/server compatibility will be checked after selecting the EKS version |
| Helm | Ready | 4.3.1 |
| AWS CLI | Ready and authenticated | 2.38.1 |
| GitHub CLI | Ready and authenticated | 2.95.0 |
| Minikube | Ready | 1.39.0 |
| jq | Ready | 1.7.1 |
| curl | Ready | 8.7.1 |
| Free disk space | Ready | Approximately 110 GiB available during preflight |

## Authentication checks

### GitHub

- Git identity is configured.
- Browser-based GitHub CLI authorization succeeded for the project account.
- `gh auth status` succeeds.
- Do not place a GitHub personal access token in the repository or `.env` files.

Verification command:

```bash
gh auth status
```

### AWS

- Browser-based AWS CLI authentication succeeded using temporary credentials.
- The default and target region is `ap-south-1` (Mumbai).
- STS identity verification succeeded.
- Read-only EKS and EC2 API checks succeeded in `ap-south-1`.
- Re-run `aws login --region ap-south-1` when the temporary session expires.
- Never commit access keys, credential files, Terraform state, or kubeconfig.

Verification commands:

```bash
aws sts get-caller-identity
aws configure get region
aws eks list-clusters --region ap-south-1
```

The account ID and identity ARN are verification data and must not be copied into project documentation or screenshots unless masked.

## Remaining gate

Step 2 is complete only when:

```text
[x] Required local command-line tools are installed
[x] Docker Desktop is running
[x] GitHub CLI authentication succeeds
[x] AWS CLI authentication succeeds
[x] AWS default region is ap-south-1
[x] Read-only EKS and EC2 API calls succeed
```
