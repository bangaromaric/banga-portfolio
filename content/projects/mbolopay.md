---
title: "MboloPay — Mobile Money pédagogique : Spring Modulith, DDD, Architecture Hexagonale | Gabon"
heroTitle: "MboloPay [DDD · Hexagonal]"
tagline: "Mini mobile money éducatif gabonais — vitrine exécutable de Domain-Driven Design, Architecture Hexagonale et Spring Modulith sur un cas métier réel (Airtel, Moov, FCFA)."
description: "Mobile money éducatif en Spring Boot 4 + Spring Modulith. Vitrine exécutable DDD, Architecture Hexagonale et Spring Native sur un cas gabonais (FCFA)."
date: 2026-05-17
year: 2026
role: "Conception · Architecture · Développement full-stack"
client: "Projet personnel · Open source (MIT)"
duration: "En cours"
status: "Pédagogique · Open source"
stack: ["Spring Boot 4", "Spring Modulith", "Java 25", "jMolecules", "ArchUnit", "Lit", "Material Web", "TypeScript", "H2"]
technologies: ["Spring Boot 4.0", "Spring Modulith 2.0", "Java 25", "jMolecules", "ArchUnit 1.4", "Lit 3", "Material Web", "TypeScript 5", "H2", "Hibernate"]
appType: "WebApplication"
github: "https://github.com/bangaromaric/mbolopay"
demo: "https://mbolopay.banga.ga/"
article: "https://medium.com/@bangaromaric/moussavou-apprend-ddd-le-guide-pratique-du-dev-qui-veut-%C3%A9crire-du-code-qui-tient-07a9192a3a42"
featured: true
weight: 1
showToc: false
---

## Pourquoi

Apprendre l'architecture par la pratique, pas par la slide. La plupart des cours sur DDD, l'architecture hexagonale ou Spring Modulith restent abstraits — diagrammes, théories, *« il faut »*, *« il faut pas »*. **MboloPay** prend l'angle inverse : un système exécutable, observable, animé, qui rend les concepts visibles à l'exécution.

Le domaine choisi est volontairement familier au Gabon : un mini **mobile money** avec souscripteurs, portefeuilles, transactions, validations contre les opérateurs Airtel et Moov, montants en FCFA.

## Ce que le projet expose

Trois disciplines combinées sur un seul cas métier :

- **Domain-Driven Design** — aggregats, value objects (Numero, Montant, IdSouscripteur), événements de domaine, ubiquitous language en français
- **Architecture Hexagonale** — séparation stricte domaine / ports / adapters, isolation des dépendances Spring
- **Spring Modulith** — bounded contexts modulaires (`identite`, `portefeuille`, `shared`), communication par événements, ArchUnit pour enforcer les frontières architecturales en tests automatisés

## Comment c'est rendu visible

L'application n'est pas seulement *correcte* — elle est *pédagogique*. Cinq dispositifs rendent l'architecture observable depuis l'interface :

- **Cycle d'opération en 13 étapes** — chaque commande passe par une animation step-by-step (réception, validation, persistance, événement, projection)
- **Slow-mo des événements de domaine** — les événements sont ralentis pour montrer la propagation entre contextes
- **Traversée des couches hexagonales** — chaque traversée (UI → port → use case → repository) est mise en surbrillance
- **Inspector HTTP live** — toutes les requêtes/réponses sont visibles en temps réel dans une console embarquée
- **Page `/architecture`** — académie avec 11 cartes glossaire et exemples de code

## Stack et choix techniques

- **Backend** : Java 25, Spring Boot 4.0.2, Spring Modulith 2.0.2, jMolecules 0.33 (annotations DDD), ArchUnit 1.4 (tests d'architecture), H2 in-memory
- **Frontend** : TypeScript 5, Lit 3.3 (Web Components), Material Web 2.4, esbuild — orchestré par Maven, **aucune installation npm requise**
- **Lancement** : `./mvnw spring-boot:run` puis `http://localhost:8080`

## Décisions techniques

Pourquoi ces choix, pas d'autres :

**Spring Modulith plutôt que microservices**. Sur un cas pédagogique, scinder en quatre microservices serait un signal de complexité sans en porter la valeur. Spring Modulith garde un seul livrable, un seul process, une seule base — mais impose des frontières internes vérifiées par tests ArchUnit. On apprend la modularité sans payer le coût opérationnel des microservices. Si demain le module `portefeuille` doit scaler indépendamment, l'extraction reste possible sans réécriture.

**Java 25 plutôt que Java 21 LTS**. Java 25 apporte le pattern matching renforcé qui simplifie l'écriture des value objects DDD, et s'aligne avec Liberica NIK 25 — un seul package au lieu de deux JDK distinctes pour la compilation native. Coût assumé : Java 25 n'est pas LTS, ce qui convient à un projet pédagogique mais pas à une fintech en production.

**H2 in-memory plutôt que Postgres**. Choix volontairement austère : aucune installation, aucun Docker Compose, `./mvnw spring-boot:run` et l'application tourne. Pour un atelier GDG Libreville où les participants ont des bandes passantes variables et des OS hétérogènes, cette simplicité vaut plus qu'un setup *« réaliste »*. Le schéma Hibernate reste compatible Postgres pour qui veut basculer.

**Lit + Material Web plutôt que React**. Web Components standards, orchestrés par Maven via esbuild — aucun `npm install` requis pour démarrer. Un développeur Java clone le repo et lance le projet sans toucher au monde Node. Le build Maven gère tout : compilation TypeScript, bundling esbuild, fingerprint des assets.

**Spring Native (GraalVM) en option de production**. Pour le déploiement Cloud Run de la démo, le binaire natif boote en 205 ms au lieu de 3 740 ms en JVM. Ça permet de tenir le free tier GCP avec `min-instances=0` — démo gratuite tant que sous deux millions de requêtes par mois.

## Mesures en production

Benchmarks mesurés le 16 mai 2026 sur la compilation native de MboloPay (Spring Boot 4.0.2, Java 25, Liberica NIK 25, Hibernate 7.2.1) :

| Métrique | JVM Java 25 | Natif GraalVM | Gain |
|---|---|---|---|
| Cold-start total | 3 740 ms | 205 ms | ×18,2 |
| JPA init seul | 774 ms | 14 ms | ×55 |
| RAM résident | ~250 Mo | ~80 Mo | ÷3 |
| Taille livrable | ~50 Mo (JAR) | ~120-180 Mo (binaire) | ×3 (compromis) |
| Build CI | ~10 s | 7-12 min | ×12 (compromis assumé) |
| Coût Cloud Run | — | 0 FCFA/mois | sous free tier 2M requêtes |

Lecture clé : la JPA init seule passe de 774 ms à 14 ms grâce à l'AOT processing de Spring Boot 4 qui pré-calcule le mapping Hibernate à la compilation. Sur une fintech qui scale à zéro la nuit, ce gain change la différence entre transaction qui aboutit et transaction perdue le matin.

## Cible

Étudiants, formateurs, développeurs qui veulent **voir** une architecture hexagonale en mouvement plutôt que la lire dans un PDF. Le projet sert aussi de support pour les ateliers GDG Libreville sur les architectures modulaires Spring.

## Pour aller plus loin

Deux articles approfondissent les choix architecturaux de MboloPay :

- [**Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith**]({{< ref "/posts/architecture-ia-spring-modulith" >}}) — comment MOUSSAVOU apprend à modéliser le domaine portefeuille et à laisser les modules dialoguer par événements de domaine.
- [**Spring Native + Cloud Run — cold-start ÷18, RAM ÷3 sur MboloPay**]({{< ref "/posts/spring-native-cloud-run" >}}) — benchmark détaillé sur quatre étapes du démarrage, cinq pièges Windows, profil Maven `-Pnative`, pipeline PowerShell de déploiement Cloud Run.

## Code

- **Repo** — [github.com/bangaromaric/mbolopay](https://github.com/bangaromaric/mbolopay)
- **Licence** — MIT
- **Captures** — `docs/assets/` (accueil, slow-mo, page architecture, inspector HTTP)
