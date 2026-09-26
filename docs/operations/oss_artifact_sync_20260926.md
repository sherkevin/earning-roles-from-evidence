# OSS artifact synchronization

Status: operational as of 2026-09-26.

This project can archive reproducibility artifacts in the following OSS region:

- Endpoint: `oss-cn-zhangjiakou.aliyuncs.com`
- Region: `cn-zhangjiakou`
- Archive bucket: `ai4sci-develop-storage`
- Fast working bucket: `ai4sci-develop-fast`

The AccessKey ID and AccessKey Secret were supplied out of band for this session. They are intentionally absent from this document, experiment logs, manifests, shell history, and Git. Upload commands receive them only through ephemeral process variables and are not retained after synchronization.

## Client and network route

The official OSSUtil v2.4.0 macOS arm64 client was downloaded from Alibaba's public distribution URL and is kept outside the repository at:

`/tmp/ossutil-v2.4.0/bin/ossutil-2.4.0-mac-arm64/ossutil`

Direct virtual-host requests to bucket-specific DNS names terminated during TLS negotiation in this environment. The generic regional endpoint was reachable. A temporary local CONNECT relay therefore maps bucket-host CONNECT targets to the generic regional endpoint while preserving the original TLS host. This is a transport workaround only; it does not change the OSS endpoint, bucket, authentication, or object names. The relay is stopped after each synchronization session and is never committed.

Example command shape (credentials omitted):

```bash
HTTPS_PROXY=http://127.0.0.1:18080 \
HTTP_PROXY=http://127.0.0.1:18080 \
ALL_PROXY=http://127.0.0.1:18080 \
NO_PROXY= \
ossutil cp <local-path> oss://ai4sci-develop-storage/earning-roles/aamas2027/<date>/ \
  --endpoint oss-cn-zhangjiakou.aliyuncs.com \
  --region cn-zhangjiakou --proxy env \
  --access-key-id "$OSS_AK" --access-key-secret "$OSS_SK" \
  --recursive --no-error-report --no-progress
```

## Artifact policy

Upload only compact, project-authored evidence needed for review or reproduction: configuration, raw/processed result files, hashes, reports, ADRs, and paper-source artifacts. Do not upload credentials, third-party source clones, nested benchmark workspaces, private keys, or unreviewed user data. Every upload must have a local manifest containing relative path, byte size, and SHA-256 before transfer; remote object listing is checked after transfer.

The current synchronization uses a date-stamped immutable archive prefix and a separate small active prefix when needed. Existing historical objects are not overwritten by this workflow.

## Security observation

Listing the fast bucket exposed existing names resembling a private SSH key and SSH configuration under `caixu/.local/.ssh/`. No contents were downloaded or inspected. If those objects are not intentionally public to the bucket's operators, the bucket owner should audit access and rotate the corresponding key material.
