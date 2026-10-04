---
title: "Pli : partage de secrets à usage unique, chiffré dans le navigateur | Go, Redis, Cloud Run"
heroTitle: "Pli [zéro connaissance]"
tagline: "Partage de secrets à usage unique, chiffré dans le navigateur : le serveur ne reçoit qu'un bloc illisible, et la première lecture le détruit."
description: "Pli chiffre vos secrets dans le navigateur avant tout envoi. Go, Redis, Cloud Run. Destruction à la première lecture, cinq invariants tenus par des tests."
date: 2026-10-04
year: 2026
role: "Conception · Architecture · Développement · Déploiement GCP"
client: "Projet personnel"
duration: "Depuis septembre 2026"
status: "Production · pli.banga.ga"
stack: ["Go", "Redis", "WebCrypto", "Cloud Run", "JavaScript sans dépendance"]
technologies: ["Go", "Gin", "Redis", "AES-256-GCM", "Cloud Run", "Artifact Registry", "Secret Manager"]
appType: "WebApplication"
demo: "https://pli.banga.ga/"
featured: true
weight: 1
showToc: false
cover:
    image: "/images/pli-cover.png"
    alt: "Les trois états d'un pli : le secret chiffré chez l'expéditeur, un bloc illisible sur le serveur, le secret rendu une seule fois chez le destinataire. Schéma par Romaric BANGA."
    caption: "Le serveur ne détient jamais la clé : elle voyage dans la partie de l'adresse que les navigateurs ne transmettent pas."
---

## Le problème

Un dossier administratif ne s'envoie jamais en une pièce. Un visa, une ouverture de compte, une location, une candidature : quatre à six documents, dont une carte d'identité, un bulletin de paie, un relevé bancaire. Le canal disponible est celui que tout le monde a déjà, WhatsApp ou un courriel, et c'est précisément celui qui garde tout. La pièce reste dans la conversation, chez vous, chez le destinataire, et sur les serveurs de l'intermédiaire. Aucun de ces outils n'a de bouton *« détruire après lecture »*.

Les services qui répondent à ce besoin se rangent en deux familles, et le lecteur tombe toujours du mauvais côté. Ceux qui facturent un abonnement chiffrent sur leur serveur : ils peuvent donc lire ce qu'ils stockent, et le disent en petits caractères. Ceux qui chiffrent dans le navigateur, et tiennent donc la promesse, sont des projets gratuits sans engagement de service. **Pli** occupe l'intersection.

## La promesse

Le secret est chiffré dans votre navigateur, avant qu'un seul octet ne parte. La clé de déchiffrement voyage dans la partie de l'adresse que les navigateurs, par conception, ne transmettent jamais au serveur. C'est l'approche commune à cette catégorie d'outils, et c'est toute la différence entre *« nous ne lisons pas vos données »* et *« nous ne pouvons pas les lire »*. Le serveur conserve donc un bloc qu'il est incapable d'ouvrir, et la première lecture le détruit : une seconde tentative sur le même lien ne trouve plus rien.

S'y ajoutent une phrase de passe optionnelle, qui fait que le lien seul ne suffit plus, un code QR pour passer d'un écran à un téléphone sans recopier, et un numéro de suivi qui dit si le pli a été ouvert.

## La limite, écrite plutôt que passée sous silence

C'est le serveur qui sert le JavaScript qui chiffre. Un attaquant qui contrôle activement ce serveur peut donc modifier ce script, et aucune quantité de cryptographie côté navigateur ne referme cette porte : elle est ouverte par la façon dont le web livre du code. La limite est partagée par **tous** les outils de cette catégorie, sans exception. Elle est écrite ici plutôt que passée sous silence, parce qu'un produit de confiance qui cache sa limite n'en est plus un.

Le numéro de suivi est la seule concession du produit à son propre principe d'indiscernabilité. Elle est assumée, et bornée à cette seule fonction.

## Les cinq invariants

Cinq engagements, numérotés dans le dépôt, chacun tenu par au moins un test automatisé. Plusieurs sont revérifiés contre le service réel à chaque mise en production, et pas seulement en intégration continue.

- **I1** : le serveur ne peut jamais déchiffrer.
- **I2** : la destruction est atomique, deux lecteurs simultanés et un seul servi.
- **I3** : un pli absent, expiré ou déjà lu donne la même réponse, au même coût.
- **I4** : la révélation n'est jamais déclenchée par une simple visite d'adresse.
- **I5** : aucun identifiant de pli n'apparaît dans aucun journal.

I3 est le moins intuitif et le plus important : si les trois réponses différaient, un tiers qui essaie des liens au hasard apprendrait lesquels ont existé.

## Arbitrages

**Go plutôt que la JVM.** Pli est le portage d'un service Java. Le conteneur est passé de près de 300 Mo à 44 Mo, le démarrage de deux secondes à quelques millisecondes, sans aucune compilation native à entretenir. C'est le contrepoint honnête à mes propres mesures sur Spring Native : le natif rattrape la JVM, il ne rattrape pas un langage qui n'a jamais eu ce problème. Coût assumé, on quitte l'écosystème Spring et tout l'outillage qui vient avec.

**Aucune dépendance frontend.** La page est servie sans cache, par choix : rien ne doit rester dans le navigateur. Chaque octet est donc repayé à chaque visite, ce qui change le calcul. Le framework CSS d'origine pesait les deux tiers de la page pour un reset et deux utilitaires, il a été retiré. Coût assumé, tout s'écrit à la main et tout se teste à la main.

**Pas de CAPTCHA.** Ce n'est pas un oubli mais une impossibilité : tout service de CAPTCHA exige de charger un script tiers sur la page même où le secret est saisi en clair. Coût assumé, la défense contre l'abus doit vivre ailleurs, et c'est nettement plus difficile.

## Ce que le produit refuse

Un tableau de bord listant ses plis en attente a été demandé, étudié, puis refusé. Une table qui relie un expéditeur à ses envois **est** une trace, quel que soit le nom qu'on lui donne, et elle fabrique une cible qui n'existait pas. Elle ne marcherait d'ailleurs pas pour le public visé, celui qui change de téléphone et se connecte parfois depuis l'ordinateur d'un cybercafé : le tableau serait vide exactement pour ceux à qui le produit s'adresse.

Le filigrane automatique sur les documents a été retiré pour une raison plus simple. Sur un PDF, il coûterait plus lourd que la page entière, et il ne devrait de toute façon jamais être vendu comme une protection, puisqu'il n'en est pas une.

C'est la même règle dans les deux cas : on ne vend pas une barrière qu'on ne sait pas tenir.

## Essayer

Le service est en ligne, sans compte et sans inscription : [pli.banga.ga](https://pli.banga.ga/). Un pli vit une heure ou douze heures, au choix, et disparaît de toute façon à la première lecture.

Mesures du projet, telles que le dépôt les consigne : conteneur de 44 Mo, page de création servie sous 120 Ko, suite de tests complète sous la minute avec le détecteur de course activé, et 2,7 lignes de test pour une ligne de production.

## Pour aller plus loin

- [**Spring Native + Cloud Run, cold-start ÷18 et RAM ÷3**]({{< ref "/posts/spring-native-cloud-run" >}}) : le même problème de démarrage à froid, résolu dans l'autre sens, en gardant la JVM et en compilant en natif.
- [**Cloud Run derrière un load balancer global**]({{< ref "/posts/cloud-run-load-balancer" >}}) : comment un service Cloud Run s'expose proprement sous son propre domaine, certificat et politique TLS comprises.
