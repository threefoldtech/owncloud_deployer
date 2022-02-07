# Owncloud freemium deployment helmchart installation guide

## Requirments

- kubernetes cluster with ingress nginx controller
- domain

## Installation

### nginx cluster installation and cert manager

- install nginx controller

    ```bash
    helm upgrade --install ingress-nginx ingress-nginx \
      --repo https://kubernetes.github.io/ingress-nginx \
      --namespace ingress-nginx --create-namespace
    ```

- install cert manager

    ```bash
    helm repo add jetstack https://charts.jetstack.io
    helm repo update
    helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --set installCRDs=true
    ```

- apply certificate

    ```bash
    kubectl create -f prod_issuer.yaml
    ```

- install chart

    ```bash
    helm install -f values.yaml owncloud . --set ingress.host="free.3botmain.grid.tf" --set env.MNEMONICS="" --set env.NETWORK="dev" --set env.CHAIN_URL="wss://tfchain.dev.grid.tf/ws" --set env.ALERT_EMAIL="waleed.hammam@gmail.com" --set env.email_host="smtp.gmail.com" --set env.email_port=587 --set env.email_username="" --set env.email_password="" --set env.ADMINS="['waleedhammam.3bot']"
    ```
