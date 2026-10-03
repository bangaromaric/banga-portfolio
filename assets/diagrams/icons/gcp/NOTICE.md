# Icônes Google Cloud

Les trois fichiers SVG de ce dossier proviennent du pack officiel
**Google Cloud architecture icons**, téléchargé le 3 octobre 2026 depuis :

    https://cloud.google.com/icons
    https://cloud.google.com/static/icons/files/google-cloud-icons.zip

| Fichier | Icône du pack |
|---|---|
| `cloud_run.svg` | `cloud_run/cloud_run.svg` |
| `cloud_load_balancing.svg` | `cloud_load_balancing/cloud_load_balancing.svg` |
| `certificate_manager.svg` | `certificate_manager/certificate_manager.svg` |

Elles sont conservées telles que Google les distribue, sans retouche. Google met
ce pack à disposition pour représenter ses produits dans des diagrammes
d'architecture, ce qui est exactement l'usage qui en est fait ici.

## Comment les réutiliser

Ne pas les référencer par `<image href>` dans un SVG destiné à `make_cover.sh` :
Chrome headless rend le fichier hors du serveur Hugo et ne résoudrait pas le
chemin. Il faut **recopier les formes dans le SVG de la cover**.

Attention au passage : `cloud_run.svg` et `cloud_load_balancing.svg` portent
leurs couleurs dans un `<style>` interne, sous les mêmes noms de classe
`.cls-1`, `.cls-2`… avec des valeurs différentes. Inlinées côte à côte dans un
même document, elles se recolorient mutuellement. Convertir chaque classe en
attribut `fill` explicite avant de les coller.

Palette d'origine : `#4285f4`, `#669df6`, `#aecbfa`.
