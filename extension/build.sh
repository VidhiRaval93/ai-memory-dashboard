#!/bin/bash

echo "�� Building AI Chat Extractor extension..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build TypeScript
echo "⚙️  Compiling TypeScript..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Compiled files are in the dist/ directory"
    echo "🚀 You can now load the extension in Chrome from the extension/ directory"
else
    echo "❌ Build failed!"
    exit 1
fi
