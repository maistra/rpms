set -x 

DIR="$(cd $(dirname $0) ; pwd -P)"

if [ $# -ne 1 ] ; then
  echo "Usage $(basename $0) <proxy-full.tar.xz>"
  exit 1
fi

INPUT_FILE="$(cd $(dirname $1) ; pwd -P)/$(basename $1)"
OUTPUT_DIR="istio-proxy"
OUTPUT_FILE="${OUTPUT_DIR}.tar.xz"

if [ ! -f "${INPUT_FILE}" ] ; then
  echo "Could not locate input file: ${INPUT_FILE}"
  exit 2
fi

CHECKSUM=$(md5sum "${INPUT_FILE}" | awk '{print $1}')
sed -i "${DIR}/istio-proxy.spec" -e 's+\(^%global\s*checksum\s*\).*$+\1'${CHECKSUM}'+'
mv ${INPUT_FILE} "${DIR}/${OUTPUT_DIR}.${CHECKSUM}.tar.xz"
