#!/bin/bash
echo "🔍 Verifying Website Paths..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check HTML files
echo "📄 Checking HTML files..."
find website -name "*.html" -type f | while read -r file; do
    if grep -q 'src="src/' "$file" || grep -q "src='src/" "$file"; then
        echo "  ❌ $file - Still has old src paths"
    else
        echo "  ✅ $file - OK"
    fi
done

# Check JavaScript files
echo "📜 Checking JavaScript files..."
find website/src -name "*.js" -type f | while read -r file; do
    if grep -q 'fetch("assets/' "$file" || grep -q "fetch('assets/" "$file"; then
        echo "  ❌ $file - Still has old fetch paths"
    else
        echo "  ✅ $file - OK"
    done

# Check symlinks
echo "🔗 Checking symlinks..."
if [ -L "website/assets" ]; then
    echo "  ✅ website/assets symlink exists"
else
    echo "  ⚠️  website/assets symlink missing"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Verification complete!"
