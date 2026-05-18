---
title: "Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith — 2026"
heroTitle: "Architecture & [IA générative] en 2026"
date: 2026-05-18
description: "Synthèse de 5 takeaways pour utiliser Claude, ChatGPT et Copilot sans laisser l'IA générer un monstre. DDD, architecture hexagonale et Spring Modulith comme garde-fous — illustré par MboloPay, mini mobile money pédagogique gabonais."
tags: ["DDD", "Architecture Hexagonale", "Spring Modulith", "Spring Boot", "IA générative", "Java", "jMolecules", "ArchUnit"]
categories: ["Architecture"]
draft: false
showToc: false
cover:
    image: "/images/hexagonal-architecture.png"
    alt: "Schéma de l'architecture hexagonale en 4 couches — Primary (incoming adapters), Application (orchestration), Domain (core business logic), Secondary (outgoing adapters) — Romaric BANGA"
    caption: "Architecture hexagonale — domaine au centre, adaptateurs interchangeables"
---

Hier j'ai publié sur Medium un long article — *« MOUSSAVOU apprend DDD »* — qui détaille pourquoi, en 2026, savoir coder n'est plus le différenciateur. Le vrai super-pouvoir, c'est de **savoir quoi demander à l'IA et comprendre ce qu'elle te rend**.

Voici la synthèse en 5 takeaways pour les pressés. La version complète (17 min de lecture, exemples de code Java, exercices) est sur Medium — lien en bas.

## 1. L'IA accélère le code médiocre si l'architecture n'est pas définie

ChatGPT, Claude, Copilot produisent du code qui compile. Sans cadre, ils génèrent aussi des *services* de 600 lignes, des règles métier dispersées entre validators Spring et listeners Hibernate, et un *anemic domain model* qui explose au premier changement de règle. L'IA n'oriente pas — elle exécute.

## 2. DDD = modéliser le métier, pas la technique

Trois primitives qui sauvent ton code :

- **Bounded Context** — un périmètre où le vocabulaire métier est cohérent. Dans [MboloPay]({{< ref "/projects/mbolopay" >}}), il y en a trois : `identite`, `portefeuille`, `shared`.
- **Aggregate Root** — un tronc métier qui naît déjà valide (pas de `new` + setters).
- **Value Object** — la *vraie* protection. `NumeroTelephoneGabonais` qui valide E.164 dans le constructeur transforme une erreur runtime en erreur de compilation.

## 3. Hexagonal = domaine au centre, adaptateurs interchangeables

La règle absolue : **infrastructure dépend du domaine, jamais l'inverse**. Pas d'`import org.springframework.*` dans le domaine. Les ports sont des interfaces. L'orchestration vit dans `application/service/`. Le résultat : le métier reste testable sans Spring, et migrable d'une base SQL à NoSQL en remplaçant l'adapter.

## 4. Spring Modulith = monolithe modulaire vérifié au runtime

Plusieurs Bounded Contexts dans un seul Spring Boot, avec frontières vérifiées :

- `@ApplicationModule(allowedDependencies = {...})` déclare ce que chaque module peut importer.
- `@ApplicationModuleListener` orchestre la communication par événements de domaine.
- `ModularityTests` (Spring Modulith) **casse le build** si un module viole les dépendances autorisées.

Demain, extraire un module en microservice devient trivial.

## 5. Verrouille avec des tests d'architecture

Le vrai filet de sécurité face à l'IA, c'est ArchUnit. Mes 18 règles sur MboloPay vérifient automatiquement :

- Le domaine n'importe pas Spring/JPA/Jackson.
- Les exceptions métier héritent toutes de `ExceptionDomaine`.
- `@RestController` ne vit QUE dans `infrastructure/primary/web/`.

L'IA peut glisser un `@Service` dans le domaine ; le CI refuse. **L'architecture devient exécutable.**

---

## La règle pratique pour les développeurs en 2026

> Apprends l'architecture AVANT de l'utiliser pour produire. Donne le vocabulaire métier exact à l'IA. Verrouille avec des tests d'architecture.

Cette discipline ne ralentit pas la livraison. Elle empêche que la livraison devienne ingérable au bout de 6 mois.

---

## Pour aller plus loin

- 📖 **Article complet sur Medium** — [« MOUSSAVOU apprend DDD : le guide pratique du dev qui veut écrire du code qui tient »](https://medium.com/@bangaromaric/moussavou-apprend-ddd-le-guide-pratique-du-dev-qui-veut-%C3%A9crire-du-code-qui-tient-07a9192a3a42) (17 min, exemples Java complets, exercices)
- 💻 **Code source du cas d'étude** — [github.com/bangaromaric/mbolopay](https://github.com/bangaromaric/mbolopay)
- 🎯 **Démo en ligne** — [mbolopay.banga.ga](https://mbolopay.banga.ga/) (visualise le cycle d'une opération en slow-mo, observe les événements de domaine traverser les couches hexagonales)
- 🗂️ **Fiche projet MboloPay** — [/projects/mbolopay/]({{< ref "/projects/mbolopay" >}})
