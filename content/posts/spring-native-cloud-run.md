---
title: "Spring Native + Cloud Run — cold-start ÷18, RAM ÷3 sur MboloPay | Gabon"
heroTitle: "Cold-start [÷18] avec Spring Native"
date: 2026-05-19
description: "Cold-start Spring Boot ÷18 et RAM ÷3 avec Spring Native + GraalVM sur Cloud Run. Benchmark mesuré au Gabon, 5 pièges Windows, profil Maven -Pnative."
tags: ["Spring Native", "GraalVM", "Spring Boot", "Cloud Run", "Java", "Performance", "DevOps", "GCP"]
categories: ["Architecture"]
draft: false
showToc: true
cover:
    image: "/images/spring-native-cloud-run-cover.jpg"
    alt: "Architecture Spring Native + GraalVM + Google Cloud Run — flow de compilation AOT vers déploiement serverless, par Romaric BANGA"
    caption: "Spring → GraalVM AOT → image OCI → Cloud Run serverless"
---

23 h 47, un dimanche soir à Libreville, au Gabon. MOUSSAVOU, la développeuse de mon article précédent — [*« Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith »*]({{< ref "/posts/architecture-ia-spring-modulith" >}}) —, vient d'envoyer un screenshot sur le WhatsApp de l'équipe. Le screenshot, c'est la console Cloud Run en prod. Six mois de boulot. PayApp, sa fintech fictive de Libreville, vient enfin de pousser son MVP en ligne. Et ça crashe.

Pas un crash franc, propre, qu'on lit dans une stack-trace. Le pire genre de crash : un crash *silencieux*. L'API tourne. Les endpoints répondent. Mais une requête sur trois retourne un timeout côté mobile. Les utilisateurs entrent leur OTP, attendent 4 secondes, voient *« Connexion impossible »*, ferment l'app. MOUSSAVOU regarde les logs : `Started PayAppApplication in 3.842 seconds`. À chaque cold-start. Cloud Run scale à zéro quand personne ne se connecte la nuit ; au premier appel du matin, l'instance met **presque 4 secondes** à booter, et l'OTP arrive avant que Spring soit prêt à le valider.

Et c'est là que ça pique économiquement. Un cold-start de 3,8 secondes, c'est **3,8 secondes de vCPU et de RAM facturées par Cloud Run** — qu'il y ait une transaction qui aboutisse au bout, ou pas. Chaque utilisateur qui timeout retry. Chaque retry réveille une nouvelle instance, donc un nouveau cold-start. La nuit où personne ne se connecte, `min-instances=0` maintient bien le coût à zéro — comme prévu. Mais le matin, 200 utilisateurs qui re-tentent leur OTP trois fois chacun, ça fait 600 cold-starts × 3,8 s = **2 280 vCPU-secondes brûlées avant qu'une seule transaction ne réussisse**. Plus 182 GB-secondes de RAM, pour la même raison. Le scale-to-zero protège la facture la nuit ; il ne fait rien contre les pics d'échec en cascade le matin.

Le lundi matin, premier dépassement du free tier. Quelques milliers de FCFA. Pour PayApp, c'est rien. Pour MOUSSAVOU qui paye son cloud avec sa bourse de fin d'études, c'est un choc. Sa première vraie facture cloud, et elle ne comprend pas encore pourquoi.

C'est cette histoire que je raconte ici. Comment passer d'un cold-start Spring Boot de **3 740 ms** à **205 ms**. Comment diviser la RAM par 3. Comment ramener une facture Cloud Run à zéro. Pas avec une astuce. Avec un compilateur qui s'appelle GraalVM et un projet qui s'appelle **Spring Native**.

## Pourquoi un Spring Boot JVM rame au démarrage

Pour comprendre pourquoi le cold-start fait mal, il faut comprendre ce qu'une JVM Java 25 fait pendant ces 3,7 secondes. Spoiler : elle ne *rame* pas. Elle travaille. Beaucoup.

Quand `java -jar app.jar` se lance, voici ce qui se passe, dans l'ordre :

D'abord, le **classpath scan**. Spring Boot ouvre ton JAR, énumère tous les `.class`, et cherche les annotations : `@Component`, `@Service`, `@Repository`, `@Configuration`. Sur MboloPay, qui dépend de Spring Boot 4.0.2 + Spring Modulith 2.0.2 + Hibernate 7.2.1, ça représente plusieurs milliers de classes à scruter. Chaque annotation déclenche une décision : faut-il créer un bean ? Quelles dépendances injecter ?

Ensuite, **l'initialisation Hibernate**. Le scanner parcourt toutes les entités JPA, lit les mappings, génère le schéma DDL en mémoire, valide les contraintes. Sur MboloPay c'est rapide parce que les bounded contexts sont petits ; sur une vraie fintech avec 80 entités, ça prend une seconde à lui tout seul.

Puis **le pool de connexions HikariCP**. Il ouvre les 10 connexions par défaut (parfois moins, parfois plus), chacune nécessitant un handshake TCP + auth. Quand la DB est sur la même VPC, ça va vite. Quand elle est ailleurs, ça respire.

Enfin, **Tomcat**. Il monte sur le port 8080, enregistre les servlets, valide les filtres, et seulement là le `Started Application in X.YYY seconds` apparaît dans les logs.

Pendant tout ce temps, la JVM utilise le **JIT** (Just-In-Time compiler) qui transforme le bytecode en code machine **au fur et à mesure** que les méthodes sont appelées. Le JIT est génial pour les apps qui tournent longtemps : il apprend à optimiser le code chaud après quelques minutes. Mais au démarrage, il n'a rien appris encore, donc tout est interprété ou en mode C1 (peu optimisé).

Imagine un kiosque mobile money à Libreville. Le matin, le caissier ouvre le rideau, branche son terminal, attend que la connexion 4G se stabilise, vérifie son float Airtel et Moov, range les pièces de monnaie par dénomination. Quinze minutes avant qu'il puisse vendre quoi que ce soit. C'est la JVM. Elle ne *rame* pas. Elle s'organise.

Le problème, c'est que Cloud Run te facture à la seconde pendant ces 15 minutes de mise en place. Et que tes clients, eux, sont déjà devant le rideau.

## Spring Native, c'est quoi exactement ?

Spring Native, c'est Spring qui dit à GraalVM : *« regarde mon code, devine TOUT à l'avance, compile-moi un binaire qui démarre comme un kiosque qui n'a rien à organiser parce qu'il a tout préparé la veille »*.

Sous le capot, c'est **GraalVM Native Image**. Un compilateur AOT — *Ahead-of-Time* — qui prend ton bytecode Java et le transforme en exécutable natif (`.exe` sous Windows, ELF sous Linux). Plus de JVM au runtime. Plus de JIT. Plus de classpath scan. Plus de réflexion paresseuse. Tout est résolu à la compilation.

Le compilateur fait ce qu'on appelle de la **closed-world analysis** : il considère que ton application est fermée, qu'aucune classe ne sera ajoutée au runtime, qu'aucun proxy dynamique ne sera créé à la volée. À partir de là, il peut suivre toutes les références depuis le `main()`, marquer les classes utilisées, jeter le reste, et compiler le minimum vital.

L'image native qui en sort est plus grosse en taille (~180 Mo vs ~50 Mo pour le JAR) parce qu'elle embarque la libc, les libs JDK essentielles, ses propres routines de garbage collection. Mais elle démarre **instantanément** parce qu'il n'y a plus rien à initialiser : tout est déjà initialisé en mémoire au moment où le binaire commence à exécuter `main()`.

Quand je préparais la certification Spring Pro 2024 v2, j'ai compris que la vraie magie n'était pas GraalVM. C'était l'intégration **Spring AOT**. Spring Boot 4 inclut désormais un plugin Maven, `spring-boot-maven-plugin:process-aot`, qui s'exécute **avant** la compilation native. Ce plugin lit ta configuration, simule le démarrage Spring, calcule à l'avance quelles classes seront utilisées, quels beans seront créés, quels endpoints seront exposés. Il génère du code Java qui *remplace* la réflexion runtime par du code direct. Puis GraalVM compile ce code direct.

> 💡 **L'éclair de compréhension** : Spring Native n'est pas une nouvelle façon d'écrire Spring. Ton code reste exactement le même — `@RestController`, `@Service`, `@Repository`, `@Transactional`, tout marche. Ce qui change, c'est le *quand* : ce que Spring fait normalement au démarrage de la JVM, il le fait maintenant au moment du `mvnw -Pnative`. Le runtime n'a plus rien à apprendre, il sait déjà.

La contrepartie de la closed-world analysis, c'est qu'elle n'aime pas les surprises. Tout ce qui repose sur de la réflexion dynamique, des proxies créés à la volée, des classes chargées par `Class.forName(nom)` à partir d'une string lue dans un fichier de config — tout ça ne marche pas par défaut. Il faut **prévenir GraalVM** que ces classes existent, via des *hints* (annotations `@RegisterReflectionForBinding`, configurations JSON `reflect-config.json`, ou processeurs `RuntimeHintsRegistrar`).

La bonne nouvelle : Spring Boot 4 connaît son propre framework, donc il génère automatiquement les hints pour 80 % des cas (les annotations Spring, JPA, Jackson, Web). Les 20 % restants — typiquement les libs tierces ou un usage exotique — demandent des hints custom. On y reviendra dans la section sur les pièges.

## Le benchmark MboloPay

Voici les mesures réelles, faites sur [MboloPay]({{< ref "/projects/mbolopay" >}}), sur ma machine Windows, le 16 mai 2026, avec Spring Boot 4.0.2, Java 25, Liberica NIK 25, Hibernate 7.2.1, Tomcat 11.0.15, H2 en mémoire. Pas un benchmark inventé sur Twitter. Des secondes mesurées au chronomètre des logs Spring.

| Étape | JVM Java 25 | Natif GraalVM | Gain |
|---|---|---|---|
| Boot → Tomcat init | 1 207 ms | 36 ms | ×33 |
| Hikari pool startup | 559 ms | 65 ms | ×8.6 |
| JPA init | 774 ms | 14 ms | ×55 |
| JPA → Tomcat 8080 | 875 ms | 76 ms | ×11.5 |
| **Total « Started in »** | **3 740 ms** | **205 ms** | **×18.2** |
| RAM résident | ~250 Mo | ~80 Mo | ÷3 |
| Taille livrable | ~50 Mo JAR | ~120-180 Mo binaire | ×3 |
| Build time | ~10 s | ~2 min local / 7-12 min CI | ×12 |

Quelques observations qui valent plus que les chiffres bruts.

**Ligne 1 — Boot → Tomcat init (×33)**. C'est là que la closed-world analysis gagne le plus. La JVM passe 1,2 seconde à scanner les classes annotées dans tous les JARs du classpath. Le binaire natif a déjà résolu tout ça à la compilation : il sait à 36 ms quels beans existent.

**Ligne 3 — JPA init (×55)**. Hibernate fait beaucoup de réflexion pour mapper entités → tables. AOT pré-calcule ce mapping. Le runtime n'a plus qu'à brancher.

**Ligne 5 — Total (×18.2)**. C'est le chiffre à retenir. 3,74 secondes deviennent 205 ms. Si ton service Cloud Run scale à zéro la nuit et redémarre au premier appel le matin, l'utilisateur attend 205 ms au lieu de 3,7 secondes. Sur un OTP fintech, c'est la différence entre une transaction qui passe et une transaction perdue.

**Ligne 6 — RAM ÷3**. 250 Mo deviennent 80 Mo. Sur Cloud Run, ça veut dire que tu peux baisser ton allocation mémoire de 512 MiB à 256 MiB, et payer la moitié de ce que tu paies par instance-seconde.

**Ligne 7 — Taille ×3 (le compromis)**. Le binaire natif est trois fois plus gros que le JAR. Si tu pushes ton image sur Artifact Registry tous les jours, ça finit par coûter de la bande passante. Pas une catastrophe, mais à noter.

**Ligne 8 — Build time ×12 (l'autre compromis)**. Compiler le binaire prend 2 minutes en local sur ma machine, et 7 à 12 minutes en CI (Cloud Build, GitHub Actions, GitLab CI). C'est la limite. Si tu déploies 30 fois par jour, tu vas attendre. Si tu déploies une fois par jour ou deux fois par semaine, c'est invisible.

> ⚠️ **Piège classique** : ne compare pas le *steady-state* de la JVM (après warm-up JIT) avec le natif. À chaud, la JVM peut être *plus rapide* qu'AOT sur certaines opérations parce que le JIT a optimisé le code en fonction du profile d'exécution réel. Le gain du natif est sur le **démarrage** et l'**empreinte mémoire**, pas sur le débit en charge soutenue.

## Le profil Maven `-Pnative`

C'est la partie qui surprend toujours quand je la montre. Active la compilation native sur un projet Spring Boot 4, ça tient en deux déclarations Maven. Tout le reste est dans le parent POM Spring Boot.

Extrait de `pom.xml` de MboloPay (visible sur GitHub) :

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.graalvm.buildtools</groupId>
            <artifactId>native-maven-plugin</artifactId>
        </plugin>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

Et c'est tout. Pas de version explicite (gérée par `spring-boot-starter-parent`). Pas de configuration custom. Pas de `<executions>` à câbler. Quand tu lances :

```bash
./mvnw -Pnative native:compile
```

Le profile `native` est défini par le parent POM `spring-boot-starter-parent` de Spring Boot 4. Il active automatiquement l'exécution `process-aot` du `spring-boot-maven-plugin`, qui génère le code AOT dans `target/spring-aot/main/sources`. Puis le `native-maven-plugin` invoque `native-image` (Liberica NIK 25) sur le résultat.

Pour produire une image Docker directement, c'est encore plus simple :

```bash
./mvnw -Pnative spring-boot:build-image
```

Spring Boot délègue à **Paketo Buildpacks** — précisément au builder `paketobuildpacks/builder-noble-java-tiny`, optimisé pour les images natives Java. Pas de Dockerfile à écrire. Le buildpack détecte que tu es en mode natif, télécharge GraalVM, compile, et produit une image OCI minuscule (Ubuntu Noble distroless-like) prête à pousser sur Artifact Registry.

> **À retenir** : la philosophie Spring Boot 4 est *« si tu suis les conventions, on s'occupe de tout »*. Pas de `@ImportRuntimeHints` à câbler. Pas de `RuntimeHintsRegistrar` custom. Pour 80 % d'une app Spring standard (Web + Data JPA + Modulith), tu ne touches rien d'autre que les deux plugins ci-dessus. Les 20 % restants, ce sont les hints pour les libs tierces ou les usages exotiques. Pile ce qu'on va voir maintenant.

## Les 5 pièges qui te font perdre 2 jours

Tout ce qui précède donne l'impression que c'est facile. Ça l'est, quand tu connais les pièges. Voilà ceux qui m'ont fait perdre du temps. Quand MOUSSAVOU a basculé en natif, elle est tombée sur exactement les trois premiers en deux jours.

### Piège 1 — La console H2 ne marche plus

C'est le piège qui pique. En mode JVM, `http://localhost:8080/h2-console` te donne une UI pratique pour inspecter ta base H2 en dev. En mode natif, tu vois une page blanche et un log d'erreur cryptique. La servlet H2 utilise de la réflexion dynamique qui n'est pas pré-enregistrée dans les hints AOT.

> **Solution honnête** : pour la dev locale, utilise la JVM standard (`./mvnw spring-boot:run`). Le mode natif est pour la prod ou pour mesurer le cold-start. Si tu veux vraiment l'h2-console en natif, il faut écrire un `RuntimeHintsRegistrar` custom qui enregistre toutes les classes de la servlet H2 — quelques dizaines de lignes, faisable mais pénible.

### Piège 2 — Spring Boot DevTools est ignoré

Tu as ajouté `spring-boot-devtools` à ton pom.xml. En JVM, il te donne du hot-reload : tu sauvegardes un fichier, l'app redémarre toute seule en 2 secondes. En natif, DevTools est **ignoré silencieusement**. Pas d'erreur, pas de log. Juste : ton hot-reload ne marche pas.

C'est logique : DevTools repose sur un classloader custom qui recharge les classes à chaud. Un binaire natif n'a pas de classloader. Il n'a plus que du code machine compilé. Tu ne peux pas hot-reloader du code machine.

**Solution** : dev en JVM, prod en natif. Comme pour H2.

### Piège 3 — Les erreurs AOT bloquent le build

L'AOT processing tourne **avant** la compilation native. Si ton code a une erreur que l'AOT détecte (typiquement : un bean qui dépend d'une classe absente, une circularité, une config invalide), le build s'arrête là. Aucun binaire ne sort.

L'erreur typique ressemble à ça :

```
[ERROR] Failed to execute goal org.springframework.boot:spring-boot-maven-plugin:4.0.2:process-aot
[ERROR] Caused by: java.lang.IllegalStateException: Failed to read candidate component class
```

C'est un faux ami : tu crois que c'est un problème natif, c'est en réalité un problème Spring détecté plus tôt qu'à la normale. Le fix est généralement de corriger la config Spring (un `@Bean` mal annoté, un `@ConditionalOnProperty` sans valeur), pas de toucher à GraalVM.

> **Méthode debug** : commence par t'assurer que `./mvnw spring-boot:run` démarre sans warning. Si la JVM démarre proprement, l'AOT démarrera aussi neuf fois sur dix.

### Piège 4 — Liberica NIK ≠ Liberica JDK

Celui-là, c'est le grand classique qui fait perdre une demi-journée parce qu'on ne comprend pas le message d'erreur.

Spring Boot 4 exige Java 25 baseline. Tu as installé Liberica JDK 25. Tu lances `./mvnw -Pnative native:compile`. Tu obtiens :

```
native-image is not installed in your JAVA_HOME
```

Tu lances `native-image --version` dans un terminal. Tu obtiens `command not found`.

Le problème : tu as installé la **JDK** Liberica 25, pas le **NIK** (Native Image Kit). La JDK seule ne contient pas `native-image.cmd`. Il te faut **Liberica NIK 25**, une distribution séparée qui inclut JDK + GraalVM + native-image.

**Source officielle** : <https://bell-sw.com/pages/downloads/native-image-kit/>. Cocher *Full* + ton OS + ton archi. Pendant l'installation Windows, cocher *Add to PATH* + *Set JAVA_HOME*. Puis **fermer tous les terminaux**, en ouvrir un nouveau, vérifier :

```cmd
java --version
echo %JAVA_HOME%
native-image --version
```

Les trois doivent retourner du Java 25 / Liberica NIK 25.

Et sous Windows uniquement, prévois **Visual Studio Build Tools** en plus : GraalVM Native Image utilise `cl.exe` (le compilateur MSVC) pour produire le binaire. Sans MSVC, tu obtiens `Error: Failed to find 'vcvarsall.bat'`. Télécharge les Build Tools (charge de travail « Développement Desktop en C++ »), puis lance la compilation depuis le « x64 Native Tools Command Prompt for VS 2022 » — ce terminal charge l'environnement MSVC automatiquement.

### Piège 5 — `docker-credential-gcr` obligatoire sous Windows

Celui-là, je l'ai vécu douloureusement la première fois que j'ai voulu pousser une image native sur Artifact Registry depuis Windows. Tu as `gcloud` installé. Tu as fait `gcloud auth login`. Tu lances `./mvnw -Pnative spring-boot:build-image` qui prend 5-10 minutes à compiler. À la toute fin, au moment du push, l'erreur tombe :

```
Cannot run program "docker-credential-gcloud": CreateProcess error=2
```

Sur macOS et Linux, `gcloud auth configure-docker` installe correctement un helper. Sur Windows, il configure un helper qui pointe sur `docker-credential-gcloud.exe`… qui n'existe pas dans le PATH. Il faut installer **docker-credential-gcr** séparément, l'ajouter au PATH utilisateur, et le configurer :

```cmd
docker-credential-gcr configure-docker --registries=<region>-docker.pkg.dev
```

Et au passage, ne pas oublier de faire `gcloud auth application-default login` (ADC) en plus de `gcloud auth login`. Ce sont **deux mécanismes d'authentification distincts**. Le premier authentifie la CLI `gcloud`. Le second écrit les credentials que les SDKs et helpers (comme docker-credential-gcr) utilisent. Sans les deux, le push échoue avec `auth: "invalid_grant" "Bad Request"` — **après 10 minutes de build**. C'est rageant.

Quand MOUSSAVOU m'a envoyé le screenshot de l'erreur sur WhatsApp, j'ai souri tristement — parce qu'elle venait de vivre, à la lettre, ce que j'avais vécu un an plus tôt en déployant une appli Spring interne à l'**ANINF**, l'agence où je travaille depuis 7 ans. Exactement la même matinée perdue, exactement la même erreur cryptique d'ADC. Sauf que MOUSSAVOU, elle, n'a pas eu à creuser 4 heures pour comprendre : je lui ai juste envoyé le petit garde-fou que cette expérience m'avait poussé à coder, un script qui vérifie l'ADC avant tout `mvnw build-image` — pas le luxe d'attendre 10 minutes pour découvrir que les credentials sont expirés. Elle l'a immédiatement reproduit dans son propre pipeline PayApp. C'est ce script-là qu'on va décortiquer maintenant.

## Le déploiement sur Cloud Run

Une fois le binaire compilé et l'image OCI poussée sur Artifact Registry, le déploiement Cloud Run tient en une commande :

```bash
gcloud run deploy <service-name> \
    --image <region>-docker.pkg.dev/<your-project>/<repo>/mbolopay:latest \
    --region <region> \
    --platform managed \
    --allow-unauthenticated \
    --cpu 1 \
    --memory 512Mi \
    --concurrency 80 \
    --min-instances 0 \
    --max-instances 5
```

Décortiquons. **CPU 1 / Memory 512Mi** suffit largement pour le binaire natif (80 Mo de RAM, on a 6× la marge). **Concurrency 80** : chaque instance encaisse jusqu'à 80 requêtes en parallèle avant que Cloud Run en démarre une nouvelle. **min-instances 0** : c'est le levier financier — quand personne ne t'appelle, tu paies zéro. **max-instances 5** : protection anti-bombe, au-delà tu refuses ou tu fais la queue.

Le workflow conceptuel ressemble à ça :

{{< figure src="/images/spring-native-cloud-run-workflow.jpg" alt="Pipeline CI/CD Spring Native vers Cloud Run en six étapes : code Spring + pom.xml, build via Paketo Buildpack, génération d'une image OCI stratifiée, stockage sur Artifact Registry, déploiement par gcloud run deploy, exécution sur Cloud Run serverless — illustration isométrique avec motif pagne ouest-africain par Romaric BANGA" caption="Du code Spring au service Cloud Run : six stations, un artefact qui voyage de gauche à droite puis revient se déployer." loading="lazy" >}}

Pour MboloPay, le service tourne dans **une région européenne**, avec un **custom domain mappé** sur `mbolopay.banga.ga`. Le mapping DNS prend ~5 minutes à propager la première fois, puis c'est invisible.

La cert Google Cloud Engineer m'avait fait comprendre une nuance importante : Cloud Run en mode serverless te facture deux choses, le CPU-seconde et la mémoire-seconde, **uniquement quand une instance est active**. Quand `min-instances=0` et qu'aucune requête n'arrive, ton coût est strictement zéro. Pas « presque zéro ». Zéro.

> ⚠️ **Piège que j'ai vu en mission** : laisser `min-instances 1` « pour éviter les cold-starts ». En natif, le cold-start est de 205 ms — c'est imperceptible. Garder 1 instance chaude 24/7 te facture en continu pour aucun bénéfice mesurable. Reste à `min-instances 0` sauf si tu as un SLA de cold-start < 100 ms et un trafic vraiment intermittent.

Pour les permissions, le service tourne sous un service account dédié (placeholder `<service-account>@<your-project>.iam.gserviceaccount.com`) avec uniquement les rôles IAM nécessaires — accès lecture Artifact Registry, et ce dont l'app a besoin pour ses dépendances (typiquement Secret Manager pour les credentials DB, Cloud SQL pour la base de prod). Le principe de moindre privilège n'est pas une option.

## Le pipeline automatisé

Justement, ce script. Sur MboloPay, c'est [~200 lignes de PowerShell à la racine du repo](https://github.com/bangaromaric/mbolopay/blob/main/cloudRunDeploy.ps1) qui enchaînent toute la séquence sans intervention manuelle. Le code complet est public sur GitHub — forkable tel quel, il suffit d'y mettre tes propres project ID, region et nom d'image en haut du fichier. Conceptuellement, voici ce qu'il fait, dans l'ordre — la même séquence que MOUSSAVOU a finalement adaptée pour PayApp :

1. **Vérifications prérequises** : Docker Desktop tourne, `gcloud auth` est valide, ADC est en place, `docker-credential-gcr` est dans le PATH. Si l'un manque, échec immédiat — pas 10 minutes plus tard.

2. **Git sync** : `git checkout main`, `git pull`. On part toujours d'une base à jour.

3. **Bump version Maven** : `0.0.9-SNAPSHOT` → `0.0.10-SNAPSHOT`. Commit + push automatique du pom.xml + création d'un tag Git `v0.0.10`.

4. **Build natif via Paketo** : `./mvnw -Pnative spring-boot:build-image` avec le nom d'image cible Artifact Registry. La compilation natif prend 5 à 8 minutes ici (un peu plus que les 2 min en local à cause du Docker overhead).

5. **Push** vers Artifact Registry, avec tags `:0.0.10` et `:latest`.

6. **Deploy Cloud Run** : `gcloud run deploy` avec les mêmes paramètres que ci-dessus.

7. **Lecture des logs** : `gcloud run services logs read --limit 50 | grep "Started"`. Mesure du cold-start réel après déploiement. S'il est > 500 ms, alerte rouge.

Durée totale : 7 à 12 minutes. C'est ma limite acceptable pour un déploiement de prod. Si je devais déployer plus souvent que ça, j'irais sur du JVM standard avec un Cloud Run min-instances=1 — sujet de la section suivante.

## Le coût

Voilà ce que la facture de MOUSSAVOU est devenue après la bascule en natif.

Cloud Run free tier (au moment où j'écris) : 2 millions de requêtes par mois, 360 000 GB-secondes de mémoire, 180 000 vCPU-secondes. Pour une fintech qui démarre, 2M requêtes c'est confortable — disons 1500 utilisateurs actifs qui font 40 requêtes/jour chacun, soit 60 000 requêtes par jour, 1,8M par mois. Sous le seuil.

Avec `min-instances=0` et un cold-start de 205 ms, l'instance ne reste chaude que pendant les pics d'activité (par défaut 15 minutes après la dernière requête). La nuit, samedi-dimanche matin, jours fériés : zéro instance, zéro coût. Le service vit gratuitement.

Le binaire natif RAM ÷ 3 (250 → 80 Mo) m'a permis de baisser l'allocation mémoire de 512 MiB à 256 MiB par instance. Sur les calculs Cloud Run, ça veut dire que pour un même volume de requêtes, je facture moitié moins par instance-seconde.

Net résultat : la facture de MOUSSAVOU est revenue à **0 FCFA / mois** pour PayApp. Tant qu'elle reste sous les 2M requêtes mensuelles, elle peut grandir gratuitement. Le jour où elle dépasse, le coût marginal sera ~0,40 USD pour le million suivant. Loin de ce qu'elle paie pour un VPS qui tourne 24/7.

## Quand NE PAS faire du natif

Soyons honnêtes. Le natif n'est pas la solution à tout. Voilà quand je ne l'utiliserais pas.

**Tu changes ton code 30 fois par jour**. Si tu es en early-stage produit, en sprint design-prod-design, le build natif de 7-12 minutes en CI va te rendre fou. Reste sur JVM standard, déploie en 2 minutes, garde tes itérations courtes. Tu basculeras en natif quand l'API se stabilisera.

**Ton service tourne 24/7 sans jamais scale à zéro**. Si tu as un trafic continu — disons 10 requêtes/seconde non-stop — ton instance reste chaude en permanence. Le cold-start n'est jamais payé. Et après quelques minutes de warm-up JIT, la JVM optimise le code chaud mieux que ce qu'AOT a pu prédire à la compilation. Sur un workload soutenu, JVM peut être 10-20 % plus rapide en débit. Le natif gagne sur les workloads **serverless / intermittents** — pas sur les workloads stables.

**Tu utilises massivement de la réflexion dynamique ou des libs tierces non Spring**. Si ton app charge des classes à partir de strings (`Class.forName(config.className)`), si tu as des proxies dynamiques générés à la volée, si tu intègres une lib obscure qui n'a pas de hints AOT… tu peux y arriver, mais le coût d'ingénierie devient significatif. Mesure avant.

**Tu n'as pas Liberica NIK / un OS supporté facilement**. Sous Linux pur, c'est rapide à installer. Sous Windows, il faut MSVC Build Tools + NIK + un terminal qui charge l'environnement Visual Studio. C'est 30 minutes la première fois. Sous macOS Apple Silicon, il faut une distribution arm64. Vérifie ton environnement avant de t'engager.

## Ce que MOUSSAVOU emporte de cette histoire

Trois choses, en sortie de cette session de 48h passée à débugger Liberica NIK et docker-credential-gcr :

- **Le cold-start n'est pas une fatalité Java**. Bien configuré, un Spring Boot 4 natif démarre en 200 ms. Ce qui ferme la principale critique adressée à Spring sur serverless.
- **GraalVM AOT n'est pas magique, c'est juste de l'analyse statique à la compilation**. Spring Boot 4 fait 80 % du travail. Les 20 % restants, ce sont les hints custom — pénible, mais documenté.
- **L'authentification Cloud sous Windows, c'est trois mécanismes distincts** : `gcloud auth login`, `gcloud auth application-default login`, et `docker-credential-gcr`. Manquer un seul des trois et le pipeline échoue. Apprends à les vérifier en 30 secondes au début de chaque script, pas après 10 minutes de build.

MOUSSAVOU a poussé son MVP natif en prod. Cold-start mesuré : 187 ms. Facture du mois : 0 FCFA. Au dernier meetup GDG Libreville, elle a présenté son retour d'expérience. Trois autres devs de fintech locales au Gabon ont basculé leur stack la semaine suivante.

## Ressources

- **Repo MboloPay** : [github.com/bangaromaric/mbolopay](https://github.com/bangaromaric/mbolopay) — l'app de démo dont le bench est extrait, avec son `pom.xml`, ses tests d'architecture ArchUnit, sa doc native-image.
- **Script de déploiement Cloud Run** : [cloudRunDeploy.ps1](https://github.com/bangaromaric/mbolopay/blob/main/cloudRunDeploy.ps1) — le pipeline PowerShell détaillé dans la section *« Le pipeline automatisé »*. Forkable tel quel, à adapter avec tes propres variables d'environnement en haut du fichier.
- **Démo en ligne** : [mbolopay.banga.ga](https://mbolopay.banga.ga) — tourne sur Cloud Run en mode natif, `min-instances=0`. Cold-start le matin, 200 ms le reste du temps.
- **GraalVM Native Image** : [graalvm.org](https://www.graalvm.org/) — la doc officielle, dense mais complète.
- **Spring Boot AOT** : [docs.spring.io/spring-boot/reference/packaging/native-image/](https://docs.spring.io/spring-boot/reference/packaging/native-image/) — guide officiel Spring sur la compilation native.
- **Liberica NIK** : [bell-sw.com/pages/downloads/native-image-kit/](https://bell-sw.com/pages/downloads/native-image-kit/) — la distribution GraalVM que j'utilise sous Windows.
- **Architecture sous-jacente** : pour le DDD + Hexagonal + Spring Modulith qui structure MboloPay, voir [*« Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith »*]({{< ref "/posts/architecture-ia-spring-modulith" >}}) — l'article précédent où MOUSSAVOU apprend à modéliser son domaine.
- **Fiche projet MboloPay** : [/projects/mbolopay/]({{< ref "/projects/mbolopay" >}}) — résumé technique, stack complète, démo en ligne.

---

> *Le repo MboloPay est ouvert sur GitHub ([github.com/bangaromaric/mbolopay](https://github.com/bangaromaric/mbolopay)), la démo tourne sur [https://mbolopay.banga.ga](https://mbolopay.banga.ga), et si tu veux qu'on parle de ton archi Spring/GCP — mission consulting, coaching d'équipe, ou juste un café au prochain meetup GDG Libreville — écris-moi via [https://ban.ga/](https://ban.ga/). Mbolo.*

#Java #SpringBoot #SpringNative #GraalVM #GCP #CloudRun #AfricaTech #DDD
