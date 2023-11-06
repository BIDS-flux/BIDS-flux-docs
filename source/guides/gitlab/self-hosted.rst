# Setting up a self-hosted Gitlab instance

## Prerequisites

- A server with a public IP address
- A domain name pointing to the server
- A user with sudo privileges


## Installation

### Install Docker

```bash
sudo apt-get update
sudo apt-get install -y docker.io
```

### Install Docker Compose

```bash
sudo apt-get install -y docker-compose
```

### Install Gitlab

```bash
sudo mkdir -p /srv/gitlab/config /srv/gitlab/data /srv/gitlab/logs
sudo chown -R 1000:1000 /srv/gitlab
sudo chmod -R g+rwX /srv/gitlab
```

```bash
sudo vim /srv/gitlab/docker-compose.yml
```
