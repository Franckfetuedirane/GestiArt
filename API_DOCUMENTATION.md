# Documentation de l'API REST GestiArt

Bienvenue dans la documentation de l'API REST pour GestiArt, une application de gestion d'activités artisanales. Cette API permet de gérer les artisans, les produits, les ventes et les statistiques.

## Fonctionnalités principales

- **Authentification** : Inscription et connexion sécurisée avec JWT
- **Gestion des artisans** : Profils complets avec coordonnées
- **Catalogue produits** : Gestion des produits par artisan avec suivi des stocks
- **Gestion des ventes** : Suivi des ventes avec lignes de vente et mise à jour automatique des stocks
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

#### Modèle de données
| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique du produit |
| name | String | Nom du produit (obligatoire) |
| description | Text | Description du produit |
| price | Decimal | Prix du produit (obligatoire) |
| stock | Integer | Quantité en stock (obligatoire) |
| categorie | ForeignKey | Catégorie du produit |
| artisan | ForeignKey | Artisan propriétaire du produit (obligatoire) |
| image | Image | Image du produit |
| date_added | Date | Date d'ajout du produit |

#### Lister tous les produits
```http
GET /api/produits/
```

**Exemple de réponse (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Table en bois",
        "description": "Table artisanale en chêne massif",
        "price": "299.99",
        "stock": 5,
        "categorie": 1,
        "artisan": 1,
        "image": "http://example.com/media/produits/table_bois.jpg"
    }
]
```

#### Créer un produit (Admin uniquement)
```http
POST /api/produits/
```

**Headers:**
```
Authorization: Bearer votre_access_token
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "name": "Chaise en bois",
    "description": "Chaise artisanale en chêne",
    "price": "149.99",
    "stock": 10,
    "categorie": 1,
    "artisan": 1
}
```

### Ventes

#### Modèle de données
| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique de la vente |
| numero_vente | String | Numéro unique de vente (généré automatiquement) |
| artisan | ForeignKey | Artisan concerné par la vente (obligatoire) |
| nom_du_client | String | Nom du client |
| designation | String | Désignation de la vente |
| date_vente | DateTime | Date de la vente |
| montant_total | Decimal | Montant total de la vente |

#### Ligne de vente
| Champ | Type | Description |
|-------|------|-------------|
| vente | ForeignKey | Vente associée |
| product | ForeignKey | Produit vendu |
| quantity | Integer | Quantité vendue |
| unit_price | Decimal | Prix unitaire au moment de la vente |

#### Lister toutes les ventes
```http
GET /api/ventes/
```

**Exemple de réponse (200 OK):**
```json
[
    {
        "id": 1,
        "numero_vente": "V20250001",
        "artisan": 1,
        "artisan_details": {
            "id": 1,
            "nom": "Artisan 1",
            "email": "artisan@example.com"
        },
        "nom_du_client": "Client 1",
        "designation": "Vente de meubles",
        "date_vente": "2025-09-15T14:30:00Z",
        "montant_total": "449.98",
        "lignes_vente": [
            {
                "id": 1,
                "product": 1,
                "quantity": 2,
                "unit_price": "224.99"
            }
        ]
    }
]
```

#### Créer une vente
```http
POST /api/ventes/
```

**Headers:**
```
Authorization: Bearer votre_access_token
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "artisan": 1,
    "nom_du_client": "Client 2",
    "designation": "Vente de déco",
    "lignes_vente": [
        {
            "product": 1,
            "quantity": 1
        },
        {
            "product": 2,
            "quantity": 2
        }
    ]
}
```

**Note :** La création d'une vente met automatiquement à jour les stocks des produits concernés.

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

### Exemple d'erreur de validation
```json
{
    "error": "Données de validation invalides",
    "status": "error",
    "details": {
        "artisan": ["Ce champ est obligatoire."],
        "lignes_vente": ["La liste ne peut pas être vide."]
    }
}
```

### Exemple d'erreur de stock insuffisant
```json
{
    "error": "Stock insuffisant pour le produit 'Table en bois'. Stock disponible : 2",
    "status": "error"
}
```

### Exemple d'erreur d'authentification
```json
{
    "detail": "Les informations d'authentification n'ont pas été fournies.",
    "status": "error"
}
```
