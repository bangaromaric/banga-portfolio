---
title: "MboloPay — Mobile Money pédagogique : Spring Modulith, DDD, Architecture Hexagonale | Gabon"
heroTitle: "MboloPay [DDD · Hexagonal]"
tagline: "Mini mobile money éducatif gabonais — vitrine exécutable de Domain-Driven Design, Architecture Hexagonale et Spring Modulith sur un cas métier réel (Airtel, Moov, FCFA)."
description: "Mini mobile money pédagogique en Spring Boot 4 / Spring Modulith 2 — vitrine DDD + Architecture Hexagonale sur un cas Gabon (Airtel/Moov, FCFA). Bounded contexts identité & portefeuille, événements de domaine, frontend Lit + Material Web."
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

## Cible

Étudiants, formateurs, développeurs qui veulent **voir** une architecture hexagonale en mouvement plutôt que la lire dans un PDF. Le projet sert aussi de support pour les ateliers GDG Libreville sur les architectures modulaires Spring.

## Code

- **Repo** — [github.com/bangaromaric/mbolopay](https://github.com/bangaromaric/mbolopay)
- **Licence** — MIT
- **Captures** — `docs/assets/` (accueil, slow-mo, page architecture, inspector HTTP)
