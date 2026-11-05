#!/usr/bin/env bash
# Secrets stay in shell-local variables or child environment; never echo npm output.
set -eu
umask 077
publish() {
  npm publish --access public 2>&1
}
if output="$(publish)"; then
  exit 0
fi
case "$output" in
  *EOTP*) ;;
  *) echo 'npm publish failed (non-2FA); read back npm before retrying' >&2; exit 1 ;;
esac
# Recheck before any retry: npm may have accepted a request whose response failed.
if state=$(npm view "$RELEASE_PACKAGE_SPEC" version --json 2>&1); then
  exit 0
fi
case "$state" in *E404*) ;; *) echo 'npm state unknown; retry stopped' >&2; exit 1 ;; esac
for code_file in .npm*.txt; do
  [ -f "$code_file" ] || continue
  # Accept one code per line; comments and USED markers are never candidates.
  line_number=$(awk 'NF && $0 !~ /^[[:space:]]*#/ && $0 !~ /[^[:alnum:][:space:]-]/ {print NR; exit}' "$code_file")
  [ -n "$line_number" ] || continue
  otp=$(sed -n "${line_number}p" "$code_file" | tr -d '[:space:]')
  accepted=false
  if output="$(npm_config_otp="$otp" publish)"; then
    accepted=true
  elif state=$(npm view "$RELEASE_PACKAGE_SPEC" version --json 2>&1); then
    accepted=true
  fi
  if [ "$accepted" = true ]; then
    # Replace the consumed line only after npm confirms success, without printing it.
    # .local-ai is already ignored; an interrupted write cannot become a commit candidate.
    mkdir -p .local-ai/release-private || exit 43
    chmod 700 .local-ai/release-private || exit 43
    private_tmp=$(mktemp ".local-ai/release-private/used.XXXXXX") || {
      echo 'Published, but recovery-code marking failed' >&2; exit 43;
    }
    trap 'rm -f "$private_tmp"' EXIT
    if ! awk -v used="$line_number" 'NR == used {$0="# USED"} {print}' "$code_file" > "$private_tmp" || ! mv "$private_tmp" "$code_file"; then
      echo 'Published, but recovery-code marking failed; do not reuse that code' >&2; exit 43
    fi
    exit 0
  fi
  echo 'npm recovery publish failed; code preserved; read back npm before retrying' >&2
  exit 1
done
if [ -n "${NPM_OTP:-}" ]; then
  if output="$(npm_config_otp="$NPM_OTP" publish)"; then exit 0; fi
  echo 'npm OTP publish failed; read back npm before retrying' >&2
  exit 1
fi
echo 'npm EOTP: no private recovery code available; request an OTP from the user' >&2
exit 42
