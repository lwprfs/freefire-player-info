#!/bin/bash
echo "🔄 Rolling back path changes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Restore HTML files from backups
find website -name "*.html.bak" -type f | while read -r backup; do
    original="${backup%.bak}"
    if [ -f "$backup" ]; then
        mv "$backup" "$original"
        echo "  ✅ Restored: $original"
    fi
done

# Restore JavaScript files from backups
find website/src -name "*.js.bak" -type f | while read -r backup; do
    original="${backup%.bak}"
    if [ -f "$backup" ]; then
        mv "$backup" "$original"
        echo "  ✅ Restored: $original"
    fi
done

# Remove symlinks if they were created by this script
if [ -L "website/assets" ]; then
    rm website/assets
    echo "  ✅ Removed: website/assets symlink"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Rollback complete!"
