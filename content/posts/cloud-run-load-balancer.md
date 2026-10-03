---
title: "Cloud Run derrière un load balancer global : certificat wildcard, pas à pas | Gabon"
heroTitle: "Cloud Run derrière un [load balancer global]"
date: 2026-10-03
description: "Migrer Cloud Run des domain mappings vers un global external Application Load Balancer : certificat wildcard, DNS authorization, TLS 1.2, serverless NEG et coûts."
tags: ["Cloud Run", "GCP", "Load Balancing", "Certificate Manager", "DNS", "DevOps"]
categories: ["Architecture"]
draft: false
showToc: true
cover:
    image: "/images/cloud-run-load-balancer-cover.png"
    alt: "Architecture Google Cloud de PayApp : du visiteur a Cloud Run en passant par la zone DNS LWS et le load balancer global payapp-prod-lb, sa certificate map wildcard et sa politique TLS 1.2, par Romaric BANGA"
    caption: "Zone DNS LWS, load balancer global, serverless NEG, puis Cloud Run"
---

Vendredi, 19 h 58, Libreville. Mon téléphone vibre. MOUSSAVOU, la développeuse qu'on avait suivie dans [« Spring Native + Cloud Run : cold-start ÷18 »]({{< ref "/posts/spring-native-cloud-run" >}}), m'envoie une capture d'écran sur WhatsApp. La console Google Cloud, onglet *Create global external Application Load Balancer*. Un champ rouge : « Certificate map is required ». Et un seul message : « Grand frère, c'est quoi ça encore ? »

Pour comprendre comment elle en est arrivée là, il faut remonter au mardi. PayApp, sa fintech fictive de Libreville, tourne en production sur Cloud Run depuis des mois. Son API répond sur `api.payapp.ga`, branchée directement sur le service Cloud Run grâce à un **domain mapping** : un CNAME vers `ghs.googlehosted.com.` chez son registrar LWS, un clic dans la console, et c'était en ligne. Simple. Gratuit.

Mardi, donc, un agrégateur de paiement de la place, avec qui PayApp veut s'interconnecter, lui envoie son questionnaire de sécurité. Ligne 14 : « Les protocoles TLS 1.0 et 1.1 doivent être désactivés sur tous les points d'entrée exposés. » MOUSSAVOU cherche le réglage dans Cloud Run. Elle ne le trouve pas. Et pour cause : la [documentation officielle](https://cloud.google.com/run/docs/mapping-custom-domains) est explicite, avec un domain mapping, **on ne peut pas désactiver TLS 1.0 et 1.1**.

En lisant la suite de la page, elle tombe sur pire. Les domain mappings sont en **Preview**. À cause de problèmes de latence, Google les considère comme pas prêts pour la production et ne les recommande pas pour des services en production. La méthode recommandée, en premier dans la liste : un **global external Application Load Balancer**. Elle s'est lancée seule, un vendredi soir. Et elle a buté sur le premier champ rouge.

Je connaissais ce champ. J'avais fait exactement la même migration peu de temps avant, pour mes propres services, en partant d'un niveau que je qualifierais honnêtement de *novice* sur les load balancers GCP. J'y avais laissé un certificat à cause d'une faute de frappe, coupé un site quelques minutes en touchant au DNS, et appris ce qu'est un *cache négatif*. Alors on a fait la soirée ensemble, en partage d'écran.

Cet article, c'est le carnet de bord de cette soirée : **pourquoi** mettre un load balancer devant Cloud Run, **lequel** choisir, et **comment** le faire pas à pas, entièrement depuis la console.

> 📝 **Ce que cet article ne couvre pas** : le déploiement d'un service Cloud Run. On part du principe que tes services tournent déjà. Si ce n'est pas le cas, commence par l'épisode précédent, [« Spring Native + Cloud Run : cold-start ÷18, RAM ÷3 »]({{< ref "/posts/spring-native-cloud-run" >}}), qui monte le service que nous allons exposer ici.

## Pourquoi les domain mappings ne suffisent plus

Les domain mappings, c'est pratique pour démarrer. Mais quand on lit la [liste officielle des limitations](https://cloud.google.com/run/docs/mapping-custom-domains), on comprend vite pourquoi Google pousse ailleurs.

- **Stade Preview, latence connue.** Pas de garantie de disponibilité, et Google ne les recommande pas en production.
- **Pas de certificat wildcard.** Un certificat par sous-domaine, provisionné à chaque nouveau mapping.
- **Impossible de désactiver TLS 1.0 et 1.1.** Un audit de sécurité te le reprochera.
- **Pas de certificat personnel** (self-managed). Tu prends le certificat Google, point.
- **Mapping uniquement sur `/`.** Impossible de router `/api` vers un service et `/` vers un autre.
- **Seulement 10 régions.** Ton service est dans une autre région ? Pas de domain mapping du tout.

Et il y a ce que la liste ne dit pas : avec les domain mappings, **chaque application est seule face à Internet**. Pas de pare-feu applicatif, pas de CDN, pas de point d'entrée commun où observer tout le trafic.

Prends le **marché Mont-Bouët** à Libreville. Imagine que chaque commerçant ait sa propre porte donnant directement sur la rue, avec son propre gardien, son propre cadenas, sa propre pancarte. Ça marche quand il y a trois boutiques. À trente, c'est ingérable : trente gardiens à payer, trente cadenas à changer, et aucun moyen de fermer le marché d'un coup si un voleur rôde.

Le load balancer, c'est **la grande entrée du marché**. Un seul portail, une seule adresse, un seul gardien qui vérifie tout le monde et qui sait exactement dans quelle allée se trouve chaque boutique. Les commerçants (tes services Cloud Run) ne s'occupent plus que de vendre.

> 💡 **En une phrase** : le load balancer t'apporte une **IP unique**, un **certificat wildcard** pour tous tes sous-domaines, le **routage** par nom de domaine ou par chemin, et la porte ouverte à **Cloud Armor** (sécurité) et **Cloud CDN** (cache). Tout ce que les domain mappings ne savent pas faire.

## Quelle option, et quel load balancer

Pour mettre un domaine personnalisé devant Cloud Run, Google propose [trois chemins](https://cloud.google.com/run/docs/mapping-custom-domains). Pour PayApp, on a pris le troisième.

- **Cloud Run domain mapping**, pour un prototype ou une démo. Gratuit, deux clics. Mais Preview, pas pour la production, et pas de wildcard.
- **Firebase Hosting**, pour un site vitrine avec un peu de dynamique. Peu cher, sert aussi le statique. Mais hors conditions Google Cloud, et moins de contrôle réseau.
- **Global external Application Load Balancer**, pour des apps en production. Wildcard, routage par domaine ou par chemin, Cloud Armor, CDN. Environ 18 $ par mois de coût fixe.

Ensuite, dans la console, l'assistant te pose une série de questions. Voici les réponses retenues pour PayApp, et pourquoi.

1. **Application Load Balancer (HTTP/HTTPS)** : on sert du web, pas du TCP brut.
2. **Public facing (external)** : les visiteurs viennent d'Internet.
3. **Best for global workloads** : les utilisateurs de PayApp sont au Gabon, mais aussi dans la diaspora en France et ailleurs. Le réseau Premium de Google les fait entrer au point de présence le plus proche.
4. **Global external Application Load Balancer**, et non *Classic*, l'ancienne génération que Google invite à migrer.

> ⚠️ **Et le load balancer régional ?** Le *regional external Application Load Balancer* utilise le réseau *Standard Tier*, avec un trafic sortant moins cher d'après la [page de tarification réseau](https://cloud.google.com/vpc/network-pricing). Mais il n'accepte pas les certificate maps de la même façon et ne donne pas l'entrée mondiale du réseau Premium. Pour quelques apps avec des visiteurs dispersés, le global reste le bon choix. Pour une app à fort trafic cantonné à une seule région, la question mérite d'être reposée.

{{< figure src="/images/cloud-run-load-balancer-01-choix-type-load-balancer.png" alt="Écran Create a load balancer de la console Google Cloud avec les quatre réponses de PayApp : Application Load Balancer en HTTP/HTTPS plutôt que Network Load Balancer, Public facing external, Global workloads, et génération Global external Application Load Balancer" caption="Les quatre questions de l'assistant et les réponses retenues : type, exposition, portée, génération." loading="lazy" >}}

## Le vocabulaire en deux minutes

Un load balancer GCP n'est pas *une* chose, c'est une chaîne de cinq petites briques que la console assemble pour toi, auxquelles on branche un certificate map et une politique SSL. Ajoute le DNS en amont, et une requête franchit six étapes avant d'atteindre Cloud Run. Les connaître évite de paniquer devant l'assistant.

```ascii {caption="Le chemin d'une requête vers api.payapp.ga. Le DNS envoie le visiteur sur l'IP du load balancer, le proxy présente le bon certificat, l'URL map choisit l'application, et le serverless NEG transmet à Cloud Run."}
Visiteur                 https://api.payapp.ga
   |
   v
Zone DNS chez LWS        api  ->  A  34.120.10.20
   |
   v
Forwarding rule          IP statique, port 443, port 80 redirigé
   |
   v
Target HTTPS proxy       termine le TLS
   |                     <-  certificate map + politique SSL
   v
URL map                  api.payapp.ga  ->  api-backend
   |
   v
Backend service          api-backend, logs activés
   |
   v
Serverless NEG           api-neg, europe-west1
   |
   v
Cloud Run, service api   ingress interne + load balancers
```

| Brique | Au marché Mont-Bouët | Dans la console |
|---|---|---|
| Forwarding rule | Le portail d'entrée et son adresse | *Frontend configuration* |
| Target HTTPS proxy, certificate map, politique SSL | Le gardien, son trousseau de badges et son règlement | *Certificate* |
| URL map | Le plan des allées | *Routing rules* |
| Backend service | Le responsable d'une allée | *Backend configuration* |
| Serverless NEG | La boutique elle-même, adresse comprise | *Serverless NEG* |

## Étape 1 : le certificat wildcard, en autorisation DNS

On commence par le certificat, **avant** le load balancer. C'est contre-intuitif, et c'est pourtant tout l'intérêt de la méthode.

### Pourquoi l'autorisation DNS, et pas l'autorisation load balancer

Pour obtenir un certificat géré par Google, il faut prouver que le domaine t'appartient. Certificate Manager propose [deux façons](https://cloud.google.com/certificate-manager/docs/certificates) :

- **Load Balancer Authorization** : Google vérifie en passant par ton load balancer. Problème, il faut que ton DNS pointe déjà sur le load balancer. Donc tu bascules le DNS **puis** tu attends le certificat. La doc prévient qu'une migration de ce type peut causer une coupure, typiquement de moins d'une heure. Et surtout, **pas de wildcard**.
- **DNS Authorization** : tu ajoutes un enregistrement CNAME dans ta zone DNS, Google le lit, et le certificat est émis **sans que ton trafic ait bougé**. Wildcard accepté.

Pour une fintech, la première option était exclue d'office : une heure sans API, ce sont des paiements qui échouent. C'est comme demander une carte de commerçant à la mairie. Avec la première méthode, l'agent vient constater que ta boutique est ouverte, il faut donc l'avoir déjà ouverte. Avec la seconde, tu montres ton titre de propriété au guichet, et ta carte est prête le jour où tu lèves le rideau.

### Dans la console

**Security → Certificate Manager → Certificates → Add Certificate**

| Champ | Pourquoi | Valeur pour PayApp |
|---|---|---|
| Name | Minuscules, tirets. **Immuable** après création | `payapp-ga-wildcard-cert` |
| Description | Pour toi dans six mois | Certificat wildcard payapp.ga |
| Location | Le load balancer est global | Global |
| Scope | La valeur prévue pour un global external ALB | Default |
| Certificate type | Google l'émet et le renouvelle seul | Google-managed |
| Certificate Authority type | Un certificat reconnu par tous les navigateurs | Public |
| Domain names | Le wildcard ne couvre pas le domaine nu, il faut les deux | `*.payapp.ga`, `payapp.ga` |
| Authorization type | Wildcard et zéro coupure | DNS Authorization |

Dès que tu choisis **DNS Authorization**, la console liste les domaines saisis avec leur autorisation DNS. Si aucune n'existe encore, clique sur **Create missing DNS authorization** et donne-lui un nom, par exemple `payapp-ga-dns-auth`. Le type par défaut est `FIXED_RECORD`, celui qu'on garde ici. La case **Per project authorization** ne sert que si plusieurs projets GCP doivent émettre des certificats pour le même domaine.

{{< figure src="/images/cloud-run-load-balancer-02-create-certificate.png" alt="Formulaire Create certificate de Certificate Manager rempli pour PayApp : nom payapp-ga-wildcard-cert, location Global, scope Default, Create Google-managed certificate, Certificate Authority type Public, domain names *.payapp.ga et payapp.ga, authorization type DNS Authorization" caption="Le formulaire rempli. Les deux noms de domaine sont saisis côte à côte : le wildcard ne couvre pas le domaine nu." loading="lazy" >}}

> ⚠️ **Le piège qui coûte un certificat** : à son premier essai, MOUSSAVOU a tapé `payapp.ba` au lieu de `payapp.ga`. Un *b* au lieu d'un *g*. Le `.ba`, c'est la Bosnie. Google lui a sagement demandé un CNAME `_acme-challenge.payapp.ba`, impossible à créer dans sa zone `payapp.ga`. Je ne me suis pas moqué, j'avais fait exactement la même faute lors de ma propre migration. Et comme l'encadré gris de la console le rappelle, les noms de domaine d'un certificat Google-managed sont **immuables** : supprimer le certificat, supprimer la DNS authorization associée, tout recommencer. **Relis les domaines deux fois avant de cliquer sur Create.**

### Le CNAME à ajouter chez LWS

Dès que l'autorisation DNS existe, le formulaire affiche un tableau : pour chaque domaine, l'enregistrement à créer. Note-le avant de cliquer sur Create. Au besoin, la commande `gcloud certificate-manager dns-authorizations describe payapp-ga-dns-auth` le réaffiche. Bonne nouvelle, `payapp.ga` et `*.payapp.ga` partagent **la même** DNS authorization, donc **un seul CNAME** suffit.

Pourquoi un seul ? Pour un certificat wildcard `*.payapp.ga`, la [doc Certificate Manager](https://cloud.google.com/certificate-manager/docs/deploy-google-managed-dns-auth) précise que l'autorisation DNS se configure sur le **domaine parent**, `payapp.ga`. Les deux noms reposent donc sur la même preuve.

{{< figure src="/images/cloud-run-load-balancer-03-dns-authorization.png" alt="Tableau DNS Authorization de la console : payapp.ga et *.payapp.ga renvoient tous deux à l'autorisation payapp-ga-dns-auth, avec le même DNS Record name _acme-challenge.payapp.ga et la même cible en authorize.certificatemanager.goog" caption="La preuve visuelle du paragraphe ci-dessus : deux domaines, une seule autorisation, un seul enregistrement à créer." loading="lazy" >}}

Chez LWS : **Gérer → Zone DNS → CNAME → Ajouter**

| Type | Nom | Cible |
|---|---|---|
| CNAME | `_acme-challenge` | `<identifiant>.authorize.certificatemanager.goog.` |

Deux détails qui font la différence :

- Dans **Nom**, seulement le préfixe `_acme-challenge`. LWS ajoute `.payapp.ga` tout seul.
- Dans **Cible**, garde le **point final**. Sans lui, certaines interfaces considèrent le nom comme relatif et fabriquent un `….goog.payapp.ga` qui ne mène nulle part.

> ⚠️ **Un seul enregistrement sur ce nom.** La doc insiste, le CNAME `_acme-challenge` doit être le **seul** enregistrement de ce nom. Certains hébergeurs laissent un TXT `_acme-challenge` d'un ancien certificat Let's Encrypt. Cette cohabitation peut bloquer l'émission ou le renouvellement. Supprime le TXT, ou recrée l'autorisation en mode *Per project authorization* : son CNAME porte alors un nom unique du type `_acme-challenge_xxxx`.

Pour vérifier, depuis n'importe quel terminal :

```bash
nslookup -type=CNAME _acme-challenge.payapp.ga 8.8.8.8
```

La réponse doit pointer vers `….authorize.certificatemanager.goog`. Ensuite, patience : le statut passe de **Provisioning** à **Active**. Ce soir-là, une dizaine de minutes.

{{< figure src="/images/cloud-run-load-balancer-04-certificat-active.png" alt="Liste Certificate Manager : le certificat payapp-ga-wildcard-cert en statut active avec une coche verte, région global, hostnames *.payapp.ga, type Google-managed, créé le 2 octobre 2026 et expirant le 31 décembre 2026" caption="Statut active. Le certificat est prêt alors que le trafic n'a pas encore bougé d'un octet." loading="lazy" >}}

> 📝 **Si tu utilises des enregistrements CAA** dans ta zone, autorise `pki.goog` et `letsencrypt.org`, comme le recommande la [doc Cloud Run](https://cloud.google.com/run/docs/mapping-custom-domains). Sans CAA, rien à faire.

## Étape 2 : la certificate map, ce fameux champ rouge

Retour au champ rouge de MOUSSAVOU, « Certificate map is required ». Elle venait de créer un beau certificat, et la console refusait de le lui laisser choisir directement. Pourquoi ?

Parce que le **global** external Application Load Balancer ne référence pas un certificat Certificate Manager tout seul : son proxy HTTPS pointe vers **une certificate map**. La référence de l'API est claire, référencer directement des certificats Certificate Manager n'est pas supporté pour ce type de load balancer, il faut passer par `certificateMap`. Le référencement direct est réservé aux load balancers régionaux et aux load balancers internes cross-region.

Une certificate map, c'est le **trousseau de clés du gardien**. Pour chaque nom de domaine qui se présente (`api.payapp.ga`, `payapp.ga`), elle dit quel certificat montrer. On y met deux entrées, une par nom du certificat.

**Certificate Manager → onglet Certificate maps → Create certificate map**

| Champ | Valeur pour PayApp |
|---|---|
| Name | `payapp-prod-cert-map` |
| Description | Certificate map de payapp-prod-lb |
| Entry 1, Hostname | `*.payapp.ga` |
| Entry 2, Hostname | `payapp.ga` |

Les deux entrées pointent vers le même certificat, `payapp-ga-wildcard-cert`.

{{< figure src="/images/cloud-run-load-balancer-05-certificate-map.png" alt="Écran de la certificate map payapp-prod-cert-map dans Certificate Manager : deux entrées, *.payapp.ga et payapp.ga, toutes deux associées au certificat payapp-ga-wildcard-cert avec une coche verte" caption="Le trousseau du gardien : deux noms d'hôte, un seul certificat derrière." loading="lazy" >}}

> 💡 **Astuce** : crée la map dans un **deuxième onglet** du navigateur. L'assistant du load balancer ne perd pas ta saisie, un clic sur *Refresh* dans la liste déroulante et la map apparaît.

## Étape 3 : le frontend, l'adresse du portail

**Network Services → Load balancing → Create load balancer**, puis les quatre choix vus plus haut. On nomme le load balancer `payapp-prod-lb`. Première section, **Frontend configuration**, c'est-à-dire *par où entrent les visiteurs*.

| Champ | Pourquoi | Valeur pour PayApp |
|---|---|---|
| Name | Lisible dans six mois | `payapp-prod-https-frontend` |
| Protocol | Le standard aujourd'hui | HTTPS (HTTP/2 et HTTP/3) |
| Network Service Tier | Imposé pour un load balancer global | Premium |
| IP version | | IPv4 |
| **IP address** | Surtout pas *Ephemeral*, voir plus bas | Create IP address |
| Port | | 443 |
| Certificate repository | La map de l'étape 2 | Use Certificate Map |
| **SSL policy** | La ligne 14 du questionnaire | Create a policy |
| HTTP/3 (QUIC) | | Automatic |
| Early data (0-RTT) | Évite les rejeux de requêtes, indispensable pour des paiements | Disabled |
| **Enable HTTP to HTTPS redirect** | Tout visiteur en `http://` est renvoyé vers `https://` | Coché |
| Client Authentication (Advanced) | C'est du mTLS, inutile ici | Ne pas activer |

L'IP réservée s'appelle `payapp-prod-lb-ip`, la certificate map est celle de l'étape 2, `payapp-prod-cert-map`, et la politique SSL que l'on crée dans la foulée, `payapp-tls12`.

{{< figure src="/images/cloud-run-load-balancer-06-frontend-config.png" alt="Section Frontend configuration du load balancer payapp-prod-lb : nom payapp-prod-https-frontend, protocole HTTPS incluant HTTP/2 et HTTP/3, Network Service Tier Premium, adresse IP réservée payapp-prod-lb-ip en 34.120.10.20, port 443, certificate map payapp-prod-cert-map, SSL policy payapp-tls12 et Early data sur Disabled" caption="Le frontend au complet. L'adresse est réservée et nommée, pas éphémère : c'est elle qui ira dans le DNS." loading="lazy" >}}

**La ligne qui a sauvé le partenariat.** Sans politique attachée, la [doc des SSL policies](https://cloud.google.com/load-balancing/docs/ssl-policies-concepts) précise que le load balancer se comporte comme avec le profil `COMPATIBLE` et **TLS 1.0 minimum**. Exactement ce que l'agrégateur refusait. MOUSSAVOU a donc choisi **Create a policy**.

| Champ de la politique | Pourquoi | Valeur |
|---|---|---|
| Name | | `payapp-tls12` |
| Profile | Large compatibilité avec les clients récents | **Modern** |
| Minimum TLS version | La ligne 14 du questionnaire | **TLS 1.2** |
| Post-quantum key exchange | Recommandé par Google, voir ci-dessous | **Enabled** |

{{< figure src="/images/cloud-run-load-balancer-06b-ssl-policy.png" alt="Panneau Create policy d'une politique SSL Google Cloud : nom payapp-tls12, Minimum TLS version sur TLS 1.2, Profile sur Modern, et Post-quantum key exchange sur Enabled" caption="La ligne 14 du questionnaire de sécurité, en trois champs." loading="lazy" >}}

Trois précisions tirées de la doc :

- Si un audit exige encore plus strict, le profil **Restricted** retire les suites de chiffrement les plus anciennes. Et pour imposer **TLS 1.3 minimum**, Restricted est obligatoire.
- L'échange de clés **post-quantique** (`X25519MLKEM768`) protège contre les futures menaces de l'informatique quantique. Il ne concerne que les clients TLS 1.3 qui le supportent, les autres ne voient aucune différence. Google prévoit de l'activer par défaut après octobre 2026, autant le choisir explicitement.
- Modifier une politique SSL **ne coupe pas** les connexions déjà ouvertes. On peut donc la durcir plus tard sans interruption.

Une fois en ligne, on le prouve à l'agrégateur. Sous Windows, `openssl` n'est pas installé par défaut, on le trouve dans Git Bash ou dans WSL.

```bash
# OpenSSL 3 refuse déjà TLS 1.1 de son côté : on baisse son propre niveau
# de sécurité pour que le refus vienne bien du serveur.
openssl s_client -connect api.payapp.ga:443 -servername api.payapp.ga -tls1_1 -cipher "DEFAULT@SECLEVEL=0"   # doit échouer
openssl s_client -connect api.payapp.ga:443 -servername api.payapp.ga -tls1_2                                # doit réussir
```

Pour joindre un rapport lisible au questionnaire, le test en ligne [SSL Labs](https://www.ssllabs.com/ssltest/) liste les versions de TLS acceptées et donne une note globale.

> ⚠️ **L'IP éphémère, le piège silencieux** : par défaut, la console propose *Ephemeral (Automatic)*. Une IP éphémère peut changer. Or c'est **cette IP** que tu vas écrire dans ton DNS chez LWS. Si elle change, l'API tombe sans que rien ne bouge côté GCP. En plus, la doc officielle précise que la redirection HTTP vers HTTPS **exige** une IP réservée. Bonne nouvelle, une IP statique rattachée à une forwarding rule est gratuite.

En cochant la redirection, la console crée en coulisse un **deuxième petit load balancer** HTTP sur la même IP, port 80, dont le seul travail est de répondre « va voir en HTTPS ». Il apparaît dans la liste sous le nom `payapp-prod-https-frontend-redirect`. Ne le supprime pas.

## Étape 4 : le backend, relier le portail à Cloud Run

C'est l'écran qui a le plus fait peur à MOUSSAVOU. Quand on clique sur **Create a backend service**, on tombe sur un formulaire chargé : *Instance group*, *Named port*, *Health check*, *Balancing mode*, *Maximum backend utilization*. De quoi faire fuir n'importe qui.

Le secret : **la plupart de ces champs ne te concernent pas**. Ils servent aux machines virtuelles. Il suffit de changer **un seul** réglage pour que le formulaire se simplifie d'un coup.

{{< figure src="/images/cloud-run-load-balancer-07-backend-service-avant.png" alt="Formulaire Create backend service par défaut, Backend type sur Instance group : champs Protocol, Named port, Timeout, IP address selection policy et un Health check obligatoire, tous sans objet pour Cloud Run" caption="Avant de toucher au Backend type : un formulaire taillé pour des machines virtuelles, health check obligatoire compris." loading="lazy" >}}

### Le réglage qui change tout : Backend type

Passe **Backend type** de *Instance group* à **Serverless network endpoint group**. Un *serverless NEG*, c'est un petit pointeur qui dit au load balancer : « derrière moi, il y a tel service Cloud Run, dans telle région ». Les health checks disparaissent, d'ailleurs ils ne sont pas supportés pour ce type de backend, Cloud Run gère lui-même la santé de ses instances.

### Les champs, un par un

| Champ | Pourquoi | Valeur pour PayApp |
|---|---|---|
| Name | Un backend service par application | `api-backend` |
| Description | | Backend Cloud Run de l'API |
| Backend type | Cloud Run est serverless | Serverless NEG |
| Protocol | La doc précise que ce paramètre est ignoré | Par défaut |
| Backends, New backend | Ouvre un petit panneau | Create Serverless NEG |
| NEG Name | | `api-neg` |
| Region | **La même** que le service Cloud Run | `europe-west1` |
| Type | Le service lui-même | Cloud Run, **api** |
| Cloud CDN | Voir ci-dessous | Décoché |
| Logging | Chaque requête visible dans Cloud Logging | Activé, sample rate 1 |
| Identity-Aware Proxy | Réservé aux apps privées derrière un compte Google | Décoché |
| Cloud Armor backend security policy | Voir ci-dessous | **None** |
| Advanced configurations | | Ne pas toucher |

Le logging est normalement coché par défaut avec un serverless NEG, mais vérifie-le.

{{< figure src="/images/cloud-run-load-balancer-08-serverless-neg.png" alt="Formulaire du backend service api-backend une fois le Backend type passé en Serverless network endpoint group : le NEG api-neg en europe-west1, Cloud CDN décoché, logging activé au sample rate 1, puis Identity-Aware Proxy décoché et aucune politique Cloud Armor sélectionnée" caption="Le même formulaire que ci-dessus, une fois le Backend type changé : plus de health check, plus de named port. Les deux colonnes se lisent de gauche à droite." loading="lazy" >}}

**Pourquoi décocher Cloud CDN.** La case est cochée par défaut, en mode *Cache static content*. Dans ce mode, le CDN met en cache les fichiers statiques (images, CSS, JavaScript) et toute réponse que l'application déclare cachable. Sur une API de paiement, presque rien n'est cachable : tu paierais chaque consultation du cache pour rien. Et il suffirait d'un en-tête `Cache-Control: public` posé par erreur sur une route de compte pour qu'une réponse personnelle, un solde par exemple, soit servie à quelqu'un d'autre. Le CDN servira plus tard pour l'app web, en mode *Use origin settings based on Cache-Control headers* : c'est alors **l'application** qui décide explicitement quoi mettre en cache.

**Pourquoi Cloud Armor sur None, pour l'instant.** La console propose une *Default security policy* qui limite chaque IP à 500 requêtes par minute. Bonne idée sur le papier. Mais une politique Cloud Armor Standard coûte [5 $ par mois, plus 1 $ par règle](https://cloud.google.com/armor/pricing), et l'assistant en créerait **une par backend**. Mieux vaut, dans un second temps, créer **une seule** politique partagée entre toutes les apps de PayApp.

Une fois le backend créé, la console le montre dans la liste avec *1 network endpoint group* et sa région.

{{< figure src="/images/cloud-run-load-balancer-09-backend-cree.png" alt="Étape Backend configuration de l'assistant Create global external Application Load Balancer : le load balancer payapp-prod-lb, le backend service api-backend en région europe-west1 avec 1 network endpoint group" caption="Le backend est créé : un network endpoint group, et zéro instance group." loading="lazy" >}}

> 💡 **Pas besoin de tout migrer d'un coup.** On a commencé par l'API seule. Le back-office `admin.payapp.ga` viendra plus tard, il suffira de **modifier** le load balancer pour ajouter son backend. Le certificat wildcard le couvre déjà.

## Étape 5 : les règles de routage, le plan du marché

Les *routing rules*, c'est le plan que le gardien consulte : « quelqu'un demande `api.payapp.ga` ? Allée de gauche, boutique api. » Techniquement, c'est l'**URL map** du load balancer.

Mode **Simple host and path rule** :

| Hosts | Paths | Backend |
|---|---|---|
| *Default, toute requête non reconnue* | | `api-backend` |
| `api.payapp.ga` | `/*` | `api-backend` |

La ligne **Default** est obligatoire, c'est là qu'atterrit tout ce qui ne correspond à aucune règle. Pour l'instant, l'API est le seul backend, donc elle pointe aussi vers lui. Le jour où le back-office arrive, il suffit d'ajouter une ligne `admin.payapp.ga` avec le chemin `/*` vers `admin-backend`.

{{< figure src="/images/cloud-run-load-balancer-10-routing-rules.png" alt="Écran Routing rules du load balancer en mode Simple host and path rule : la ligne All unmatched (Default) pointe vers api-backend, et la règle api.payapp.ga avec le chemin /* pointe elle aussi vers api-backend" caption="Le plan du marché : une règle par défaut, une règle nommée, et pour l'instant le même backend au bout des deux." loading="lazy" >}}

Dernier écran, **Review and finalize**, une relecture rapide, puis **Create**. Deux à cinq minutes plus tard, deux lignes apparaissaient dans la liste des load balancers : `payapp-prod-lb` en HTTPS, et `payapp-prod-https-frontend-redirect` en HTTP.

{{< figure src="/images/cloud-run-load-balancer-11-liste-load-balancers.png" alt="Liste Load balancing de la console avec deux entrées de type Application et External : payapp-prod-https-frontend-redirect en HTTP, et payapp-prod-lb en HTTPS avec 1 backend service, 0 instance group et 1 network endpoint group" caption="Deux lignes pour un seul portail : la redirection HTTP vit sa propre vie, sur la même IP." loading="lazy" >}}

## Étape 6 : tester avant de toucher au DNS

À ce stade, **rien n'a changé pour les utilisateurs de PayApp**. Le DNS de `api.payapp.ga` pointe toujours vers le domain mapping. Le load balancer existe à côté, avec son IP, en attendant son heure. C'est le moment idéal pour le tester sans risque.

L'astuce, recommandée par la [doc Google](https://cloud.google.com/load-balancing/docs/https/setting-up-https-serverless), est l'option `--resolve` de `curl`. Elle dit à `curl` : « pour ce nom de domaine, ne demande pas au DNS, va directement à cette IP ». Les utilisateurs ne voient rien. Seul ton terminal emprunte le nouveau chemin. Dans les exemples, l'IP du load balancer est `34.120.10.20`, remplace-la par la tienne.

```cmd
curl -I --resolve api.payapp.ga:443:34.120.10.20 https://api.payapp.ga
```

### Le premier essai, la douche froide

```text
curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed
```

Réflexe de MOUSSAVOU : « il faut sûrement supprimer le domain mapping de Cloud Run d'abord ». **Non.** Le domain mapping ne concerne que le trafic qui passe par `ghs.googlehosted.com`. Le test frappait directement l'IP du load balancer, un circuit totalement séparé. Supprimer le mapping à ce moment-là aurait coupé l'API en production, sans réparer le test.

L'erreur voulait dire : *le load balancer répond, mais il n'a pas encore de certificat* à présenter. Il venait d'être créé, et la certificate map met du temps à se déployer sur les serveurs de Google à travers le monde.

Pour en avoir le cœur net, un test **sans** TLS :

```cmd
curl -I http://34.120.10.20
```

```text
HTTP/1.1 301 Moved Permanently
Location: https://34.120.10.20:443/
```

Le load balancer est bien vivant, et la redirection HTTP vers HTTPS fonctionne. Il ne manquait que le certificat. Quelques minutes plus tard, même commande :

```text
HTTP/1.1 200 OK
strict-transport-security: max-age=31536000; includeSubDomains
server: Google Frontend
via: 1.1 google
```

Le `via: 1.1 google` est la signature du load balancer : la requête est passée par lui avant d'atteindre Cloud Run.

> 💡 **Pas de panique si tu n'obtiens pas 200.** `curl -I` envoie une requête `HEAD` sur `/`. Une API qui n'expose rien à la racine peut répondre `404` ou `405`. Ce n'est pas un problème, n'importe quel code HTTP accompagné de `via: 1.1 google` prouve que le chemin visiteur, load balancer, Cloud Run fonctionne. Pour un test plus parlant, vise une vraie route, par exemple `https://api.payapp.ga/actuator/health` si l'Actuator de Spring Boot est exposé.

> ⚠️ **À retenir** : après la création, compte **10 à 30 minutes** avant que le HTTPS réponde. Une erreur de handshake TLS pendant ce délai est normale. Vérifie que la certificate map est bien attachée (colonne *Certificate* du frontend), puis attends.

> 💡 **Sous Windows**, `curl` est fourni avec le système depuis plusieurs années. Lance-le de préférence depuis l'invite de commandes (`cmd`), ou appelle-le explicitement `curl.exe` dans PowerShell.

## Étape 7 : la bascule DNS chez LWS, et la coupure qu'on aurait pu éviter

Le test passe. Il ne reste plus qu'à dire au monde : « l'API, c'est maintenant à cette IP ». Dans la zone DNS LWS de PayApp, l'API ressemblait à ça :

| Type | Nom | Cible | TTL |
|---|---|---|---|
| CNAME | `api` | `ghs.googlehosted.com.` | 6 heures |

> 💡 **Le geste qu'on a oublié : baisser le TTL la veille.** Le TTL dit aux résolveurs combien de temps garder une réponse en mémoire. Avec 6 heures, certains clients continuent à suivre l'ancien chemin jusqu'à 6 heures après la bascule, et il faut attendre aussi longtemps avant de nettoyer. La bonne pratique : passer le TTL du CNAME à la plus petite valeur proposée par LWS **au moins un ancien TTL avant la bascule**, soit ici 6 heures avant. Le jour J, l'ancien chemin disparaît des caches en quelques minutes, et un retour arrière est tout aussi rapide si quelque chose cloche.

Il faut le remplacer par :

| Type | Nom | Valeur | TTL |
|---|---|---|---|
| A | `api` | `34.120.10.20` | 1 heure ou moins |

Un CNAME et un enregistrement A **ne peuvent pas coexister** sur le même nom. MOUSSAVOU a donc supprimé le CNAME, et ajouté le A quelques minutes plus tard. Quelques minutes de trop. J'avais fait exactement la même erreur lors de ma propre migration, et sur le partage d'écran, je l'ai vu une seconde trop tard. Résultat :

```text
nslookup api.payapp.ga 8.8.8.8
*** dns.google ne parvient pas à trouver api.payapp.ga : Non-existent domain
```

**Non-existent domain.** Pendant ces quelques minutes, l'API n'existait plus du tout pour le reste d'Internet. Chez LWS, après l'ajout du A, c'était bon tout de suite :

```text
nslookup api.payapp.ga ns21.lwsdns.com
Nom :    api.payapp.ga
Address:  34.120.10.20
```

Mais sur son PC :

```text
curl -I https://api.payapp.ga
curl: (6) Could not resolve host: api.payapp.ga
```

### Le cache négatif, expliqué simplement

Les résolveurs DNS (celui de ton opérateur, celui de Google, celui de ton PC) gardent en mémoire les réponses, pour ne pas reposer la même question sans arrêt. Ce qu'on oublie souvent : ils mémorisent aussi les réponses **négatives**. Le résolveur de MOUSSAVOU avait demandé « api.payapp.ga ? » pendant le trou, entendu « n'existe pas », et il lui répétait fidèlement cette réponse périmée.

C'est comme un taxi de Libreville à qui on a dit « la boutique a fermé » un matin où elle était en travaux. Pendant un moment, il ne t'y amènera plus, même si elle a rouvert entre-temps.

La durée maximale de ce cache négatif est fixée dans l'enregistrement **SOA** de la zone :

```bash
nslookup -type=SOA payapp.ga ns21.lwsdns.com
```

### Ce qui a débloqué la situation

1. **Vérifier la source** : `nslookup api.payapp.ga ns21.lwsdns.com` interroge directement LWS. Si LWS répond la bonne IP, la configuration est correcte, il ne reste que des caches.
2. **Vider le cache Google** : sur [la page Flush Cache de Google Public DNS](https://dns.google/cache), saisir `api.payapp.ga`, type `A`, puis *Flush Cache*.
3. **Vider le cache Windows** : `ipconfig /flushdns`.
4. **Tester en contournant l'opérateur** : `curl -I --doh-url https://dns.google/dns-query https://api.payapp.ga` résout le nom via le DNS de Google en HTTPS.
5. **Attendre** : un quart d'heure après, `curl -I https://api.payapp.ga` répondait `200 OK`, sans aucune option.

> ⚠️ **La leçon** : un CNAME et un A ne cohabitent pas sur le même nom, donc la bascule laisse forcément une fenêtre. Fais-la **la plus courte possible**, utilise le bouton **Modifier** (le crayon) si ton registrar le permet, sinon enchaîne suppression et ajout **dans la même minute**, sans rien faire entre les deux. Et choisis un moment calme : pour une fintech, un vendredi soir vaut mieux qu'un lundi matin.

> 💡 **Ce qui n'a pas posé problème** : l'ancien CNAME avait un TTL de 6 heures. Les clients qui l'avaient en cache ont continué à passer par le domain mapping pendant ce temps. Comme **les deux chemins fonctionnaient en parallèle**, ils n'ont rien vu. C'est pour ça qu'on ne supprime pas le domain mapping tout de suite.

## Étape 8 : fermer la porte de derrière

Le load balancer est en place, mais l'API a encore **deux autres portes** ouvertes : le domain mapping, et l'URL par défaut `https://api-xxxx.europe-west1.run.app`. Tant qu'elles existent, quelqu'un peut contourner le load balancer, et avec lui la politique TLS 1.2 et les futures règles Cloud Armor. L'agrégateur n'aurait pas apprécié. La [doc Google](https://cloud.google.com/run/docs/securing/ingress) le dit explicitement : sans le bon réglage d'ingress, les utilisateurs peuvent passer par l'URL par défaut et **contourner le load balancer**.

L'ordre compte :

1. **Attendre l'expiration de l'ancien TTL**, 6 heures ici, donc on l'a fait le lendemain.
2. **Cloud Run → Domain mappings**, supprimer le mapping `api.payapp.ga`.
3. **Service api → Networking → Ingress → Internal + Allow traffic from external Application Load Balancers**.
4. Vérifier : `https://api.payapp.ga` répond toujours, l'URL `…run.app` renvoie une erreur.

{{< figure src="/images/cloud-run-load-balancer-12-cloud-run-ingress.png" alt="Onglet Networking du service Cloud Run api en europe-west1 : l'ingress est sur Internal, la case Allow traffic from external Application Load Balancers est cochée, et l'option All qui autorise l'accès direct depuis Internet est décochée" caption="La porte de derrière fermée : plus rien n'entre par l'URL run.app sans passer par le load balancer." loading="lazy" >}}

> ⚠️ **Ne fais pas l'étape 3 avant l'étape 2.** D'après la doc de l'ingress, avec ce réglage, les requêtes venant d'Internet ne passent plus ni par l'URL `run.app`, ni par un domaine mappé. Si tu le changes alors que des clients suivent encore l'ancien CNAME, ils tombent sur une erreur.

> 📝 **Pour aller plus loin : désactiver l'URL `run.app`.** L'ingress bloque déjà Internet sur cette URL. Si tu veux qu'elle n'existe plus du tout, l'onglet *Networking* du service propose, dans la carte *Endpoints*, de décocher **Enable** sous *Default HTTPS endpoint URL*. Attention, la doc de l'ingress prévient que Cloud Scheduler, Cloud Tasks, Pub/Sub, Eventarc, Workflows et les uptime checks appellent Cloud Run par cette URL. Si PayApp les utilise, on la garde.

## Bonus : un seul NEG pour toutes les apps, avec les URL masks

En relisant la doc pour préparer cet article, je suis tombé sur une fonctionnalité qui évite de créer un backend par application : les **URL masks**.

Au lieu de pointer un serverless NEG vers *un* service Cloud Run précis, tu lui donnes un **modèle d'URL**. Le NEG extrait le nom du service depuis l'adresse demandée et envoie la requête au bon service. Pour PayApp :

| URL demandée | URL mask | Service Cloud Run appelé |
|---|---|---|
| `https://api.payapp.ga` | `<service>.payapp.ga` | `api` |
| `https://admin.payapp.ga` | `<service>.payapp.ga` | `admin` |

Un seul NEG, un seul backend service, une seule règle par défaut. Un nouveau service `marchands` déployé sur Cloud Run dans la même région ? Côté load balancer, rien à faire, il suffit d'ajouter l'enregistrement DNS `marchands`. Dans la console, au moment de créer le serverless NEG, choisis **Use URL Mask** au lieu de *Select service*.

Deux conditions : le **nom du service Cloud Run doit être identique** au sous-domaine, et tous les services doivent être **dans la région du NEG**. C'est la piste retenue pour le back-office, et elle se marie bien avec une application découpée en modules, comme les contextes bornés de [MboloPay]({{< ref "/projects/mbolopay" >}}), où chaque module peut un jour devenir son propre service.

On peut même éviter de toucher au DNS à chaque nouveau service : un enregistrement générique `*` de type A vers l'IP du load balancer, chez LWS, envoie tous les sous-domaines vers le load balancer. Les enregistrements explicites restent prioritaires sur le générique. Revers de la médaille, n'importe quel sous-domaine inventé atterrit lui aussi sur le load balancer, qui répond par une erreur.

## Combien ça coûte, vraiment

Réponse courte : **environ 18 à 20 $ par mois** pour cette configuration, soit à peu près une dizaine de milliers de FCFA. Presque tout est un **coût fixe**, qu'il y ait du trafic ou pas. Tous les tarifs ci-dessous viennent des pages officielles [Network pricing](https://cloud.google.com/vpc/network-pricing) et [Certificate Manager pricing](https://cloud.google.com/certificate-manager/pricing), consultées en octobre 2026.

| Élément | Tarif officiel | Coût mensuel |
|---|---|---|
| Forwarding rules (2 : HTTPS et redirection) | 0,025 $/h pour les 5 premières | environ 18,25 $ |
| Traitement par le load balancer | 0,008 $/Gio entrant et 0,008 $/Gio sortant | quelques centimes |
| Sortie Internet vers l'Afrique (Premium) | 1er Gio gratuit, puis 0,15 $/Gio | selon le trafic |
| IP statique rattachée au load balancer | Gratuite | 0 $ |
| Certificat wildcard (Certificate Manager) | Gratuit jusqu'à 100 certificats par projet, sans frais par connexion avec une clé RSA-2048 ou ECDSA | 0 $ |
| Politique SSL (TLS 1.2 minimum) | Aucune ligne de prix dédiée dans la grille tarifaire | 0 $ |
| Cloud CDN, Cloud Armor | Désactivés | 0 $ |

Exemple concret : l'API PayApp envoie 5 Gio par mois à des clients en Afrique. 18,25 $ de forwarding rules, environ 0,08 $ de traitement, (5 − 1) × 0,15 = 0,60 $ de sortie Internet. **Total : environ 19 $.**

Deux bonnes nouvelles cachées dans la doc :

- **La redirection HTTP ne coûte rien de plus** : les 5 premières forwarding rules d'un projet sont facturées ensemble, 0,025 $/h.
- **Pas de double facturation du trafic sortant** : avec un serverless NEG, les frais de sortie propres à Cloud Run ne s'appliquent plus aux requêtes qui passent par le load balancer. Seul le tarif de sortie Internet compte.

> ⚠️ **Le vrai prix du confort** : avec les domain mappings, le coût fixe était de **0 $**. Ces 18 $ par mois paient le wildcard, le TLS 1.2 exigé par le partenaire, le point d'entrée unique et la possibilité d'ajouter sécurité et cache. Et ils ne bougent pas quand on ajoute une app : le back-office, et tous les services suivants, passent par les mêmes forwarding rules. **Plus tu regroupes d'apps derrière ce load balancer, plus il devient rentable.**

## Et si le trafic explose

Côté technique, rien à faire, le load balancer global absorbe la charge tout seul. C'est la **facture** qui grossit, surtout via la sortie Internet. Ordre de grandeur, clients en Afrique, hors coût de Cloud Run lui-même :

| Trafic sortant par mois | Total approximatif |
|---|---|
| 5 Gio | 19 $ |
| 100 Gio | 35 $ |
| 1 Tio | 190 $ |

Les leviers, du plus simple au plus avancé :

1. **Alléger les réponses**, gratuit : `server.compression.enabled=true` dans Spring Boot, des images en WebP à la bonne taille.
2. **Activer Cloud CDN sur l'app web** quand le trafic dépasse une centaine de Gio par mois, en laissant l'application décider via `Cache-Control: public, max-age=31536000` sur les fichiers statiques versionnés, et `no-store` sur tout ce qui touche au compte et au solde.
3. **Une politique Cloud Armor partagée** dès que les logs montrent des robots : les requêtes bloquées ne passent pas par le load balancer, donc ne génèrent pas de frais de traitement.
4. **Baisser le sample rate des logs** de 1 à 0,1 au-delà de quelques millions de requêtes par mois.
5. **Un `max-instances` raisonnable** sur chaque service Cloud Run, pour qu'un pic ou une attaque ne fasse pas exploser la facture de calcul.

Et avant tout le reste : une **alerte budgétaire** dans *Billing → Budgets & alerts*. Elle ne coûte rien et évite la surprise du lundi matin. MOUSSAVOU, qui avait découvert sa première facture cloud dans l'article précédent, l'a configurée avant même de fermer la console.

## Quand NE PAS mettre un load balancer

Soyons honnêtes, ce n'est pas la bonne réponse partout.

**Tu as une seule app de démo, sans vrais utilisateurs.** 18 $ par mois pour un prototype que personne n'utilise, c'est cher. Le domain mapping fait l'affaire le temps de valider l'idée. Tu migreras le jour où ça devient sérieux.

**Ton site est surtout statique.** Une page vitrine avec un formulaire de contact ? Firebase Hosting devant Cloud Run, ou même un simple bucket, coûtera moins cher.

**Ton budget cloud se compte en bourses d'étudiant.** Le free tier de Cloud Run peut te faire tourner gratuitement des mois. Le load balancer, lui, n'a pas de free tier, il facture dès la première heure. Fais le calcul avant.

**Ton trafic est massif et concentré dans une seule région.** Regarde alors le load balancer **régional**, sur réseau Standard, dont la sortie Internet coûte moins cher.

## Ce que MOUSSAVOU emporte de cette soirée

- **Le certificat d'abord, le DNS ensuite.** L'autorisation DNS permet d'avoir un certificat wildcard actif **avant** de toucher au trafic. C'est elle qui rend la migration sans coupure possible.
- **Tester avec `curl --resolve` avant de basculer.** On valide le nouveau chemin pendant que l'ancien sert les clients. Une erreur de handshake TLS dans les premières minutes n'est pas un bug, c'est une propagation.
- **Un CNAME et un A ne cohabitent pas.** La bascule DNS crée forcément un trou, il doit durer quelques secondes, pas quelques minutes. Sinon, le cache négatif se charge de te le rappeler. Et un TTL baissé la veille accélère tout, y compris un retour arrière.
- **Ne jamais laisser la politique SSL par défaut.** Sans politique attachée, le load balancer accepte encore TLS 1.0. Une politique `MODERN` avec TLS 1.2 minimum ne coûte rien et répond à la plupart des questionnaires de sécurité.

Le lundi suivant, MOUSSAVOU a renvoyé le questionnaire à l'agrégateur. Ligne 14 : *conforme*, avec le rapport SSL Labs et la sortie d'`openssl` en pièce jointe. L'API de PayApp tourne désormais derrière `payapp-prod-lb`, avec le header `via: 1.1 google` comme preuve. Le back-office suivra, avec un URL mask. Et le jour où un robot viendra marteler l'API, il n'y aura qu'une politique Cloud Armor à brancher.

## Ressources

- [Map custom domains, Cloud Run](https://cloud.google.com/run/docs/mapping-custom-domains) : les trois options et les limitations des domain mappings, dont TLS 1.0 et 1.1.
- [Global external Application Load Balancer avec Cloud Run](https://cloud.google.com/load-balancing/docs/https/setting-up-https-serverless) : le guide officiel, URL masks, ingress, CDN, Cloud Armor.
- [Deploy a global Google-managed certificate with DNS authorization](https://cloud.google.com/certificate-manager/docs/deploy-google-managed-dns-auth) : le CNAME `_acme-challenge` et les certificate maps.
- [Certificate Manager, manage certificates](https://cloud.google.com/certificate-manager/docs/certificates) : DNS authorization contre load balancer authorization, et la question du wildcard.
- [SSL policies overview](https://cloud.google.com/load-balancing/docs/ssl-policies-concepts) : profils et version TLS minimale.
- [Restrict network ingress, Cloud Run](https://cloud.google.com/run/docs/securing/ingress) : les réglages d'ingress et la désactivation de l'URL `run.app`.
- [Network pricing](https://cloud.google.com/vpc/network-pricing) et [Certificate Manager pricing](https://cloud.google.com/certificate-manager/pricing) : les tarifs utilisés dans cet article.
- [Google Public DNS, Flush Cache](https://dns.google/cache) : pour forcer Google à oublier une vieille réponse DNS.
- [« Spring Native + Cloud Run : cold-start ÷18, RAM ÷3 »]({{< ref "/posts/spring-native-cloud-run" >}}) : l'épisode précédent de PayApp, pour la partie déploiement Cloud Run.

---

## Exposer vos services Cloud Run comme il faut

Mettre un load balancer devant Cloud Run, ça se décide une fois et ça se vit des années. C'est concrètement ce que je fais avec les équipes, ici au Gabon et ailleurs en zone francophone :

- 🎓 **Formation entreprise** : architecture GCP de production, certificats gérés, politiques TLS et observabilité d'un point d'entrée unique. [Voir les formats →](/about/#services)
- 🧭 **Consulting & audit** : répondre à un questionnaire de sécurité partenaire sans refaire toute votre infrastructure. [Discutons d'un projet](mailto:bangaromaric@gmail.com)
- 📖 **Aller plus loin** : [« Spring Native + Cloud Run : cold-start ÷18, RAM ÷3 »]({{< ref "/posts/spring-native-cloud-run" >}}) (l'épisode précédent, qui déploie le service exposé ici) et [« Dompter l'IA générative avec DDD, Hexagonal & Spring Modulith »]({{< ref "/posts/architecture-ia-spring-modulith" >}}) (le pendant architectural, côté code).
- 🗂️ **Cas concret** : [MboloPay]({{< ref "/projects/mbolopay" >}}), le mobile money pédagogique dont les contextes bornés se prêtent bien aux URL masks décrits plus haut.
- 🌍 **Communauté** : [GDG Libreville](/gdg/), où ce genre de soirée de dépannage finit souvent en atelier.

*Si tu dois toi aussi passer tes services Cloud Run derrière un load balancer, ou répondre au questionnaire de sécurité d'un partenaire, écris-moi via [ban.ga](https://ban.ga/). Mbolo.*

#GCP #CloudRun #LoadBalancing #CertificateManager #DNS #DevOps #AfricaTech
