# HubSpot MCP Server - Guide de Déploiement Production

Ce guide explique comment déployer le serveur MCP HubSpot en mode SSE sur Kubernetes en utilisant la chart Helm [app-component](https://gitlab.com/keltiotechnology/helm-charts/-/tree/master/app-component?ref_type=heads).

## 📋 Prérequis

### Outils Requis
- `kubectl` configuré avec accès au cluster Kubernetes
- `helm` v3.x installé
- `docker` pour construire les images
- Accès à un registry Docker (ex: Docker Hub, ECR, GCR)

### Infrastructure Kubernetes
- **cert-manager** installé et configuré
- **ingress-nginx** ou autre contrôleur d'ingress
- **External Secrets Operator** installé
- Cluster Kubernetes v1.19+

## 🔐 **Authentification et Sécurité**

Le serveur MCP HubSpot inclut désormais un système d'authentification par header pour sécuriser l'accès à l'API en mode SSE.

### **Configuration de l'Authentification**

#### **Variables d'Environnement**
- **`MCP_AUTH_KEY`** : Clé d'API pour l'authentification (optionnel)
- **`MCP_AUTH_HEADER`** : Nom du header d'authentification (défaut: `X-API-Key`)

#### **Comportement de l'Authentification**
- **Authentification désactivée** : Si `MCP_AUTH_KEY` n'est pas défini
- **Authentification activée** : Si `MCP_AUTH_KEY` est défini
- **Endpoints exemptés** : `/health` et `/ready` ne nécessitent pas d'authentification
- **Header case-insensitive** : Le nom du header n'est pas sensible à la casse

#### **Exemple de Configuration**
```bash
# Authentification avec header personnalisé
export MCP_AUTH_KEY="mon-secret-super-securise-123"
export MCP_AUTH_HEADER="Authorization"

# Authentification avec header par défaut
export MCP_AUTH_KEY="ma-cle-api-securisee"
# MCP_AUTH_HEADER sera automatiquement "X-API-Key"
```

#### **Utilisation Client**
```bash
# Avec X-API-Key (défaut)
curl -H "X-API-Key: mon-secret-super-securise-123" https://mcp-hubspot.yourdomain.com/sse

# Avec header personnalisé
curl -H "Authorization: mon-secret-super-securise-123" https://mcp-hubspot.yourdomain.com/sse

# Les endpoints de santé ne nécessitent pas d'authentification
curl https://mcp-hubspot.yourdomain.com/health
curl https://mcp-hubspot.yourdomain.com/ready
```

#### **Réponses d'Authentification**
```bash
# Authentification réussie : 200 OK + contenu normal
# Authentification échouée : 401 Unauthorized
{
  "error": "Unauthorized",
  "message": "Invalid API key"
}
```

## 🚀 Processus de Déploiement

### Étape 1: Configuration de l'Environnement

Configurez les variables d'environnement :

```bash
export NAMESPACE="production"
export DOMAIN="mcp-hubspot.yourdomain.com"
export IMAGE_REGISTRY="your-registry.com"
export IMAGE_TAG="1.0.0"
export HUBSPOT_API_KEY="your-hubspot-api-key"
export MCP_AUTH_KEY="your-mcp-authentication-key"
```

### Étape 2: Construction de l'Image Docker

```bash
# Construction locale
docker build -t ${IMAGE_REGISTRY}/hubspot-mcp-server:${IMAGE_TAG} .

# Push vers le registry
docker push ${IMAGE_REGISTRY}/hubspot-mcp-server:${IMAGE_TAG}
```

### Étape 3: Configuration des Secrets

#### Avec External Secrets Operator (AWS Secrets Manager)

1. Stockez vos clés dans AWS Secrets Manager :
```bash
# Clé API HubSpot
aws secretsmanager create-secret \
    --name "production/hubspot/api-key" \
    --description "HubSpot API Key for MCP Server" \
    --secret-string "$HUBSPOT_API_KEY"

# Clé d'authentification MCP
aws secretsmanager create-secret \
    --name "production/hubspot/mcp-auth-key" \
    --description "MCP Authentication Key" \
    --secret-string "$MCP_AUTH_KEY"
```

2. Le SecretStore et ExternalSecret seront créés automatiquement par le script de déploiement.

#### Avec Secret Kubernetes Manuel

```bash
kubectl create secret generic hubspot-mcp-secrets \
    --from-literal=hubspot-api-key="$HUBSPOT_API_KEY" \
    --from-literal=mcp-auth-key="$MCP_AUTH_KEY" \
    --namespace="$NAMESPACE"
```

### Étape 4: Configuration du Certificat SSL

Le ClusterIssuer Let's Encrypt sera créé automatiquement :

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: devops@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod-private-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Étape 5: Déploiement avec Helm

#### Automatique avec le Script

```bash
# Rendre le script exécutable
chmod +x deploy/scripts/deploy.sh

# Déploiement complet avec authentification
DOMAIN="mcp-hubspot.yourdomain.com" \
IMAGE_REGISTRY="your-registry.com" \
IMAGE_TAG="1.0.0" \
./deploy/scripts/deploy.sh deploy
```

#### Manuel avec Helm

```bash
# Ajouter le repository Keltio
helm repo add keltio https://gitlab.com/keltiotechnology/helm-charts
helm repo update

# Mettre à jour les dépendances
helm dependency update ./deploy

# Déployer
helm upgrade --install hubspot-mcp-server ./deploy \
    --namespace production \
    --create-namespace \
    --values ./deploy/values-production.yaml \
    --set image.repository="${IMAGE_REGISTRY}/hubspot-mcp-server" \
    --set image.tag="${IMAGE_TAG}" \
    --set ingress.hosts[0].host="${DOMAIN}" \
    --set ingress.tls[0].hosts[0]="${DOMAIN}" \
    --wait \
    --timeout=600s
```

## 🔍 Vérification du Déploiement

### Vérifier les Pods
```bash
kubectl get pods -n production -l app.kubernetes.io/name=hubspot-mcp-server
```

### Vérifier les Services
```bash
kubectl get services -n production -l app.kubernetes.io/name=hubspot-mcp-server
```

### Vérifier l'Ingress
```bash
kubectl get ingress -n production
```

### Test des Endpoints de Santé
```bash
# Health check (sans authentification)
curl -f https://${DOMAIN}/health

# Readiness check (sans authentification)
curl -f https://${DOMAIN}/ready

# Endpoint SSE (avec authentification si activée)
curl -H "X-API-Key: ${MCP_AUTH_KEY}" -f https://${DOMAIN}/sse
```

### **Test de l'Authentification**
```bash
# Test avec bonne clé d'authentification
curl -H "X-API-Key: ${MCP_AUTH_KEY}" https://${DOMAIN}/sse
# Retour attendu : Connexion SSE établie

# Test avec mauvaise clé
curl -H "X-API-Key: wrong-key" https://${DOMAIN}/sse
# Retour attendu : {"error": "Unauthorized", "message": "Invalid API key"}

# Test sans header d'authentification
curl https://${DOMAIN}/sse
# Retour attendu : {"error": "Unauthorized", "message": "Invalid API key"}
```

## 📊 Monitoring et Logs

### Consulter les Logs
```bash
kubectl logs -n production -l app.kubernetes.io/name=hubspot-mcp-server -f
```

### Logs d'Authentification
Les logs incluront des informations sur l'état de l'authentification :
```
[INFO] Authentication enabled with header: X-API-Key
[WARNING] Authentication disabled - MCP_AUTH_KEY not set
```

### Monitoring avec Prometheus (si activé)
L'endpoint `/metrics` est exposé pour Prometheus si le monitoring est activé dans les values.

## 🔄 Gestion des Versions

### Mise à Jour
```bash
# Nouvelle version
IMAGE_TAG="1.1.0" ./deploy/scripts/deploy.sh deploy
```

### Rollback
```bash
# Rollback à la version précédente
./deploy/scripts/deploy.sh rollback

# Rollback à une version spécifique
./deploy/scripts/deploy.sh rollback 2
```

## 🧹 Nettoyage

### Suppression Complète
```bash
./deploy/scripts/deploy.sh cleanup
```

### Suppression Manuelle
```bash
helm uninstall hubspot-mcp-server -n production
kubectl delete namespace production
```

## ⚙️ Configuration Avancée

### Personnalisation des Values

Modifiez `deploy/values-production.yaml` pour personnaliser :

- **Ressources** : CPU/Mémoire requests/limits
- **Réplicas** : Nombre d'instances
- **Ingress** : Configuration SSL/TLS
- **Monitoring** : Métriques Prometheus
- **Network Policies** : Règles réseau
- **Security Context** : Contexte de sécurité
- **Authentification** : Configuration des clés et headers

### Variables d'Environnement Disponibles

| Variable | Description | Défaut | Requis |
|----------|-------------|--------|---------|
| `MODE` | Mode de communication (sse/stdio) | `sse` | Non |
| `HOST` | Host d'écoute | `0.0.0.0` | Non |
| `PORT` | Port d'écoute | `8080` | Non |
| `HUBSPOT_API_KEY` | Clé API HubSpot | - | **Oui** |
| `MCP_AUTH_KEY` | Clé d'authentification MCP | - | Non |
| `MCP_AUTH_HEADER` | Nom du header d'authentification | `X-API-Key` | Non |

### Configuration Multi-Environnement

Créez des fichiers de values séparés :
- `values-development.yaml` (authentification optionnelle)
- `values-staging.yaml` (authentification recommandée)
- `values-production.yaml` (authentification obligatoire)

## 🚨 Troubleshooting

### Problèmes Courants

#### **Problèmes d'Authentification**

##### Erreur 401 Unauthorized
```bash
# Vérifier la configuration du secret
kubectl get secret hubspot-mcp-secrets -n production -o yaml

# Vérifier les variables d'environnement du pod
kubectl describe pod -n production -l app.kubernetes.io/name=hubspot-mcp-server

# Vérifier les logs pour les erreurs d'authentification
kubectl logs -n production -l app.kubernetes.io/name=hubspot-mcp-server | grep -i auth
```

##### Authentification Non Activée
```bash
# Vérifier que MCP_AUTH_KEY est défini
kubectl exec -n production deployment/hubspot-mcp-server -- env | grep MCP_AUTH_KEY

# Vérifier les logs de démarrage
kubectl logs -n production -l app.kubernetes.io/name=hubspot-mcp-server | grep -E "(Authentication|MCP_AUTH)"
```

#### Pod en CrashLoopBackOff
```bash
# Vérifier les logs
kubectl describe pod -n production -l app.kubernetes.io/name=hubspot-mcp-server
kubectl logs -n production -l app.kubernetes.io/name=hubspot-mcp-server --previous
```

#### Problème de Secret
```bash
# Vérifier le secret
kubectl get secret hubspot-mcp-secrets -n production -o yaml
```

#### Problème de Certificat
```bash
# Vérifier les certificats
kubectl get certificate -n production
kubectl describe certificate hubspot-mcp-tls -n production
```

#### Problème d'Ingress
```bash
# Vérifier l'ingress
kubectl describe ingress -n production
```

### Debug du Serveur MCP

#### Test en Local
```bash
# Test du container en local avec authentification
docker run -p 8080:8080 \
    -e HUBSPOT_API_KEY="your-key" \
    -e MCP_AUTH_KEY="test-auth-key" \
    ${IMAGE_REGISTRY}/hubspot-mcp-server:${IMAGE_TAG}
```

#### Port-Forward pour Debug
```bash
# Accès direct au pod
kubectl port-forward -n production deployment/hubspot-mcp-server 8080:8080

# Test direct avec authentification
curl -H "X-API-Key: your-auth-key" http://localhost:8080/sse

# Test direct sans authentification (devrait échouer)
curl http://localhost:8080/sse
```

## 📚 Architecture

### Composants Déployés

1. **Deployment** : 2 réplicas par défaut avec health checks
2. **Service** : Exposition interne ClusterIP
3. **Ingress** : Exposition externe avec SSL/TLS
4. **HPA** : Auto-scaling basé sur CPU/Mémoire
5. **NetworkPolicy** : Règles de sécurité réseau
6. **ServiceAccount** : Compte de service dédié
7. **ExternalSecret** : Gestion sécurisée des secrets
8. **AuthenticationMiddleware** : Middleware d'authentification ASGI

### Endpoints Exposés

- `/sse` : Endpoint principal MCP en mode SSE (**authentification requise**)
- `/health` : Health check pour Kubernetes (**pas d'authentification**)
- `/ready` : Readiness check pour Kubernetes (**pas d'authentification**)
- `/messages/` : Messages MCP internes (**authentification requise**)

## 🔒 Sécurité

### Bonnes Pratiques Appliquées

- ✅ Container non-root
- ✅ Security context restrictif
- ✅ Network policies
- ✅ Secrets externalisés
- ✅ TLS/SSL obligatoire
- ✅ Resource limits
- ✅ Health checks
- ✅ **Authentification par header API**
- ✅ **Endpoints de santé exemptés d'authentification**
- ✅ **Case-insensitive header matching**

### **Recommandations de Sécurité pour l'Authentification**

#### **Génération de Clés Sécurisées**
```bash
# Générer une clé d'authentification sécurisée
openssl rand -base64 32

# Ou avec uuidgen
uuidgen | tr -d '-' | tr '[:upper:]' '[:lower:]'
```

#### **Rotation des Clés**
```bash
# Mise à jour de la clé d'authentification
kubectl patch secret hubspot-mcp-secrets -n production \
    --type='json' \
    -p='[{"op": "replace", "path": "/data/mcp-auth-key", "value":"'$(echo -n "nouvelle-cle" | base64)'"}]'

# Redémarrer les pods pour charger la nouvelle clé
kubectl rollout restart deployment/hubspot-mcp-server -n production
```

#### **Audit et Monitoring**
- Surveillez les tentatives d'authentification échouées dans les logs
- Configurez des alertes sur les erreurs 401
- Utilisez des clés d'authentification différentes par environnement
- Activez l'audit Kubernetes pour tracer les accès aux secrets

### Recommandations Supplémentaires

- Utilisez des images scannées pour les vulnérabilités
- Activez Pod Security Standards
- Configurez RBAC approprié
- Surveillez les logs d'accès et d'authentification
- Mettez à jour régulièrement les dépendances
- **Activez toujours l'authentification en production**
- **Utilisez des clés d'authentification complexes et uniques**
- **Stockez les clés dans un gestionnaire de secrets externe**

---

Pour plus d'informations sur la chart app-component, consultez : https://gitlab.com/keltiotechnology/helm-charts/-/tree/master/app-component 