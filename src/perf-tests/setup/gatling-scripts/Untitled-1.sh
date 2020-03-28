#!/usr/bin/env bash

readonly CURRENT_SCRIPT="$(basename -- ${BASH_SOURCE[0]})"
readonly CURRENT_DIRECTORY="$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly DOCKER_BINARY="$(command -v docker)"

source "${CURRENT_DIRECTORY}/scripts/config.sh"
source "${CURRENT_DIRECTORY}/scripts/util.sh"

# usage: usage [printer]
usage() {
  local printer="$(arg_or_default "$1" 'print_raw')"

  "${printer}" "usage: ${CURRENT_SCRIPT} [-h] [TAG]"
}

# usage: full_usage [printer]
full_usage() {
  local printer="$(arg_or_default "$1" 'print_raw')"

  usage "${printer}"
  "${printer}"
  "${printer}" 'Build tool for esp8266 development container'
  "${printer}"
  "${printer}" 'arguments:'
  "${printer}" '  -h                    show this help message and exit'
  "${printer}" '  TAG                   the tag of the image to build'
}


# usage: build_image [tag]
build_image() {
  # Generate image name
  local name="${DOCKER_IMAGE_NAME}:$(arg_or_default "$1" \
                                                    "${DOCKER_IMAGE_TAG}")"

  print "building image ${name}"

  # Run docker with the provided arguments
  docker build -t "${name}" \
                  "${CURRENT_DIRECTORY}/${DOCKER_LOCAL_SOURCE_DIRECTORY}"
}

# usage: main [-h] [-d DATA_DIRECTORY] [-t TAG] [ARGS...]
main() {
  check_requirements "$@" || exit 1

  while getopts ':h' OPT; do
    case "${OPT}" in
      h)
        full_usage
        exit 0
        ;;
      ?)
        full_usage
        print
        error "invalid argument: ${OPTARG}"
        exit 1
        ;;
    esac
  done

  shift $((OPTIND - 1))

  build_image "$@"
}

if [[ "$0" == "${BASH_SOURCE[0]}" ]]; then
  main "$@"
fi