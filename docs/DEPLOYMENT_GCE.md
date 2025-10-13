# Google Compute Engine Deployment Guide

This guide walks you through deploying the Trump Truth Social Trading Monitor on Google Compute Engine (GCE).

## Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed (optional but recommended)
- Gmail account for email notifications (or other SMTP)

## Step 1: Create GCE Instance

### Option A: Using GCP Console

1. Go to [GCP Console](https://console.cloud.google.com/)
2. Navigate to **Compute Engine > VM Instances**
3. Click **Create Instance**
4. Configure:
   - **Name**: `trump-trader-monitor`
   - **Region**: Choose closest to you (e.g., `us-central1`)
   - **Machine type**: `e2-micro` (FREE tier eligible!)
   - **Boot disk**: 
     - OS: **Ubuntu 22.04 LTS**
     - Size: **10 GB** (sufficient)
   - **Firewall**: Allow HTTP/HTTPS (optional)
5. Click **Create**

### Option B: Using gcloud CLI

```bash
gcloud compute instances create trump-trader-monitor \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=10GB \
    --tags=http-server,https-server
```

## Step 2: Connect to Instance

```bash
gcloud compute ssh trump-trader-monitor --zone=us-central1-a
```

Or use the **SSH** button in the GCP Console.

## Step 3: Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv git

# Install system dependencies
sudo apt-get install -y build-essential python3-dev
```

## Step 4: Clone or Upload Project

### Option A: Clone from Git (if you have a repository)

```bash
cd ~
git clone https://github.com/yourusername/trump_trader.git
cd trump_trader
```

### Option B: Upload Files

From your local machine:

```bash
gcloud compute scp --recurse /local/path/to/trump_trader \
    trump-trader-monitor:~/ --zone=us-central1-a
```

Then on the server:
```bash
cd ~/trump_trader
```

## Step 5: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Step 6: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add your configuration:

```bash
# Google Gemini API Key (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# Email Notification Settings (REQUIRED for production)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
RECIPIENT_EMAIL=alerts@yourdomain.com

# SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Monitoring settings
CHECK_INTERVAL_SECONDS=60
```

**Getting Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (custom name)"
3. Name it "Trump Trader Monitor"
4. Copy the 16-character password
5. Use this as `SENDER_PASSWORD`

Save and exit (Ctrl+X, then Y, then Enter)

## Step 7: Test the Setup

```bash
# Run all tests
python run_tests.py

# Or test components individually
python tests/test_gemini.py         # Test Gemini API
python tests/test_email.py          # Test email notifications
python tests/test_ai_analysis.py    # Test AI analysis
python tests/test_system.py         # Test full system
```

## Step 8: Create Systemd Service (Run as Daemon)

```bash
# Create service file
sudo nano /etc/systemd/system/trump-trader.service
```

Add this content:

```ini
[Unit]
Description=Trump Truth Social Trading Monitor
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/trump_trader
Environment="PATH=/home/YOUR_USERNAME/trump_trader/venv/bin"
ExecStart=/home/YOUR_USERNAME/trump_trader/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=append:/home/YOUR_USERNAME/trump_trader/logs/output.log
StandardError=append:/home/YOUR_USERNAME/trump_trader/logs/error.log

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual username** (usually your GCP username).

Find your username:
```bash
whoami
```

## Step 9: Create Logs Directory

```bash
mkdir -p ~/trump_trader/logs
```

## Step 10: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable trump-trader

# Start service
sudo systemctl start trump-trader

# Check status
sudo systemctl status trump-trader
```

## Step 11: Monitor Logs

```bash
# View live logs
tail -f ~/trump_trader/logs/output.log

# View errors
tail -f ~/trump_trader/logs/error.log

# View systemd journal
sudo journalctl -u trump-trader -f
```

## Service Management Commands

```bash
# Start service
sudo systemctl start trump-trader

# Stop service
sudo systemctl stop trump-trader

# Restart service
sudo systemctl restart trump-trader

# View status
sudo systemctl status trump-trader

# Disable (don't start on boot)
sudo systemctl disable trump-trader
```

## Step 12: Verify It's Working

1. Check logs:
   ```bash
   tail -n 50 ~/trump_trader/logs/output.log
   ```

2. You should see:
   ```
   [OK] Google Gemini AI enabled for analysis
   [OK] Email notifications enabled
   [OK] Loaded state: X posts processed
   Testing connection to trumpstruth.org...
   [2025-XX-XX XX:XX:XX] Checking for new posts...
   ```

3. Check data files:
   ```bash
   ls -lh ~/trump_trader/data/
   ```

4. Wait for a new post and check your email!

## Cost Estimate

### GCE e2-micro Instance (FREE TIER)

- **First 720 hours/month**: FREE
- **After free tier**: ~$7/month
- **Network egress**: First 1GB/month free

### Total Cost: $0 - $7/month

(Free if you stay within free tier limits)

## Firewall & Security

### Restrict SSH Access (Recommended)

```bash
# Allow SSH only from your IP
gcloud compute firewall-rules create allow-ssh-from-my-ip \
    --allow tcp:22 \
    --source-ranges YOUR_IP_ADDRESS/32 \
    --target-tags trump-trader
```

### Update Firewall Tags

```bash
gcloud compute instances add-tags trump-trader-monitor \
    --tags trump-trader \
    --zone us-central1-a
```

## Backup & Recovery

### Automated Backups

```bash
# Create backup script
nano ~/backup.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf ~/backups/trump_trader_$DATE.tar.gz \
    ~/trump_trader/data/ \
    ~/trump_trader/.env
find ~/backups/ -name "trump_trader_*.tar.gz" -mtime +7 -delete
```

Make executable and schedule:
```bash
chmod +x ~/backup.sh
mkdir -p ~/backups

# Add to crontab (daily at 2 AM)
crontab -e
```

Add line:
```
0 2 * * * /home/YOUR_USERNAME/backup.sh
```

## Troubleshooting

### Service Won't Start

```bash
# Check for errors
sudo journalctl -u trump-trader -n 100

# Check Python path
which python
/home/YOUR_USERNAME/trump_trader/venv/bin/python --version

# Test manually
cd ~/trump_trader
source venv/bin/activate
python main.py
```

### Email Not Sending

```bash
# Test email separately
cd ~/trump_trader
source venv/bin/activate
python email_notifier.py
```

Check:
- Gmail App Password is correct
- "Less secure app access" is NOT needed (use App Password)
- SENDER_EMAIL matches the Gmail account

### Connection Issues

```bash
# Test internet
ping -c 3 google.com

# Test trumpstruth.org
curl -I https://trumpstruth.org

# Check DNS
nslookup trumpstruth.org
```

### High Memory Usage

```bash
# Check memory
free -h

# If needed, add swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Updating the Code

```bash
# Stop service
sudo systemctl stop trump-trader

# Update code (if using git)
cd ~/trump_trader
git pull

# Or upload new files
# (from local machine)
gcloud compute scp --recurse /local/path/to/trump_trader \
    trump-trader-monitor:~/ --zone=us-central1-a

# Reinstall dependencies (if requirements.txt changed)
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl start trump-trader
```

## Monitoring & Alerts

### Check if Service is Running

```bash
# Quick check
systemctl is-active trump-trader

# Detailed status
sudo systemctl status trump-trader
```

### Email Alerts on Service Failure

Edit service file:
```bash
sudo nano /etc/systemd/system/trump-trader.service
```

Add under `[Service]`:
```ini
OnFailure=status-email-user@%n.service
```

## Best Practices

1. **Regular Updates**: Update system packages weekly
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Monitor Disk Space**:
   ```bash
   df -h
   du -sh ~/trump_trader/data/
   ```

3. **Rotate Logs**: The service automatically appends logs
   ```bash
   # Clean old logs manually or use logrotate
   sudo apt-get install logrotate
   ```

4. **Check API Quotas**: Monitor Gemini API usage at https://aistudio.google.com/

5. **Backup `.env` file**: Store securely outside the instance

## Production Checklist

- [ ] GCE instance created and running
- [ ] Python environment set up
- [ ] Dependencies installed
- [ ] `.env` file configured with all keys
- [ ] Email notifications tested
- [ ] Systemd service created and enabled
- [ ] Logs directory created
- [ ] Service starts automatically on boot
- [ ] Backup script configured
- [ ] Firewall rules configured
- [ ] Email alerts working
- [ ] Monitoring in place

## Support

If you encounter issues:

1. Check logs: `tail -f ~/trump_trader/logs/output.log`
2. Check errors: `tail -f ~/trump_trader/logs/error.log`
3. Test components individually
4. Verify API keys and credentials

## Next Steps

Your monitor is now running 24/7 on Google Cloud! You'll receive email alerts whenever Trump posts something market-relevant.

**Enjoy your automated trading intelligence! 📈🤖**

