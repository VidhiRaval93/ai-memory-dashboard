#!/bin/bash

echo "🔨 Building and deploying AI Chat Extractor extension..."

# Build TypeScript
echo "⚙️  Compiling TypeScript..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Copy compiled files to root for Chrome extension
    echo "📁 Copying files to extension root..."
    cp dist/contentScript.js .
    cp -r dist/agents .
    
    echo "✅ Extension ready for Chrome loading!"
    echo "🚀 Go to chrome://extensions/ and reload the extension"
else
    echo "❌ Build failed!"
    exit 1
fi
