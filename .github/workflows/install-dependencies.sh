#!/bin/bash
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail

# install wget
sudo apt install -y wget

# install dotnet CLI
sudo apt-get update
sudo apt-get install wget
wget -O - https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.asc.gpg
sudo mv microsoft.asc.gpg /etc/apt/trusted.gpg.d/
wget https://packages.microsoft.com/config/debian/9/prod.list
sudo mv prod.list /etc/apt/sources.list.d/microsoft-prod.list
sudo chown root:root /etc/apt/trusted.gpg.d/microsoft.asc.gpg
sudo chown root:root /etc/apt/sources.list.d/microsoft-prod.list

sudo apt-get install -y apt-transport-https && \
sudo apt-get update && \
sudo apt-get install -y dotnet-sdk-6.0
echo "✅ dotnet installed"

# The latest version of the ubuntu image has homebrew installed on image but not added to path
# See release notes for details: https://github.com/actions/runner-images/blob/releases/ubuntu20/20220922/images/linux/Ubuntu2004-Readme.md#ubuntu-20045-lts
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# install kubectl
brew install kubernetes-cli@1.25
echo "✅ kubectl installed"

brew install helm
echo "✅ helm installed"

# install go
wget https://golang.org/dl/go1.18.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.18.linux-amd64.tar.gz
echo 'export GOPATH=$HOME/go' >> ~/.profile
echo 'export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin' >> ~/.profile
source ~/.profile
echo "✅ golang installed"

# install build-essential (gcc, used for go test)
sudo apt install -y build-essential

# install addlicense
go install github.com/google/addlicense@latest
sudo ln -s $HOME/go/bin/addlicense /bin

# install build-essential (gcc, used for go test)
sudo apt install -y build-essential

# install skaffold
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && \
chmod +x skaffold && \
sudo mv skaffold /usr/local/bin
echo "✅ skaffold installed"
