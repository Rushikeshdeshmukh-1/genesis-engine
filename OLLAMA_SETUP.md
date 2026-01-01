# Installing Ollama for Local LLM

## Quick Installation Steps

1. **Download Ollama** (already downloading to your project folder)
   - Or download from: https://ollama.com/download

2. **Install Ollama**
   ```powershell
   # Run the installer (double-click OllamaSetup.exe)
   # Or run silently:
   .\OllamaSetup.exe /S
   ```

3. **Verify Installation**
   ```powershell
   ollama --version
   ```

4. **Pull a Model** (Choose based on your PC specs)
   
   ### For 8GB RAM:
   ```powershell
   ollama pull llama3.2:3b
   ```
   - Size: ~2GB
   - Speed: Very fast
   - Quality: Good for most tasks
   
   ### For 16GB RAM:
   ```powershell
   ollama pull llama3.2
   ```
   - Size: ~4.7GB
   - Speed: Fast
   - Quality: Excellent
   
   ### For 32GB+ RAM:
   ```powershell
   ollama pull llama3.1:70b
   ```
   - Size: ~40GB
   - Speed: Slower but very powerful
   - Quality: Best

5. **Start Ollama Service**
   ```powershell
   # Ollama runs automatically after installation
   # Check if running:
   ollama list
   ```

6. **Test the Model**
   ```powershell
   ollama run llama3.2:3b "Generate a tech business idea"
   ```

## Recommended Model for Your Setup

Based on typical PC specs, I recommend starting with **llama3.2:3b**:
- Fast responses
- Low memory usage
- Good quality for business idea generation

## After Installation

The backend will automatically detect Ollama and start using it instead of mock data!

No code changes needed - just install Ollama and pull a model.

## Troubleshooting

### Ollama not starting?
```powershell
# Check if service is running
Get-Service Ollama

# Start manually if needed
ollama serve
```

### Model too slow?
Try a smaller model:
```powershell
ollama pull phi3:mini
```

### Want better quality?
Try a larger model (if you have RAM):
```powershell
ollama pull llama3.2:7b
```
