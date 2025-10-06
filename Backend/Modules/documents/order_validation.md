# Order Validation

## Description
Règles métier pour la validation des commandes entrantes.

## Vérifications
1. Tous les champs obligatoires remplis (client, adresse, produits).
2. Statut initial correct (`NEW`).
3. Produits existants dans l’inventaire.

## Actions recommandées
- Marquer la commande comme `READY` si valide.
- Notifier ExceptionAgent en cas d'erreur.

## Output attendu
- Commande validée ou signalée en erreur.
