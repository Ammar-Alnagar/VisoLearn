# 🛠️ Installation & Setup

## 📋 Prerequisites & System Requirements

### 🔰 Minimum Requirements
- **🖥️ Operating System**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **🐍 Python**: 3.8 or higher (3.10+ recommended)
- **💾 RAM**: 4GB minimum, 8GB recommended
- **💾 Storage**: 2GB free space for installation, 5GB for full usage
- **🌐 Internet**: Stable connection for AI API calls (10 Mbps+ recommended)
- **🌐 Browser**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+

### 🚀 Recommended Requirements
- **💾 RAM**: 16GB for optimal performance
- **💾 Storage**: SSD with 10GB+ free space
- **🌐 Internet**: High-speed broadband (50 Mbps+)
- **🖥️ GPU**: CUDA-compatible GPU for enhanced performance (optional)
- **🖥️ CPU**: Quad-core processor or better

### 🔧 Supported Platforms

**Desktop Platforms:**
- ✅ Windows 10/11 (64-bit)
- ✅ macOS 10.14+ (Mojave and later)
- ✅ Ubuntu 18.04+ and other Debian-based Linux distributions
- ✅ Fedora 30+ and other RPM-based Linux distributions

**Cloud Platforms:**
- ✅ AWS EC2 (Ubuntu/Amazon Linux)
- ✅ Google Cloud Platform
- ✅ Microsoft Azure
- ✅ DigitalOcean Droplets

## 📦 Installation Methods

### 🏠 Method 1: Standard Local Installation

#### 📥 Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/VisoLearn-2.git
cd VisoLearn-2
```

**Troubleshooting:**
- If you get `git: command not found`, install Git first:
  - Windows: Download from [git-scm.com](https://git-scm.com/)
  - macOS: `brew install git`
  - Linux: `sudo apt install git` (Ubuntu/Debian) or `sudo dnf install git` (Fedora)

#### 🐍 Step 2: Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

**Alternative Virtual Environment Options:**
- **conda**: `conda create -n visolearn python=3.10` then `conda activate visolearn`
- **pyenv**: `pyenv virtualenv 3.10.0 visolearn` then `pyenv activate visolearn`

**Troubleshooting:**
- If `python -m venv` fails, ensure you have the venv module installed
- On Ubuntu/Debian: `sudo apt install python3-venv`
- On Fedora: `sudo dnf install python3-virtualenv`

#### 📦 Step 3: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install additional dependencies for development (optional)
pip install pytest pytest-cov black flake8 mypy
```

**Dependency Details:**
- **gradio==5.35.0**: Web interface framework
- **pillow**: Image processing library
- **google-generativeai==0.8.4**: Google AI integration
- **openai**: OpenAI API client
- **python-dotenv**: Environment variable management

**Troubleshooting:**
- If installation fails due to permission issues, try:
  ```bash
  pip install --user -r requirements.txt
  ```
- For network issues, you may need to configure pip to use a proxy

#### 🔑 Step 4: Configure Environment Variables

Create a `.env` file in the project root:
```bash
cp .env.example .env  # If .env.example exists
nano .env
```

**Required API Keys:**
```env
# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Hugging Face token
HF_TOKEN=your_hf_token_here
```

**API Key Sources:**
- Google API Key: [Google Cloud Console](https://console.cloud.google.com/)
- OpenAI API Key: [OpenAI Platform](https://platform.openai.com/)
- Hugging Face Token: [Hugging Face](https://huggingface.co/)

#### 🚀 Step 5: Launch the Application
```bash
python app.py
```

The application will start and be available at:
- Local: `http://localhost:7860`
- Network: `http://0.0.0.0:7860` (if configured)

**Troubleshooting:**
- If port 7860 is in use, change it in `app.py` or use:
  ```bash
  python app.py --server_port 7861
  ```
- For firewall issues, ensure the port is open

### ☁️ Method 2: AWS EC2 Deployment

#### 🚀 Step 1: Launch EC2 Instance
```bash
# Recommended instance: t3.large or larger for optimal performance
# Ubuntu 20.04 LTS or Amazon Linux 2
# Minimum 8GB RAM, 20GB storage
```

**Instance Configuration:**
- **Instance Type**: t3.large (2 vCPUs, 8GB RAM) or larger
- **AMI**: Ubuntu 20.04 LTS or Amazon Linux 2
- **Storage**: 20GB+ GP2/GP3 SSD
- **Security Group**: Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 7860 (App)

#### 🛠️ Step 2: Initial Server Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-pip python3.10-venv -y

# Install system dependencies
sudo apt install build-essential libopencv-dev nginx -y

# Install additional tools
sudo apt install git curl wget unzip -y
```

**Optional Security Enhancements:**
```bash
# Set up firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 7860
sudo ufw enable

# Set up fail2ban for security
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

#### 📦 Step 3: Application Deployment
```bash
# Clone and setup application
git clone https://github.com/yourusername/VisoLearn-2.git
cd VisoLearn-2

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env  # Add your API keys
```

#### 🔐 Step 4: Set Up Reverse Proxy (Optional)

Install and configure Nginx:
```bash
sudo apt install nginx
```

Create a configuration file at `/etc/nginx/sites-available/visolearn`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:
```bash
sudo ln -s /etc/nginx/sites-available/visolearn /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

#### 🔒 Step 5: Set Up SSL (Optional but Recommended)

Install Certbot for Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

#### 🚀 Step 6: Run as a Service

Create a systemd service file at `/etc/systemd/system/visolearn.service`:
```ini
[Unit]
Description=VisoLearn-2 Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/VisoLearn-2
Environment="PATH=/home/ubuntu/VisoLearn-2/venv/bin"
ExecStart=/home/ubuntu/VisoLearn-2/venv/bin/python /home/ubuntu/VisoLearn-2/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable visolearn
sudo systemctl start visolearn
sudo systemctl status visolearn
```

### 🐳 Method 3: Docker Deployment (Advanced)

#### 📦 Step 1: Install Docker
```bash
# For Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to the docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 📦 Step 2: Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 7860

CMD ["python", "app.py"]
```

#### 🐳 Step 3: Build and Run Container
```bash
docker build -t visolearn .
docker run -d -p 7860:7860 --env-file .env --name visolearn visolearn
```

#### 🔧 Step 4: Docker Compose (Optional)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  visolearn:
    build: .
    ports:
      - "7860:7860"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 🔧 Configuration Options

### 📝 Environment Variables

**Core Configuration:**
```env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=7860

# API Configuration
GOOGLE_API_KEY=your_key
OPENAI_API_KEY=your_key
GEMINI_API_KEY=your_key

# Application Settings
DEBUG_MODE=False
MAX_SESSIONS=10
IMAGE_CACHE_SIZE=100
```

### 🎨 Customization Options

**Interface Customization:**
- Modify `static/styles.css` for visual styling
- Edit UI components in `ui/interface.py`
- Configure Gradio theme parameters

**Behavior Customization:**
- Adjust difficulty levels in `config.py`
- Modify evaluation thresholds
- Customize feedback messages

## 🐛 Troubleshooting

### 🔴 Common Issues and Solutions

**Issue: Application fails to start**
- **Cause**: Missing dependencies or incorrect Python version
- **Solution**: Check requirements and Python version
  ```bash
  python --version
  pip list
  ```

**Issue: API keys not working**
- **Cause**: Invalid or expired API keys
- **Solution**: Verify keys in `.env` file and check API provider status

**Issue: Images not generating**
- **Cause**: Network issues or API quota exceeded
- **Solution**: Check internet connection and API usage limits

**Issue: Slow performance**
- **Cause**: Insufficient system resources
- **Solution**: Upgrade hardware or reduce concurrent operations

**Issue: Port already in use**
- **Cause**: Another application using port 7860
- **Solution**: Change port in `app.py` or kill conflicting process
  ```bash
  lsof -i :7860
  kill -9 <PID>
  ```

### 📊 Performance Optimization Tips

**Local Development:**
- Use virtual environments to isolate dependencies
- Limit concurrent sessions during development
- Disable unnecessary features for testing

**Production Deployment:**
- Use a production-ready web server (Nginx, Apache)
- Implement proper caching strategies
- Monitor resource usage and scale appropriately
- Use load balancing for high-traffic scenarios

## 📈 Monitoring and Maintenance

### 📊 System Monitoring

**Key Metrics to Monitor:**
- CPU and memory usage
- API call rates and quotas
- Session counts and durations
- Error rates and types

**Monitoring Tools:**
- **System**: `htop`, `glances`, `nmon`
- **Logs**: `journalctl`, `tail -f`
- **Network**: `iftop`, `nethogs`

### 🔄 Update Process

**Updating VisoLearn-2:**
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart application
# For local: Ctrl+C and restart
# For service: sudo systemctl restart visolearn
```

**Version Compatibility:**
- Always check release notes for breaking changes
- Test updates in a staging environment first
- Backup configuration and data before major updates

## 🔒 Security Best Practices

### 🛡️ Application Security

**API Key Management:**
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Implement rate limiting

**Network Security:**
- Use HTTPS for all communications
- Implement proper firewall rules
- Use VPN for remote access
- Regular security audits

### 📁 Data Security

**Data Protection:**
- Encrypt sensitive data at rest
- Implement proper access controls
- Regular data backups
- Secure data disposal procedures

**Privacy Compliance:**
- Follow GDPR and other privacy regulations
- Implement data minimization principles
- Provide clear privacy policies
- Obtain proper consent for data collection

## 🎓 Advanced Configuration

### 🔧 Custom API Endpoints

For advanced users, you can extend the API functionality:

```python
# Example: Custom API endpoint in app.py
from fastapi import FastAPI

api = FastAPI()

@api.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

### 📊 Custom Analytics

Extend analytics capabilities:

```python
# Example: Custom analytics in utils/analytics.py
def custom_analytics(session_data):
    # Implement custom tracking logic
    return analytics_results
```

### 🤖 Custom AI Models

Integrate additional AI models:

```python
# Example: Custom model integration in models/custom.py
def custom_model_inference(prompt):
    # Implement custom AI logic
    return model_output
```

## 📚 Additional Resources

### 📖 Documentation Links
- [Official Documentation](https://visolearn.org/docs)
- [API Reference](https://visolearn.org/api)
- [Developer Guide](https://visolearn.org/developers)

### 💬 Community Support
- [GitHub Issues](https://github.com/visolearn/visolearn-2/issues)
- [Discussion Forum](https://forum.visolearn.org)
- [Slack Community](https://slack.visolearn.org)

### 🎓 Learning Resources
- [Autism Education Research](https://autism-research.org)
- [AI in Education](https://ai-education.org)
- [Gradio Documentation](https://gradio.app/docs)
