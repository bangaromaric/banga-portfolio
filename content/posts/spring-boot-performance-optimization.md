---
title: "Optimiser les performances Spring Boot en production"
date: 2024-09-10
description: "Cinq années de mise en production Spring Boot, distillées en six leviers concrets — JVM, connexions DB, JPA, cache, monitoring."
tags: ["Spring Boot", "Performance", "Java", "JVM"]
categories: ["Backend"]
draft: false
showToc: false
---

Cinq années de mises en production Spring Boot m'ont laissé une liste courte de leviers qui rapportent vraiment. Les voici, sans tableau de classement ni promesse de miracle — juste ce que je vérifie en priorité quand une application tousse.

## JVM — ce qui se règle avant tout le reste

La JVM par défaut est rarement adaptée à votre charge réelle. Trois flags couvrent 80 % des cas :

```bash
-Xms2g -Xmx4g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:+UseStringDeduplication
```

Allouer `Xms` et `Xmx` à la même valeur évite les redimensionnements de heap pendant les pics. G1GC est le bon défaut pour la plupart des applications web modernes. La déduplication de chaînes coûte peu et économise sensiblement la mémoire sur les services à fort volume de strings (logs, sérialisation JSON).

## Pool de connexions HikariCP

Le pool de connexions est l'endroit où la plupart des applications meurent silencieusement.

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 20000
      idle-timeout: 300000
```

Règle de pouce contre-intuitive : **moins de connexions est souvent plus rapide**. Un pool sous-dimensionné fait la queue ; un pool surdimensionné effondre la base. Mesurez avant d'augmenter.

## JPA — les trois pièges classiques

Trois optimisations JPA évitent 90 % des problèmes que je rencontre :

- **Lazy loading discipliné** — savoir où il est, savoir quand il déclenche
- **Batch processing** sur les insertions massives (`spring.jpa.properties.hibernate.jdbc.batch_size`)
- **N+1 queries** éliminées avec `@EntityGraph` ou `JOIN FETCH`

## Monitoring — sans cela, le reste est aveugle

Micrometer pour les métriques applicatives. Les GC logs activés et conservés. JProfiler ou async-profiler pour les sessions de profiling ponctuelles. Sans une vue continue, chaque optimisation est un pari.

## Résultats observés sur une application réelle

Sur une plateforme e-commerce gabonaise traitant ~10 000 requêtes/minute, l'application combinée de ces six leviers a donné :

- Temps de réponse médian — **800 ms → 320 ms** (−60 %)
- Consommation mémoire — **−40 %**
- Throughput — **+150 %**

## Ce que j'ai appris à arrêter de faire

J'évite désormais d'**optimiser avant de mesurer**. J'évite de **changer plusieurs variables à la fois** — sinon impossible d'attribuer le gain. Et j'évite les **micro-optimisations** qui complexifient le code pour un gain marginal alors qu'un index manquant en base coûte 100× plus.

L'optimisation est un processus itératif. Mesurer, isoler, corriger, remesurer.
