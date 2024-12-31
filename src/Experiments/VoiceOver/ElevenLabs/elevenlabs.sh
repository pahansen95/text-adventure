#!/usr/bin/env bash
set -eEou pipefail
: "${WORK_CACHE:?"Missing Work Cache"}"
declare WORK_DIR="${WORK_CACHE}/elevenlabs"; install -dm0755 "${WORK_DIR}"
: "${ELEVENLABS_API_KEY:?"Missing Elevenlabs API Key"}"
ELEVENLABS_BASE_URL="${ELEVENLABS_BASE_URL:-"https://api.elevenlabs.io"}"
declare subcmd="${1:?"Missing Subcommand"}"; shift
case "${subcmd,,}" in
  tts)
    : "${1:?"Missing Text to Dub"}"
    declare fingerprint; fingerprint="$(echo -n "$1" | md5sum | cut -d' ' -f1)"
    declare outfile="${WORK_DIR}/tts-${fingerprint:0:16}.mp3"
    curl -fsSL -X POST "${ELEVENLABS_BASE_URL}/v1/text-to-speech/9BWtsMINqrJLrRacOk9x" \
      -H "Xi-Api-Key: ${ELEVENLABS_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$(jq -cn --arg txt "$1" '{
        "text": $txt,
        "output_format": "mp3_44100_192"
      }')" > "${outfile}"
    ;;
  voices)
    declare outfile="${WORK_DIR}/voices.jsonl"
    curl -fsSL -X GET "${ELEVENLABS_BASE_URL}/v1/voices" \
      -H "Xi-Api-Key: ${ELEVENLABS_API_KEY}" \
      -H "Content-Type: application/json" | jq -c '.voices | sort_by(.name) | .[]' > "${outfile}"
    {
      printf -- 'Name VoiceID\n'
      printf -- '==== =======\n'
      jq -r '"\(.name) \(.voice_id)"' "${outfile}"
    } | column -t
    ;;
  *)
    echo "Unknown Subcommand: ${subcmd}" >&2
    exit 1
    ;;
esac

