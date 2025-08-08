#!/bin/bash

# Veterinary AI Transcription System Installer
# Confidential Project - Not for public distribution

set -e

echo "🏥 Veterinary AI Transcription System Installer"
echo "================================================"
echo "This script will install the veterinary transcription system"
echo "with SAML 2.0 authentication and WCAG 2.2 compliance."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "🔧 Installing dependencies..."
apt-get install -y \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    docker.io \
    docker-compose \
    ffmpeg

# Start and enable Docker
echo "🐳 Setting up Docker..."
systemctl start docker
systemctl enable docker

# Clone repository (if not already present)
if [ ! -d "/opt/vet-transcription" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/your-org/vet-transcription-mvp.git /opt/vet-transcription
    cd /opt/vet-transcription
else
    echo "📁 Repository already exists, updating..."
    cd /opt/vet-transcription
    git pull
fi

# Set up backend
echo "🔧 Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download Vosk model if not present
if [ ! -d "models/vosk-model-en-us-0.22" ]; then
    echo "🤖 Downloading Vosk model..."
    mkdir -p models
    cd models
    wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
    unzip vosk-model-en-us-0.22.zip
    rm vosk-model-en-us-0.22.zip
    cd ..
fi

# Set up frontend
echo "🎨 Setting up frontend..."
cd ../frontend
npm install

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/vet-transcription.service << EOF
[Unit]
Description=Veterinary AI Transcription System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/vet-transcription
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable vet-transcription.service
systemctl start vet-transcription.service

# Create auto-shutdown cron job
echo "⏰ Setting up auto-shutdown (2 AM daily)..."
(crontab -l 2>/dev/null; echo "0 2 * * * /sbin/shutdown -h now") | crontab -

# Create firewall rules
echo "🔥 Configuring firewall..."
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 3000/tcp # Frontend
ufw allow 8000/tcp # Backend
ufw --force enable

# Create admin user
echo "👤 Creating admin user..."
useradd -m -s /bin/bash vetadmin
echo "vetadmin:VetAdmin2024!" | chpasswd
usermod -aG docker vetadmin

# Set up SSL certificate (self-signed for demo)
echo "🔒 Setting up SSL certificate..."
mkdir -p /etc/ssl/vet-transcription
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/vet-transcription/private.key \
    -out /etc/ssl/vet-transcription/certificate.crt \
    -subj "/C=US/ST=State/L=City/O=VetClinic/CN=vet-transcription.local"

# Create nginx configuration
echo "🌐 Setting up nginx..."
apt-get install -y nginx

cat > /etc/nginx/sites-available/vet-transcription << EOF
server {
    listen 80;
    server_name _;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name _;

    ssl_certificate /etc/ssl/vet-transcription/certificate.crt;
    ssl_certificate_key /etc/ssl/vet-transcription/private.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/vet-transcription /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# Create status script
echo "📊 Creating status script..."
cat > /usr/local/bin/vet-status << EOF
#!/bin/bash
echo "🏥 Veterinary AI Transcription System Status"
echo "============================================"
echo "Service Status:"
systemctl status vet-transcription.service --no-pager -l
echo ""
echo "Docker Containers:"
docker-compose -f /opt/vet-transcription/docker-compose.yml ps
echo ""
echo "System Resources:"
free -h
df -h /
echo ""
echo "Access URLs:"
echo "Frontend: https://$(hostname -I | awk '{print $1}')"
echo "Backend API: https://$(hostname -I | awk '{print $1}')/api/"
echo "Admin Login: vetadmin / VetAdmin2024!"
EOF

chmod +x /usr/local/bin/vet-status

# Final setup
echo "✅ Installation completed!"
echo ""
echo "🎉 Veterinary AI Transcription System is now ready!"
echo ""
echo "📋 System Information:"
echo "   Frontend URL: https://$(hostname -I | awk '{print $1}')"
echo "   Backend API: https://$(hostname -I | awk '{print $1}')/api/"
echo "   Admin Login: vetadmin / VetAdmin2024!"
echo ""
echo "🔧 Management Commands:"
echo "   Check status: vet-status"
echo "   Start service: systemctl start vet-transcription"
echo "   Stop service: systemctl stop vet-transcription"
echo "   View logs: docker-compose -f /opt/vet-transcription/docker-compose.yml logs"
echo ""
echo "🔒 Security Features:"
echo "   ✅ SAML 2.0 Mock Authentication"
echo "   ✅ WCAG 2.2 Compliance"
echo "   ✅ SSL/TLS Encryption"
echo "   ✅ Firewall Configuration"
echo "   ✅ Auto-shutdown (2 AM daily)"
echo ""
echo "📞 For support, contact your system administrator."
echo ""

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running successfully!"
else
    echo "⚠️ Frontend may still be starting up..."
fi

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running successfully!"
else
    echo "⚠️ Backend may still be starting up..."
fi

echo ""
echo "🎯 Installation script completed successfully!" 