SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

for file in *.py; do
    echo "Running $file ..."
    python3 "$file" &
done

wait

echo "All models completed."
