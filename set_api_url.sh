#!/usr/bin/env bash
# Usage: ./set_api_url.sh https://your-deployment.vercel.app [path/to/README.md]
set -euo pipefail
url="${1:?deployment URL required}"; url="${url%/}"
readme="${2:-../alishaaverma/README.md}"
sed -i "s#https://alishaaverma-profile-api.vercel.app#${url}#g" "$readme"
echo "Updated $readme -> $url"
