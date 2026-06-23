#!/usr/bin/env bash
set -euo pipefail

RTK_VERSION="${RTK_VERSION:-0.42.4}"
TARGET="${TARGET:-vendor/rtk-x86_64-unknown-linux-musl}"
EXPECTED_SHA256="${EXPECTED_SHA256:-1d8bf5f1861f5ce33236400b1d93b967aec30b6a456e9a0b43b1584c5200119a}"
ASSET="rtk-x86_64-unknown-linux-musl.tar.gz"
URL="https://github.com/rtk-ai/rtk/releases/download/v${RTK_VERSION}/${ASSET}"

if command -v sha256sum >/dev/null 2>&1; then
  sha256_cmd=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then
  sha256_cmd=(shasum -a 256)
else
  echo "error: need sha256sum or shasum" >&2
  exit 1
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

mkdir -p "$(dirname "$TARGET")"
echo "Downloading rtk ${RTK_VERSION} (${ASSET})..." >&2
curl -fsSL "$URL" -o "$tmpdir/$ASSET"
tar -xzf "$tmpdir/$ASSET" -C "$tmpdir"

src=""
for candidate in \
  "$tmpdir/rtk" \
  "$tmpdir/rtk-x86_64-unknown-linux-musl" \
  "$tmpdir"/*/rtk \
  "$tmpdir"/*/rtk-x86_64-unknown-linux-musl; do
  if [[ -f "$candidate" ]]; then
    src="$candidate"
    break
  fi
done

if [[ -z "$src" ]]; then
  echo "error: could not find rtk binary in downloaded archive" >&2
  find "$tmpdir" -maxdepth 3 -type f >&2
  exit 1
fi

install -m 0755 "$src" "$TARGET"
actual="$(${sha256_cmd[@]} "$TARGET" | awk '{print $1}')"
if [[ "$actual" != "$EXPECTED_SHA256" ]]; then
  echo "error: checksum mismatch for $TARGET" >&2
  echo "expected: $EXPECTED_SHA256" >&2
  echo "actual:   $actual" >&2
  rm -f "$TARGET"
  exit 1
fi

echo "Installed $TARGET" >&2
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    "$TARGET" --version
    ;;
  *)
    echo "Checksum verified. Not executing $TARGET on $(uname -s)/$(uname -m); it is intended for Linux x86_64 containers." >&2
    ;;
esac
