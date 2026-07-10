---
title: "Google Antigravity : apprendre la culture de votre équipe à un agent IA en 2026"
heroTitle: "Un agent IA dans votre [équipe]"
date: 2026-06-15
draft: false
description: "Comment Google Antigravity transforme un agent IA générique en membre de l'équipe : Rules, Skills, Workflows, Tâches planifiées. Retour d'expérience GDG Libreville, Gabon."
categories: ["IA"]
tags: ["IA générative", "Antigravity", "Agents IA", "Culture tech", "Développement", "GDG", "Gabon"]
author: "BANGA Romaric"
slug: "google-antigravity-agent-culture"
showToc: false
cover:
    image: "/images/google-antigravity-agent-culture-cover.png"
    alt: "Google Antigravity : un agent IA aligné sur les règles d'une équipe (Rules, Skills, Workflows, Tâches planifiées), palette Google et ornements pagne, contexte GDG Libreville, par BANGA Romaric"
    caption: "Un agent qui s'imprègne de votre culture d'ingénierie plutôt que d'improviser sur les couleurs, la langue et la stack."
---

Mardi soir, après le boulot à l'ANINF. La chaleur lourde de Libreville commence à peine à retomber, mais dans la salle du GDG Libreville, les ventilateurs tournent à plein régime. Mavoungou, notre développeur frontend, fixe son écran avec une moue dubitative. Il vient de demander à un agent d'IA générative de concevoir la page d'accueil de notre prochain événement « Build with AI ».

La page est là. Elle tourne, elle compile, et techniquement, il n'y a pas d'erreur. Mais elle est désespérément froide. Rédigée en anglais, habillée de couleurs agressives sans aucun rapport avec notre identité, et bâtie sur un framework lourd qu'on s'interdit d'utiliser pour nos projets légers.

« C'est propre, mais c'est pas nous », murmure-t-il en coupant son serveur de dev.

Cette scène résume tout le paradoxe actuel. Les agents d'IA sont comme des stagiaires extrêmement brillants venus de l'autre bout du monde : ils connaissent les syntaxes par cœur, mais ils ne connaissent pas votre maison. Ils ignorent vos standards, votre charte, vos habitudes de code.

> 📝 **Note de terminologie (en clair).** Une IA générative classique *répond* : vous lui demandez une recette, elle vous la dicte, mais c'est vous qui faites les courses et qui cuisinez. Un **agent IA**, lui, *agit* : c'est le cuisinier à qui vous dites « prépare le dîner » et qui lit la recette, va au marché, cuisine, goûte, rectifie le sel et sert le plat. *Exemple actuel* : l'agent de ChatGPT (OpenAI) ou de Gemini (Google) à qui vous dites « réserve-moi une table pour samedi soir » et qui ouvre le web, compare et réserve à votre place. L'**IA agentique** (*agentic AI*), c'est ce mode de travail généralisé : on confie une mission complète à l'IA, qui planifie et enchaîne les étapes avec peu de supervision, quitte à coordonner plusieurs agents. *Exemple actuel* : Salesforce Agentforce, où des agents traitent une demande client de bout en bout (comprendre, chercher, résoudre). En 2026, c'est la grande bascule : l'IA passe d'« assistant qui répond » à « collègue qui exécute ».

C'est là qu'entre en scène **Google Antigravity**, un environnement de développement agentique conçu non pas pour coder à votre place à l'aveugle, mais pour s'imprégner de votre culture d'ingénierie. C'est, en un sens, le pendant lumineux d'une histoire plus sombre que j'ai racontée ailleurs : celle où l'IA [dissout ce qui unissait une équipe]({{< ref "/posts/ia-division-developpeurs" >}}). Ici, on ne subit pas l'agent : on lui apprend *notre maison* pour qu'il devienne un vrai membre de l'équipe. Voici comment, étape par étape.

---

## § I — Le point de départ : l'illusion de l'autonomie brute

Quand on lance un agent sans cadre, la première tentation est de lui jeter un prompt vague : *« Crée une page d'accueil web simple pour un événement tech. »*

L'agent s'exécute. Il planifie ses tâches, ouvre le terminal, écrit le code et lance un serveur local. Antigravity fait cela très bien grâce à un principe appelé **Review-Driven Development**. Avant de modifier la moindre ligne, il vous présente un `plan d'implémentation` et une `Task List`. C'est le premier étage de la confiance : la machine ne travaille pas en boîte noire, elle propose et vous validez. Le travail fini, elle vous montre une capture de son rendu : l'artefact `Walkthrough`.

Mais le résultat brut reste le même : une page générique. Une de plus sur le web. Le code est correct, sauf que l'agent a improvisé sur l'esthétique, la langue et l'architecture, parce qu'il n'avait aucune boussole.

> L'autonomie sans culture n'est pas de l'intelligence, c'est de la génération aléatoire bien élevée.

Pour que l'agent soit utile, il faut lui donner les règles du jeu.

---

## § II — Les règles du jeu (Workspace Rules)

Dans Antigravity, le premier levier de personnalisation s'appelle les `Rules`. Ce sont des instructions persistantes qui s'appliquent à toutes les conversations du projet, sans que vous ayez à les répéter dans vos prompts.

Pour notre événement, un atelier de la série [« Build with AI » de GDG Libreville](https://gdg.community.dev/events/details/google-gdg-libreville-presents-build-with-ai-decouvrez-google-antigravity-lere-du-developpement-pilote-par-les-agents-ia/), nous avons défini une règle courte dans le workspace :

```markdown
- Réponds toujours en français, avec un ton chaleureux ancré à Libreville / au Gabon.
- Palette principale : les 4 couleurs de Google (#4285F4, #EA4335, #F9AB00, #34A853),
  sur fond clair, texte #1E1E1E.
- Ajoute des touches visuelles gabonaises en ornements DISCRETS (motifs géométriques,
  masques Punu & Fang ou motifs wax) en réutilisant la palette Google.
- Code en HTML/CSS/JS pur, sans framework ni dépendance externe.
- Vérifie toujours le rendu dans le navigateur avant de conclure.
```

Ce n'est pas un exemple théorique : c'est notre fichier de règles réel, [`.agents/rules/agent.md`](https://github.com/bangaromaric/buildwithai/blob/master/.agents/rules/agent.md), celui qui a produit la page. Nous relançons l'agent avec un prompt tout aussi bref : *« Refais cette page d'accueil pour notre événement "Build with AI – Google Antigravity". »*

Le contraste est immédiat. En ouvrant le diff (les modifications de code que l'agent propose), on constate qu'il a appliqué nos consignes de lui-même. La page est en français. Le design reprend nos codes couleurs. Un motif géométrique inspiré du pagne orne subtilement le fond, en n'utilisant que les couleurs Google. Pas de React, pas de Tailwind importé en douce.

> L'agent a cessé de deviner. Il applique désormais les standards de la maison.

---

## § III — L'expertise mise en boîte (Skills)

La règle fixe le cadre général. Mais que se passe-t-il lorsque vous avez besoin d'un composant technique très précis, par exemple un compte à rebours pour le lancement de l'événement ?

Si vous demandez simplement *« Ajoute un compte à rebours jusqu'au 11 juillet 2026 à 19h »*, l'agent va l'improviser. Il écrira ses propres fonctions JavaScript, stylisera le compteur à sa façon, et recréera de la dette technique. C'est le comportement classique d'une IA générique.

C'est là qu'interviennent les `Skills`, un standard ouvert qu'Antigravity a adopté. Une Skill est un dossier contenant des instructions précises (`SKILL.md`) et des ressources (exemples de code, assets SVG) qui décrivent comment implémenter un composant selon vos règles de l'art.

Dans notre projet, nous avons configuré une skill [`gdg-branding`](https://github.com/bangaromaric/buildwithai/blob/master/.agents/skills/gdg-branding/SKILL.md), notre charte de marque complète, dont l'implémentation exacte d'un compte à rebours approuvé par l'équipe. Lorsque Mavoungou demande *« Refais le compte à rebours en respectant l'identité visuelle de GDG Libreville »*, le mécanisme s'enclenche :

1. **La découverte autonome** : l'agent scanne les compétences disponibles, détecte que la description de `gdg-branding` correspond à la demande, et lit le fichier d'instructions de lui-même.
2. **Le respect du standard** : il génère son plan en reprenant le code exact et la structure SVG de notre composant de référence.

Nous n'avons rien eu à expliquer sur *comment* coder le compteur. La Skill a servi de boîte à outils d'expertise dans laquelle l'agent a pioché pour rester cohérent avec le reste de l'écosystème.

Cette idée n'est pas neuve : elle a juste changé d'outil. C'est exactement la logique du **tool calling** que j'exploite dans mon [Assistant IA Gabonais]({{< ref "/projects/assistant-ia-gabon" >}}) : là, l'agent n'improvise pas les démarches administratives, il appelle des fonctions Spring au périmètre défini (`getRequiredDocuments`, `generateChecklist`). Une Skill Antigravity, c'est le même principe, côté outil de dev. Et c'est le prolongement direct de ce que je défends dans [« Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith »]({{< ref "/posts/architecture-ia-spring-modulith" >}}) :

> L'expertise ne se raconte pas au prompt. Elle se met en boîte pour devenir exécutable et reproductible.

---

## § IV — De la commande ponctuelle à l'industrialisation (Workflows & Tâches planifiées)

Une fois les règles et les composants maîtrisés, le problème devient celui de la répétabilité. Si vous devez créer une deuxième page (par exemple une page « Merci » après l'inscription), vous ne voulez pas réexpliquer toute la structure à l'agent.

C'est le rôle des `Workflows` : des guides textuels (fichiers `.md` dans `.agents/workflows/`) qui dictent à l'agent une procédure pas-à-pas pour une tâche récurrente. Le nôtre, [`create_page.md`](https://github.com/bangaromaric/buildwithai/blob/master/.agents/workflows/create_page.md), est ouvert sur GitHub. En tapant simplement :

```bash
/create_page  →  page « Merci »
```

L'agent charge le workflow, déroule la séquence, crée une structure HTML identique aux autres pages, applique la charte et livre le fichier fini. Zéro blabla, zéro déviation. On passe de la création artisanale à l'industrialisation.

Mais on peut aller plus loin encore avec les `Tâches planifiées` (*Scheduled Tasks*). Un agent classique attend sagement que vous cliquiez sur « Envoyer ». Un agent Antigravity peut être programmé pour s'exécuter en tâche de fond, de façon récurrente. Imaginez vouloir rafraîchir chaque matin le nombre d'inscrits affiché sur la page :

```bash
/schedule chaque jour à 8h, mets à jour le compteur d'inscrits sur la page d'accueil et régénère-la.
```

L'agent s'exécute en arrière-plan, modifie le fichier de façon autonome et produit un rapport de progression dans ses logs.

> L'IA cesse d'être un assistant qu'on sollicite au coup par coup. Elle devient un *daemon* (au sens informatique : un processus qui tourne en silence en arrière-plan), un collaborateur discret qui gère ses propres tâches récurrentes pendant que vous vous concentrez sur l'essentiel.

---

## § V — Garder les rênes : le Review-Driven Development

L'autonomie de la machine peut faire peur. Si Mavoungou ou Ndong confient des générations entières à un agent, comment s'assurer qu'il ne casse pas l'architecture du projet ou n'introduit pas de faille de sécurité ?

La réponse tient dans les **artefacts** qu'Antigravity produit à chaque étape. Le Review-Driven Development (l'un des deux modes de revue proposés au démarrage, le plus prudent) est un garde-fou structurel :

- L'agent ne commite rien sans votre accord : il affiche son `plan d'implémentation` et attend que vous l'approuviez.
- Il montre ses résultats de manière visuelle : captures d'écran, enregistrements navigateur, logs d'exécution. Notre règle lui impose d'ailleurs de vérifier chaque rendu via un subagent `/browser` avant de conclure.
- Il fournit le diff précis de chaque fichier modifié.

Ce dialogue constant entre l'humain et l'agent garantit que le développeur reste seul maître à bord. L'agent propose le chemin ; c'est vous qui tenez le volant.

En transmettant notre culture (`Rules`), nos composants de référence (`Skills`) et nos méthodes (`Workflows`) à l'agent, nous avons arrêté de nous battre contre des templates génériques crachés par des serveurs lointains. Nous avons construit un outil qui respecte le travail de l'équipe, de Libreville au reste du monde. La page « Build with AI » qui en est sortie est [ouverte sur GitHub](https://github.com/bangaromaric/buildwithai), en HTML/CSS/JS pur, exactement comme nos règles l'exigeaient.

Et c'est peut-être ça, au fond, le vrai rôle de l'IA dans nos équipes. Non pas dissoudre ce qui nous liait, mais nous décharger de la répétition pour nous rendre le temps de concevoir des architectures qui durent, et de choisir, enfin, la collaboration qu'on veut vraiment.

*Et dans votre équipe : laissez-vous l'agent improviser, ou lui avez-vous déjà appris votre maison ?*

---

## Amener l'IA agentique dans votre équipe

Apprendre à un agent à respecter votre culture, ça ne s'improvise pas : ça s'outille. C'est concrètement ce que je fais avec les équipes, ici au Gabon et ailleurs en zone francophone :

- 🎓 **Formation entreprise** : structurer le travail agentique (`Rules`, `Skills`, `Workflows`, revue de code générée par l'IA) pour que l'agent produise *votre* code, pas un template générique. [Voir les formats →](/about/#services)
- 🧭 **Consulting & audit** : intégrer un agent qui respecte votre charte, votre langue et votre stack, sans hypothéquer votre architecture. [Discutons d'un projet](mailto:bangaromaric@gmail.com)
- 📖 **Aller plus loin** : [« L'IA et la division silencieuse des équipes »]({{< ref "/posts/ia-division-developpeurs" >}}) (l'envers du décor) et [« Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith »]({{< ref "/posts/architecture-ia-spring-modulith" >}}) (le pendant technique : rendre l'expertise exécutable).
- 💻 **Code source** : la page « Build with AI » construite avec Antigravity dans cette histoire, en HTML/CSS/JS pur : [github.com/bangaromaric/buildwithai](https://github.com/bangaromaric/buildwithai).
- 🧪 **Cas concret** : [Assistant IA Gabonais]({{< ref "/projects/assistant-ia-gabon" >}}), où un agent Spring AI reste cadré par le tool calling plutôt que de halluciner.
- 🌍 **Communauté** : [GDG Libreville](/gdg/) et ses ateliers « Build with AI », d'où vient cette histoire.

*Le code de nos ateliers « Build with AI » est [ouvert sur GitHub](https://github.com/bangaromaric/buildwithai), et si vous voulez qu'on parle d'agents, d'archi Spring/GCP ou juste boire un café au prochain meetup GDG Libreville, écrivez-moi via [ban.ga](https://ban.ga/). Mbolo.*

#Antigravity #IAGenerative #AgentsIA #GDGLibreville #AfricaTech #Gabon
