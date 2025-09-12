# Documentation de l'API REST GestiArt

Bienvenue dans la documentation de l'API REST pour GestiArt, une application de gestion d'activités artisanales pour le Village Artisanal Régional de Bafoussam (VARBAF). Cette API est conçue pour moderniser la gestion artisanale en digitalisant la gestion des artisans, des produits, le suivi des ventes, et le calcul de statistiques et rapports.

L'API est construite avec Django et Django REST Framework, et utilise l'authentification **Basic** pour sécuriser les endpoints. Elle est organisée en modules (Artisans, Produits, Catégories, Ventes, Statistiques, Utilisateurs) avec des endpoints clairs et structurés.

## Table des Matières

1.  [Authentification Basic](#1-authentification-basic)
2.  [Module Utilisateurs](#2-module-utilisateurs)
3.  [Module Artisans](#3-module-artisans)
4.  [Module Produits](#4-module-produits)
5.  [Module Catégories](#5-module-catégories)
6.  [Module Ventes](#6-module-ventes)
7.  [Module Statistiques](#7-module-statistiques)

## Configuration et Démarrage

Pour démarrer le projet localement, suivez les étapes suivantes :

1.  **Cloner le dépôt (si applicable) :**
    ```bash
    git clone <URL_DU_DEPOT>
    cd gestiart
    ```
2.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configurer la base de données MySQL :**
    Assurez-vous d'avoir un serveur MySQL en cours d'exécution. Mettez à jour les informations de connexion dans `gestiart/settings.py` :
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'gestiart_db', # Nom de votre base de données
            'USER': 'root',         # Votre nom d'utilisateur MySQL
            'PASSWORD': 'password', # Votre mot de passe MySQL
            'HOST': 'localhost',ccc
            'PORT': '3306',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            }
        }
    }
    ```
4.  **Exécuter les migrations :**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5.  **Créer un superutilisateur (administrateur) :**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Démarrer le serveur Django :**
    ```bash
    python manage.py runserver
        ```

L'API sera accessible à `http://127.0.0.1:8000/api/`.

## 1. Authentification Basic

L'API GestiArt utilise l'authentification **HTTP Basic**. C'est une méthode d'authentification simple où les identifiants (email et mot de passe) sont envoyés avec chaque requête, encodés en Base64.

**⚠️ Avertissement de Sécurité :** L'authentification Basic n'est pas sécurisée si elle est utilisée sur une connexion HTTP non chiffrée (sans HTTPS). Pour un environnement de production, vous devez **impérativement utiliser HTTPS** ou un mécanisme d'authentification plus robuste (comme les tokens JWT ou les tokens d'API de Django REST Framework si la simplicité des tokens est acceptable).

### Processus d'Authentification

1.  **Enregistrement (si nouvel utilisateur) :** Créez un compte utilisateur en utilisant l'endpoint `/api/register/`.
2.  **Accès aux ressources :** Pour chaque requête à un endpoint sécurisé, incluez l'en-tête `Authorization` avec la valeur `Basic <credentials_base64>`.
    *   Pour obtenir `<credentials_base64>`, combinez votre email et mot de passe au format `email:password`, puis encodez cette chaîne en Base64.
    *   **Exemple :** Si votre email est `admin@example.com` et votre mot de passe est `admin123`, la chaîne `admin@example.com:admin123` encodée en Base64 donne `YWRtaW5AZXhhbXBsZS5jb206YWRtaW4xMjM=` (cela sera différent pour vos propres identifiants).

### Permissions

Les permissions sont gérées en fonction du `user_type` (admin, artisan, secondary_admin) et sont appliquées au niveau des vues.

*   **Admin :** Accès complet (CRUD) à toutes les ressources.
*   **Secondary Admin :** Accès en lecture à toutes les ressources, et accès aux statistiques.
*   **Artisan :** Accès en lecture/écriture à ses propres ressources (profil, produits, ventes) et accès en lecture aux produits et ventes publiques.
*   **AllowAny :** Aucun utilisateur n'est requis.
*   **IsAuthenticated :** Tout utilisateur authentifié.

## 2. Module Utilisateurs

Ce module gère l'enregistrement et la gestion des utilisateurs (administrateurs, artisans, administrateurs secondaires). Pour les endpoints sécurisés, l'authentification Basic est requise.

### Endpoints

#### **POST /api/register/**
*   **Description :** Enregistre un nouvel utilisateur.
*   **Permissions :** `AllowAny`
*   **Requête (Body JSON) :**
    ```json
    {
        "email": "utilisateur@example.com",
        "password": "votremotdepasse",
        "user_type": "artisan" 
    }
    ```
    *`user_type` peut être `admin`, `artisan` ou `secondary_admin`. Par défaut : `artisan`.*
*   **Réponse (Succès - 201 Created) :**
    ```json
    {
        "id": 1,
        "email": "utilisateur@example.com",
        "user_type": "artisan"
    }
    ```

#### **GET /api/users/**
*   **Description :** Liste tous les utilisateurs du système.
*   **Permissions :** `Admin` ou `Secondary Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Liste d'utilisateurs)
    ```json
    [
        {
            "id": 1,
            "email": "admin@example.com",
            "user_type": "admin"
        },
        // ... autres utilisateurs ...
    ]
    ```

#### **GET /api/users/{id}/**
*   **Description :** Récupère les détails d'un utilisateur spécifique.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :**
    ```json
    {
        "id": 1,
        "email": "admin@example.com",
        "user_type": "admin"
    }
    ```

#### **PUT /api/users/{id}/**
*   **Description :** Met à jour un utilisateur existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "email": "nouvel_email@example.com",
        "user_type": "secondary_admin"
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet utilisateur mis à jour)

#### **PATCH /api/users/{id}/**
*   **Description :** Met à jour partiellement un utilisateur existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "user_type": "admin"
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet utilisateur mis à jour partiellement)

#### **DELETE /api/users/{id}/**
*   **Description :** Supprime un utilisateur existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 204 No Content)**

## 3. Module Artisans

Ce module permet de gérer les profils des artisans. Chaque profil est lié à un utilisateur de type `artisan`.

### Endpoints

#### **POST /api/artisans/**
*   **Description :** Crée un nouveau profil d'artisan. L'utilisateur associé doit exister et être de type `artisan`.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "user_id": 1, 
        "first_name": "Fatou",
        "last_name": "Diallo",
        "speciality": "Vannerie",
        "contact_phone": "+237699112233",
        "contact_email": "fatou.diallo@example.com",
        "department": "Littoral",
        "image": null 
    }
    ```
    *`user_id` est l'ID de l'utilisateur existant de type `artisan`. `image` est facultatif (peut être `null` ou un fichier `multipart/form-data`).*
*   **Réponse (Succès - 201 Created) :**
    ```json
    {
        "user": {
            "id": 1,
            "email": "artisan@example.com",
            "user_type": "artisan"
        },
        "user_id": 1,
        "first_name": "Fatou",
        "last_name": "Diallo",
        "speciality": "Vannerie",
        "contact_phone": "+237699112233",
        "contact_email": "fatou.diallo@example.com",
        "date_joined": "2023-10-27",
        "department": "Littoral",
        "image": null 
    }
    ```

#### **GET /api/artisans/**
*   **Description :** Liste tous les profils d'artisans. Un artisan ne verra que son propre profil.
*   **Permissions :** `Admin`, `Secondary Admin` ou `Artisan`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Liste d'artisans)
    ```json
    [
        {
            "user": {
                "id": 1,
                "email": "artisan@example.com",
                "user_type": "artisan"
            },
            "user_id": 1,
            "first_name": "Fatou",
            "last_name": "Diallo",
            "speciality": "Vannerie",
            "contact_phone": "+237699112233",
            "contact_email": "fatou.diallo@example.com",
            "date_joined": "2023-10-27",
            "department": "Littoral",
            "image": "http://127.0.0.1:8000/media/artisans_images/fatou.jpg" 
        },
        // ... autres artisans ...
    ]
    ```

#### **GET /api/artisans/{id}/**
*   **Description :** Récupère les détails d'un profil d'artisan spécifique.
*   **Permissions :** `Admin`, `Secondary Admin` ou `Artisan` (s'il est le propriétaire du profil)
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Objet artisan)

#### **PUT /api/artisans/{id}/**
*   **Description :** Met à jour un profil d'artisan existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "speciality": "Céramique",
        "contact_phone": "+237677987654"
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet artisan mis à jour)

#### **PATCH /api/artisans/{id}/**
*   **Description :** Met à jour partiellement un profil d'artisan existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "speciality": "Bijouterie"
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet artisan mis à jour partiellement)

#### **DELETE /api/artisans/{id}/**
*   **Description :** Supprime un profil d'artisan existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 204 No Content)**

## 4. Module Produits

Gestion complète des produits artisanaux avec suivi des stocks et catégorisation.

### Structure des données

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Identifiant unique (automatique) |
| `name` | String (255) | Nom du produit (obligatoire) |
| `description` | Text | Description complète (optionnel) |
| `categorie` | Integer | ID de la catégorie (obligatoire) |
| `price` | Decimal | Prix unitaire (max 99999999.99) |
| `stock` | Integer | Quantité disponible (défaut: 0) |
| `numero_boutique` | String (50) | Référence de localisation (ex: "A12") |
| `date_added` | Date | Date de création (automatique) |
| `artisan` | Integer | ID de l'artisan propriétaire |
| `image` | File | Photo du produit (optionnel) |

### Points clés

1. **Catégorie**
   - Choisir parmi les catégories existantes
   - Utiliser l'ID de la catégorie
   - Exemple: `"categorie": 3`

2. **Numéro de boutique**
   - Format libre (ex: "A12", "Boutique 3")
   - Permet de localiser physiquement l'artisan
   - Optionnel mais recommandé

3. **Gestion des stocks**
   - Le stock est automatiquement mis à jour lors des ventes
   - Valeur minimale: 0
   - Les produits en rupture n'apparaissent pas dans les résultats par défaut

**Exemple de création** :
```json
{
    "name": "Masque traditionnel Bamiléké",
    "description": "Masque cérémoniel en bois sculpté à la main",
    "categorie": 2,
    "price": "75.50",
    "stock": 8,
    "numero_boutique": "B12",
    "artisan": 1
}
```

### Endpoints

#### **POST /api/produits/**
*   **Description :** Crée un nouveau produit.
*   **Permissions :** `Admin` ou `Artisan`
    *   Si `Admin`, `artisan_id` est obligatoire dans la requête.
    *   Si `Artisan`, le produit est automatiquement lié à son profil.
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "name": "Sac en raphia",
        "description": "Sac artisanal tressé en raphia",
        "category": "Vannerie",
        "price": 50.00,
        "stock": 30,
        "artisan_id": 1,
        "image": null 
    }
    ```
    *`artisan_id` est l'ID de l'artisan associé. Obligatoire pour les admins, ignoré pour les artisans (lié automatiquement). `image` est facultatif (peut être `null` ou un fichier `multipart/form-data`).*
*   **Réponse (Succès - 201 Created) :**
    ```json
    {
        "id": 1,
        "name": "Sac en raphia",
        "description": "Sac artisanal tressé en raphia",
        "category": "Vannerie",
        "price": "50.00",
        "stock": 30,
        "date_added": "2023-10-27",
        "artisan": {
            "user": {
                "id": 1,
                "email": "artisan@example.com",
                "user_type": "artisan"
            },
            "first_name": "Fatou",
            "last_name": "Diallo",
            "speciality": "Vannerie",
            "contact_phone": "+237699112233",
            "contact_email": "fatou.diallo@example.com",
            "date_joined": "2023-10-27",
            "department": "Littoral"
        },
        "artisan_id": 1,
        "image": "http://127.0.0.1:8000/media/produits_images/raphia_sac.jpg" 
    }
    ```

#### **GET /api/produits/**
*   **Description :** Liste tous les produits. Les artisans ne verront que leurs propres produits.
*   **Permissions :** `Admin`, `Secondary Admin` ou `Artisan`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Liste de produits)

#### **GET /api/produits/{id}/**
*   **Description :** Récupère les détails d'un produit spécifique.
*   **Permissions :** `Admin`, `Secondary Admin` ou `Artisan` (s'il est le propriétaire du produit)
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Objet produit)

#### **PUT /api/produits/{id}/**
*   **Description :** Met à jour un produit existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "name": "Sac en raphia tressé",
        "price": 55.00,
        "stock": 25
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet produit mis à jour)

#### **PATCH /api/produits/{id}/**
*   **Description :** Met à jour partiellement un produit existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "stock": 28
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet produit mis à jour partiellement)

#### **DELETE /api/produits/{id}/**
*   **Description :** Supprime un produit existant.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 204 No Content)**

## 5. Module Catégories

Ce module permet de gérer les catégories de produits. Les catégories permettent d'organiser les produits par type ou par famille.

### Modèle de données

| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Identifiant unique de la catégorie |
| nom | String (100) | Nom de la catégorie (unique) |
| description | Text | Description de la catégorie (optionnelle) |
| date_creation | DateTime | Date de création (automatique) |
| date_mise_a_jour | DateTime | Date de dernière mise à jour (automatique) |

### Endpoints

#### **GET /api/categories/**
*   **Description :** Récupère la liste de toutes les catégories.
*   **Permissions :** Tous les utilisateurs authentifiés
*   **Réponse (Succès - 200 OK) :**
    ```json
    [
        {
            "id": 1,
            "nom": "Sculpture",
            "description": "Œuvres sculptées en bois, pierre, etc.",
            "date_creation": "2025-09-12T04:00:00Z",
            "date_mise_a_jour": "2025-09-12T04:00:00Z"
        },
        ...
    ]
    ```

#### **POST /api/categories/**
*   **Description :** Crée une nouvelle catégorie.
*   **Permissions :** Administrateur uniquement
*   **Requête (Body JSON) :**
    ```json
    {
        "nom": "Céramique",
        "description": "Objets en terre cuite et céramique"
    }
    ```
*   **Réponse (Succès - 201 Created) :**
    ```json
    {
        "id": 2,
        "nom": "Céramique",
        "description": "Objets en terre cuite et céramique",
        "date_creation": "2025-09-12T04:05:00Z",
        "date_mise_a_jour": "2025-09-12T04:05:00Z"
    }
    ```

#### **GET /api/categories/{id}/**
*   **Description :** Récupère les détails d'une catégorie spécifique.
*   **Permissions :** Tous les utilisateurs authentifiés
*   **Réponse (Succès - 200 OK) :**
    ```json
    {
        "id": 1,
        "nom": "Sculpture",
        "description": "Œuvres sculptées en bois, pierre, etc.",
        "date_creation": "2025-09-12T04:00:00Z",
        "date_mise_a_jour": "2025-09-12T04:00:00Z"
    }
    ```

#### **PUT /api/categories/{id}/**
*   **Description :** Met à jour une catégorie existante.
*   **Permissions :** Administrateur uniquement
*   **Requête (Body JSON) :**
    ```json
    {
        "nom": "Sculpture sur bois",
        "description": "Œuvres sculptées principalement en bois"
    }
    ```
*   **Réponse (Succès - 200 OK) :**
    ```json
    {
        "id": 1,
        "nom": "Sculpture sur bois",
        "description": "Œuvres sculptées principalement en bois",
        "date_creation": "2025-09-12T04:00:00Z",
        "date_mise_a_jour": "2025-09-12T04:10:00Z"
    }
    ```

#### **DELETE /api/categories/{id}/**
*   **Description :** Supprime une catégorie.
*   **Permissions :** Administrateur uniquement
*   **Réponse (Succès - 204 No Content)**

## 6. Module Ventes

Ce module gère l'enregistrement et le suivi des transactions de vente. La mise à jour du stock des produits est automatique après chaque vente.

### Endpoints

#### **POST /api/ventes/**
*   **Description :** Enregistre une nouvelle vente.
*   **Permissions :** `Admin` ou `Artisan`
    *   Si `Artisan`, seul ses propres produits peuvent être vendus.
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "product": 1, 
        "quantity": 2
    }
    ```
    *`product` est l'ID du produit vendu. `unit_price` sera automatiquement renseigné par le prix actuel du produit. `artisan` sera automatiquement lié au produit vendu.*
*   **Réponse (Succès - 201 Created) :**
    ```json
    {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "product": 1,
        "product_details": {
            "id": 1,
            "name": "Sac en raphia",
            "description": "Sac artisanal tressé en raphia",
            "category": "Vannerie",
            "price": "50.00",
            "stock": 28,
            "date_added": "2023-10-27",
            "artisan": {
                "user": {
                    "id": 1,
                    "email": "artisan@example.com",
                    "user_type": "artisan"
                },
                "first_name": "Fatou",
                "last_name": "Diallo",
                "speciality": "Vannerie",
                "contact_phone": "+237699112233",
                "contact_email": "fatou.diallo@example.com",
                "date_joined": "2023-10-27",
                "department": "Littoral"
            }
        },
        "quantity": 2,
        "unit_price": "50.00",
        "total_price": "100.00",
        "sale_date": "2023-10-27T10:00:00Z",
        "artisan": 1,
        "artisan_details": {
            "user": {
                "id": 1,
                "email": "artisan@example.com",
                "user_type": "artisan"
            },
            "first_name": "Fatou",
            "last_name": "Diallo",
            "speciality": "Vannerie",
            "contact_phone": "+237699112233",
            "contact_email": "fatou.diallo@example.com",
            "date_joined": "2023-10-27",
            "department": "Littoral"
        }
    }
    ```

#### **GET /api/ventes/**
*   **Description :** Liste toutes les ventes. Les artisans ne verront que les ventes de leurs produits.
*   **Permissions :** `Admin`, `Secondary Admin` ou `Artisan`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Liste de ventes)

#### **GET /api/ventes/{uuid}/**
*   **Description :** Récupère les détails d'une vente spécifique.
*   **Permissions :** `Admin`, `Secondary Admin` ou `Artisan` (s'il est lié à la vente par le produit)
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :** (Objet vente)

#### **PUT /api/ventes/{uuid}/**
*   **Description :** Met à jour une vente existante. (Seul un admin peut modifier une vente pour corriger d'éventuelles erreurs. La mise à jour du stock n'est pas automatique ici pour éviter des incohérences si la correction n'est pas liée à la quantité du produit initialement vendue.)
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "product": 1,
        "quantity": 3,
        "unit_price": 50.00 
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet vente mis à jour)

#### **PATCH /api/ventes/{uuid}/**
*   **Description :** Met à jour partiellement une vente existante.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Requête (Body JSON) :**
    ```json
    {
        "quantity": 1 
    }
    ```
*   **Réponse (Succès - 200 OK) :** (Objet vente mis à jour partiellement)

#### **DELETE /api/ventes/{uuid}/**
*   **Description :** Supprime une vente existante.
*   **Permissions :** `Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 204 No Content)**

## 6. Module Statistiques

Ce module fournit des endpoints pour récupérer des statistiques globales et générer des rapports détaillés sur les activités des artisans et les ventes.

### Endpoints

#### **GET /api/stats/dashboard/**
*   **Description :** Récupère un ensemble de statistiques clés pour le tableau de bord.
*   **Permissions :** `Admin` ou `Secondary Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :**
    ```json
    {
        "total_artisans": 5,
        "active_products": 12,
        "total_sales_global": "1500.50",
        "total_revenue": "1500.50",
        "sales_by_artisan": [
            {
                "artisan__first_name": "Fatou",
                "artisan__last_name": "Diallo",
                "total_sales": "750.00"
            },
            {
                "artisan__first_name": "Jean",
                "artisan__last_name": "Dupont",
                "total_sales": "500.50"
            }
        ],
        "top_selling_products": [
            {
                "product__name": "Sac en raphia",
                "total_quantity_sold": 10
            },
            {
                "product__name": "Vase en terre cuite",
                "total_quantity_sold": 8
            }
        ]
    }
    ```

#### **GET /api/stats/report-card/**
*   **Description :** Génère une fiche de rapport tabulaire détaillée pour tous les artisans, leurs produits et les ventes associées.
*   **Permissions :** `Admin` ou `Secondary Admin`
*   **En-têtes (Headers) :** `Authorization: Basic <credentials_base64>`
*   **Réponse (Succès - 200 OK) :**
    ```json
    [
        {
            "artisan_name": "Fatou Diallo",
            "speciality": "Vannerie",
            "product_name": "Sac en raphia",
            "product_category": "Vannerie",
            "product_price": "50.00",
            "product_stock": 28,
            "total_sales_for_product": 10,
            "revenue_for_product": "500.00"
        },
        {
            "artisan_name": "Fatou Diallo",
            "speciality": "Vannerie",
            "product_name": "Chapeau tressé",
            "product_category": "Vannerie",
            "product_price": "30.00",
            "product_stock": 15,
            "total_sales_for_product": 5,
            "revenue_for_product": "150.00"
        },
        {
            "artisan_name": "Jean Dupont",
            "speciality": "Sculpteur",
            "product_name": "Statue en bois",
            "product_category": "Sculpture",
            "product_price": "100.00",
            "product_stock": 5,
            "total_sales_for_product": 2,
            "revenue_for_product": "200.00"
        },
        {
            "artisan_name": "Nouvel Artisan",
            "speciality": "Peintre",
            "product_name": "N/A",
            "product_category": "N/A",
            "product_price": 0,
            "product_stock": 0,
            "total_sales_for_product": 0,
            "revenue_for_product": 0
        }
    ]
    ```
