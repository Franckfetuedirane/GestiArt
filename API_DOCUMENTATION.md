# Documentation de l'API REST GestiArt

Bienvenue dans la documentation de l'API REST pour GestiArt, une application de gestion d'activités artisanales. Cette API permet de gérer les artisans, les produits, les ventes et les statistiques.

## Fonctionnalités principales

- **Authentification** : Inscription et connexion sécurisée avec JWT
- **Gestion des artisans** : Profils complets avec coordonnées
- **Catalogue produits** : Gestion des produits par artisan
- **Gestion des ventes** : Suivi des ventes avec lignes de vente
- **Statistiques** : Tableaux de bord et rapports

## Base URL

```
http://127.0.0.1:8000/api/
```

## Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification.

### Obtenir un token

```http
POST /api/token/
```

**Body (JSON):**
```json
{
    "email": "utilisateur@example.com",
    "password": "votremotdepasse"
}
```

**Réponse (200 OK):**
```json
{
    "refresh": "votre_refresh_token",
    "access": "votre_access_token"
}
```

### Rafraîchir un token

```http
POST /api/token/refresh/
```

**Body (JSON):**
```json
{
    "refresh": "votre_refresh_token"
}
```

## Endpoints

### Artisans

#### Lister tous les artisans
```http
GET /api/artisans/
```

#### Créer un artisan
```http
POST /api/artisans/
```

**Headers:**
```
Authorization: Bearer votre_access_token
Content-Type: application/json
```

### Produits

#### Lister tous les produits
```http
GET /api/produits/
```

#### Créer un produit
```http
POST /api/produits/
```

### Ventes

#### Lister toutes les ventes
```http
GET /api/ventes/
```

#### Créer une vente
```http
POST /api/ventes/
```

#### Obtenir les statistiques des ventes
```http
GET /api/ventes/stats/
```

**Réponse (200 OK):**
```json
{
    "total_ventes": 42,
    "montant_total": 1250.75,
    "periode": {
        "debut": "2025-09-01T00:00:00Z",
        "fin": "2025-10-01T00:00:00Z"
    },
    "status": "success"
}
```

## Exemple d'utilisation avec cURL

```bash
# Obtenir un token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"utilisateur@example.com","password":"votremotdepasse"}'

# Lister les ventes avec token
curl http://127.0.0.1:8000/api/ventes/ \
  -H "Authorization: Bearer votre_access_token"
```

## Codes de statut HTTP

- **200 OK** : Requête réussie
- **201 Created** : Ressource créée avec succès
- **400 Bad Request** : Données de requête invalides
- **401 Unauthorized** : Authentification requise
- **403 Forbidden** : Accès refusé
- **404 Not Found** : Ressource non trouvée
- **500 Internal Server Error** : Erreur serveur

## Gestion des erreurs

Les erreurs sont renvoyées au format JSON avec un message descriptif :

```json
{
    "error": "Message d'erreur détaillé",
    "status": "error"
}
