#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="bert-llm-chat-app-backend"
TAG="${1:-local-test}"  # Utilise le premier argument ou "local-test" par défaut

echo "🔧 Configuration:"
echo "  Region: $AWS_REGION"
echo "  Repository: $ECR_REPOSITORY"
echo "  Tag: $TAG"
echo ""

# Récupérer l'Account ID
echo "🔑 Récupération de l'AWS Account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo "  Account ID: $AWS_ACCOUNT_ID"
echo "  Registry: $ECR_REGISTRY"
echo ""

# Authentification ECR
echo "🔐 Authentification à ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REGISTRY
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "./backend" ]; then
  echo "❌ Erreur: Le répertoire ./backend n'existe pas."
  echo "   Veuillez exécuter ce script depuis la racine du projet."
  exit 1
fi

# # Build de l'image
# echo "🏗️  Build de l'image Docker..."
# echo "  Context: ./backend"
# echo "  Dockerfile: ./backend/Dockerfile"
# echo "  Platform: linux/amd64"
# echo ""
docker buildx build \
  --platform linux/arm64 \
  --file ./backend/Dockerfile \
  --tag $ECR_REPOSITORY:$TAG \
  ./backend

# echo ""

# Tag pour ECR
# echo "🏷️  Tag de l'image pour ECR..."
# docker tag $ECR_REPOSITORY:$TAG $ECR_REGISTRY/$ECR_REPOSITORY:$TAG
# echo "  Local tag: $ECR_REPOSITORY:$TAG"
# echo "  ECR tag: $ECR_REGISTRY/$ECR_REPOSITORY:$TAG"
# echo ""

# # Push vers ECR
# echo "📤 Push vers ECR..."
# docker push $ECR_REGISTRY/$ECR_REPOSITORY:$TAG
# echo ""

# # Résumé
# echo "✅ Image pushée avec succès!"
# echo ""
# echo "📝 Résumé:"
# echo "  Image URI: $ECR_REGISTRY/$ECR_REPOSITORY:$TAG"
# echo ""
# echo "💡 Pour déployer cette image sur App Runner, vous pouvez:"
# echo "   1. Aller dans la console AWS App Runner"
# echo "   2. Sélectionner votre service: bert-llm-chat-app-backend-service"
# echo "   3. Cliquer sur 'Deploy' et utiliser cette image URI"
# echo ""
# echo "   Ou utiliser la commande AWS CLI:"
# echo "   aws apprunner update-service \\"
# echo "     --service-arn <YOUR_SERVICE_ARN> \\"
# echo "     --source-configuration '{\"ImageRepository\": {\"ImageIdentifier\": \"$ECR_REGISTRY/$ECR_REPOSITORY:$TAG\", \"ImageRepositoryType\": \"ECR\"}}' \\"
# echo "     --region $AWS_REGION"

