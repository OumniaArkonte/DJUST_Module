# Invoice Generation

## Description
Instructions pour générer les factures et gérer le paiement.

## Vérifications
1. Vérifier le montant de la commande.
2. Associer la facture au bon `order_id`.

## Actions recommandées
- Générer la facture dans la base `payments`.
- Notifier le client de la création de facture.
- En cas d’échec, alerter ExceptionAgent.

## Output attendu
- Facture créée et paiement en cours ou échoué.
