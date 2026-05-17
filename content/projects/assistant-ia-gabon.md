---
title: "Assistant IA [Gabonais]"
tagline: "Un compagnon conversationnel pour rendre les démarches administratives gabonaises intelligibles, en français parlé et écrit."
description: "Prototype Spring AI d'assistant administratif gabonais — reconnaissance vocale, tool calling, Spring Boot. Pionnier de l'IA générative au service du citoyen."
date: 2024-09-20
year: 2024
role: "Conception · Développement · Prompt engineering"
client: "Projet personnel"
duration: "3 mois"
status: "Démo en ligne"
stack: ["Spring AI", "Spring Boot", "Spring Data JPA", "H2", "JavaScript", "Web Speech API"]
technologies: ["Spring AI", "Spring Boot", "H2 Database", "JavaScript", "Spring Data JPA"]
appType: "WebApplication"
github: "https://github.com/bangaromaric/spring-ai"
demo: "https://lnkd.in/eVx6Gxpi"
article: "https://medium.com/@bangaromaric/boostez-votre-application-spring-boot-avec-lia-g%C3%A9n%C3%A9rative-spring-ai-et-tool-calling-fc9fe16cd8e7"
featured: true
weight: 1
showToc: false
---

## Le problème

L'administration gabonaise reste largement papier et guichet. Trouver la bonne pièce, le bon bureau, le bon créneau prend des heures de recherche éparse — quand l'information existe en ligne, elle est fragmentée entre plusieurs sites institutionnels, jargon administratif compris.

Pour un citoyen qui veut renouveler son passeport, son acte de naissance ou son permis, le coût d'entrée est cognitif autant qu'administratif.

## La proposition

Un assistant conversationnel disponible 24h/24, accessible au clavier *et à la voix*, qui répond en français naturel — pas en formulaires.

L'utilisateur demande *« Comment je fais pour mon passeport ? »* et reçoit une réponse contextuelle : pièces requises, frais, lieux, délais, alternatives selon sa situation. L'assistant pose des questions de clarification quand c'est utile et génère des checklists personnalisées.

## Comment c'est fait

L'architecture repose sur **Spring AI** côté serveur, avec deux mécaniques principales :

- **Prompt engineering ciblé** — un system prompt contextualisé pour le cadre administratif gabonais, alimenté par une base H2 listant les démarches, pièces, autorités compétentes et délais.
- **Tool calling** — l'assistant expose des fonctions Spring (`getRequiredDocuments`, `generateChecklist`, `findNearestOffice`, `estimateProcessingTime`) que le LLM peut invoquer dynamiquement selon la requête.

```java
@Service
public class GabonAdministrationService {

    @Value("classpath:prompts/gabon-admin-system.st")
    private Resource systemPrompt;

    public String processUserQuery(String query, UserContext context) {
        return chatClient.prompt()
            .system(systemPrompt)
            .user(query)
            .functions("getRequiredDocuments", "generateChecklist")
            .call()
            .content();
    }
}
```

Côté frontend, l'interface utilise la **Web Speech API** pour la reconnaissance vocale, et reste volontairement minimaliste — une boîte de chat, un bouton micro, le suivi conversationnel.

## Mesures issues du prototype

Sur les sessions tests menées avec un panel de 20 utilisateurs :

- **Latence** inférieure à 2 secondes en moyenne sur les requêtes courantes
- **95 % de précision** sur les informations administratives factuelles
- **98 % de reconnaissance** vocale en français avec accent local
- **85 %** des utilisateurs préfèrent l'interaction vocale au texte
- **20+ démarches** couvertes par la base initiale

## Démonstration

- **Vidéo** — [démonstration complète sur YouTube](https://www.youtube.com/watch?v=nS9LKyFFRYk)
- **Article technique** — [Medium, février 2025](https://medium.com/@bangaromaric/boostez-votre-application-spring-boot-avec-lia-g%C3%A9n%C3%A9rative-spring-ai-et-tool-calling-fc9fe16cd8e7)
- **Code source** — [github.com/bangaromaric/spring-ai](https://github.com/bangaromaric/spring-ai)

## Ce que le projet a appris

Trois choses se confirment au fil des tests. D'abord, le **tool calling Spring AI** est aujourd'hui assez stable pour bâtir des assistants à scope défini sans tomber dans la fabulation. Ensuite, la **voix change le rapport à l'administration** — pour des publics seniors ou ruraux, taper est une barrière que parler franchit instantanément. Enfin, le contexte local compte : un modèle généraliste rate les particularités gabonaises sans prompt soigneusement préparé.

Ce prototype n'a pas vocation à se substituer aux services publics. C'est une démonstration de ce que l'IA générative peut faciliter, dans un cadre éthique transparent — toutes les sources sont citées, le code est ouvert, les données restent locales.
