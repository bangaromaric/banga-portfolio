#!/usr/bin/env python3
"""hugo_doctor : controle de sante du site Hugo ban.ga.

Verifie ce qu'un relecteur humain rate systematiquement : les parametres de
configuration qui atterrissent dans la mauvaise table TOML, les cles depreciees,
les APIs de template obsoletes, les derives de version entre le poste et la CI,
et les garde-fous historiques que personne ne doit retirer par inadvertance.

Zero dependance : uniquement la bibliotheque standard (tomllib, Python 3.11+),
pour pouvoir tourner en CI sans etape d'installation.

Usage :
    python scripts/hugo_doctor.py          # rapport complet
    python scripts/hugo_doctor.py --ci     # pour la CI : saute le build local
    python scripts/hugo_doctor.py --quiet  # n'affiche que erreurs et alertes

Code de sortie : 1 s'il reste au moins une ERREUR, 0 sinon.
Les ALERTES et les NOTES ne font jamais echouer.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    sys.exit("Python 3.11+ requis (module tomllib).")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ERR, WARN, NOTE, OK = "ERREUR", "ALERTE", "NOTE  ", "  ok  "
_counts = {ERR: 0, WARN: 0}
_quiet = False


def say(level: str, label: str, detail: str = "", *lines: str) -> None:
    if level in _counts:
        _counts[level] += 1
    if _quiet and level in (OK, NOTE):
        return
    print(f"  [{level}] {label}" + (f" : {detail}" if detail else ""))
    for extra in lines:
        print(f"           {extra}")


def section(title: str) -> None:
    if not _quiet:
        print(f"\n--- {title} " + "-" * max(0, 58 - len(title)))


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "hugo.toml").exists():
            return p
    return Path.cwd()


ROOT = repo_root()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def template_files() -> list[Path]:
    return sorted(ROOT.joinpath("layouts").rglob("*.html"))


def theme_files() -> list[Path]:
    theme = ROOT / "themes"
    return sorted(theme.rglob("*.html")) if theme.exists() else []


# ----------------------------------------------------------------------------
# 1. Placement des parametres dans les tables TOML
# ----------------------------------------------------------------------------

PARAM_REFS = [
    re.compile(r'\.Param\s+"([A-Za-z0-9_]+)"'),
    re.compile(r"\bsite\.Params\.([A-Za-z0-9_]+)"),
    re.compile(r"\b\.Site\.Params\.([A-Za-z0-9_]+)"),
]


def flatten(node: dict, prefix: str = "") -> dict[str, str]:
    """Chemin complet -> type, pour toutes les cles simples de la config."""
    out: dict[str, str] = {}
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            for item in value:
                if isinstance(item, dict):
                    out.update(flatten(item, path))
        else:
            out[path] = type(value).__name__
    return out


def find_misplaced_params(
    params: dict, referenced: dict[str, set[str]]
) -> list[tuple[str, str, set[str]]]:
    """Fonction pure, testee par --selftest.

    Renvoie (nom, chemin_reel, consommateurs) pour chaque parametre lu par un
    template mais declare sous une sous-table au lieu de la racine de params.

    C'est le bug silencieux numero un de ce projet : en TOML, un header de table
    capture toutes les cles qui le suivent. Une cle ecrite apres [params.schema]
    atterrit dans params.schema, Hugo ne dit rien, et le parametre est ignore.
    """
    root_keys = {k.lower() for k, v in params.items() if not isinstance(v, dict)}

    nested: dict[str, list[str]] = {}
    for path in flatten(params):
        if "." not in path:
            continue
        nested.setdefault(path.split(".")[-1].lower(), []).append(path)

    out = []
    for name, consumers in sorted(referenced.items()):
        if name in root_keys:
            continue
        paths = nested.get(name, [])
        if paths:
            out.append((name, paths[0], consumers))
    return out


def collect_param_refs() -> dict[str, set[str]]:
    referenced: dict[str, set[str]] = {}
    for f in template_files() + theme_files():
        text = read(f)
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        for rx in PARAM_REFS:
            for name in rx.findall(text):
                referenced.setdefault(name.lower(), set()).add(rel)
    return referenced


def check_param_placement(config: dict) -> None:
    section("Placement des parametres")

    params = config.get("params", {})
    referenced = collect_param_refs()
    misplaced = find_misplaced_params(params, referenced)

    for name, path, consumers in misplaced:
        projet = [c for c in consumers if not c.startswith("themes/")]
        say(
            ERR,
            f"parametre `{name}` hors de params",
            f"declare sous params.{path}",
            "un header de table TOML capture les cles qui le suivent : remonter",
            "cette cle au-dessus de la premiere sous-table [params.xxx].",
            "lu par : " + ", ".join(sorted(projet or consumers)[:3]),
        )

    if not misplaced:
        say(OK, "aucun parametre capture par une mauvaise table")

    root_keys = {k.lower() for k, v in params.items() if not isinstance(v, dict)}

    # Config morte : declaree a la racine mais lue nulle part.
    dead = sorted(
        k for k in root_keys
        if k not in referenced and k not in {"env", "keywords", "images", "mainsections"}
    )
    if dead:
        say(
            NOTE,
            f"{len(dead)} parametre(s) declare(s) mais lu(s) par aucun template",
            ", ".join(dead[:10]),
            "soit un template surcharge le consommateur, soit c'est de la config morte.",
        )


# ----------------------------------------------------------------------------
# 2. Cles depreciees dans le contenu
# ----------------------------------------------------------------------------

DEPRECATED_FRONTMATTER = {
    "_build": ("build", "deprecie depuis Hugo 0.145"),
    "_target": ("target", "deprecie depuis Hugo 0.145"),
}


def check_content_frontmatter() -> None:
    section("Frontmatter du contenu")
    found = 0
    for md in sorted(ROOT.joinpath("content").rglob("*.md")):
        for line_no, line in enumerate(read(md).splitlines()[:60], start=1):
            key = line.split(":")[0].strip()
            if key in DEPRECATED_FRONTMATTER:
                new, why = DEPRECATED_FRONTMATTER[key]
                found += 1
                say(
                    ERR,
                    f"cle `{key}` depreciee",
                    f"{md.relative_to(ROOT)}:{line_no}",
                    f"{why}, renommer en `{new}`.",
                )
    if not found:
        say(OK, "aucune cle de frontmatter depreciee")


# ----------------------------------------------------------------------------
# 3. APIs de template obsoletes ou risquees
# ----------------------------------------------------------------------------

TEMPLATE_SMELLS = [
    (r"\.Scratch\b", ERR, ".Scratch est remplace par .Store depuis Hugo 0.138"),
    (r"\.Hugo\b", ERR, ".Hugo a ete retire, utiliser hugo.Version"),
    (r"\.RSSLink\b", ERR, '.RSSLink a ete retire, utiliser .OutputFormats.Get "rss"'),
    (r"\.GetParam\b", ERR, ".GetParam est remplace par .Param"),
    (r"\.Site\.IsServer\b", ERR, ".Site.IsServer est remplace par hugo.IsServer"),
    (r"\.Site\.", WARN, "prefere la forme globale `site.` a `.Site.`"),
    # Volontairement absent : `.URL`. Il est deprecie sur une Page mais parfaitement
    # legitime sur une entree de menu, et les deux se ressemblent dans un template.
    # Un controle qui crie a chaque boucle de menu serait ignore en deux semaines.
]

# partialCached sans cle de variante : le resultat du PREMIER rendu est reutilise
# pour toutes les pages. C'est exactement le piege rencontre sur ce projet avec le
# footer de PaperMod, qui rendait un drapeau de page non deterministe.
RX_PARTIAL_CACHED = re.compile(r'partialCached\s+"[^"]+"\s+\.?[\w$]*\s*(-?\}\})')


def check_template_apis() -> None:
    section("APIs de template")
    hits = 0
    seen: set[tuple[str, int, str]] = set()

    for f in template_files():
        text = read(f)
        rel = str(f.relative_to(ROOT)).replace("\\", "/")

        for pattern, level, message in TEMPLATE_SMELLS:
            for m in re.finditer(pattern, text):
                line_no = text[: m.start()].count("\n") + 1
                key = (rel, line_no, message)
                if key in seen:
                    continue
                seen.add(key)
                hits += 1
                say(level, message, f"{rel}:{line_no}")

        for m in RX_PARTIAL_CACHED.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            hits += 1
            say(
                WARN,
                "partialCached sans cle de variante",
                f"{rel}:{line_no}",
                "le resultat du premier rendu sert a toutes les pages.",
                "ajouter une cle de variante, ou utiliser partial tout court.",
            )

    if not hits:
        say(OK, "aucune API de template obsolete")


def check_render_hooks() -> None:
    section("Render hooks")
    generic = list(ROOT.rglob("layouts/**/render-codeblock.html"))
    if generic:
        say(
            ERR,
            "render-codeblock.html generique present",
            str(generic[0].relative_to(ROOT)),
            "il intercepte TOUTES les fences et tue la coloration syntaxique.",
            "nommer le hook par son langage : render-codeblock-<langage>.html",
        )
    else:
        say(OK, "pas de hook de codeblock generique")

    hooks = sorted(ROOT.glob("layouts/_default/_markup/render-codeblock-*.html"))
    if hooks:
        noms = ", ".join(h.stem.replace("render-codeblock-", "") for h in hooks)
        say(NOTE, f"{len(hooks)} hook(s) de fence", noms)


# ----------------------------------------------------------------------------
# 4. Derive de version entre le poste et la CI
# ----------------------------------------------------------------------------


def local_hugo_version() -> str | None:
    try:
        out = subprocess.run(
            ["hugo", "version"], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"v(\d+\.\d+\.\d+)", out)
    return m.group(1) if m else None


def check_version_drift() -> None:
    section("Versions")
    wf = ROOT / ".github" / "workflows" / "hugo.yml"
    if not wf.exists():
        say(NOTE, "pas de workflow GitHub Actions")
        return
    m = re.search(r"hugo-version:\s*'([\d.]+)'", read(wf))
    if not m:
        say(WARN, "version Hugo non epinglee dans le workflow")
        return
    ci = m.group(1)
    local = local_hugo_version()
    if local is None:
        say(NOTE, f"CI epinglee sur Hugo {ci}", "binaire hugo introuvable en local")
    elif local != ci:
        say(
            WARN,
            "derive de version Hugo",
            f"local {local}, CI {ci}",
            "un build local ne prouve alors rien sur le build de production.",
        )
    else:
        say(OK, f"Hugo {local} en local et en CI")


# ----------------------------------------------------------------------------
# 5. Garde-fous de configuration, chacun lie a un incident connu
# ----------------------------------------------------------------------------


def dig(node: dict, path: str):
    cur = node
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def check_config_guards(config: dict) -> None:
    section("Garde-fous de configuration")

    if dig(config, "minify.tdewolff.html.keepQuotes") is True:
        say(OK, "keepQuotes actif")
    else:
        say(
            ERR,
            "keepQuotes absent de [minify.tdewolff.html]",
            "",
            "sans lui, --minify retire les guillemets HTML5-legaux et casse",
            "la verification Bing Webmaster Tools (CLAUDE.md §10.1).",
        )

    if dig(config, "markup.goldmark.renderer.unsafe") is True:
        say(OK, "goldmark unsafe actif")
    else:
        say(
            ERR,
            "markup.goldmark.renderer.unsafe desactive",
            "",
            "le HTML brut de content/about.md et les diagrammes SVG inline",
            "cesseraient d'etre rendus.",
        )

    noclasses = dig(config, "markup.highlight.noClasses")
    if noclasses is None or noclasses is True:
        say(
            WARN,
            "markup.highlight.noClasses actif ou absent",
            "",
            "Chroma ecrit alors un style INLINE sur chaque <pre>, que les tokens",
            "CSS ne peuvent pas battre. Mettre noClasses = false et habiller les",
            "classes dans assets/css/extended/15-chroma.css.",
        )
    else:
        say(OK, "coloration syntaxique en classes")

    block_attr = dig(config, "markup.goldmark.parser.attribute.block")
    if block_attr is True:
        say(
            WARN,
            "parser.attribute.block active",
            "",
            "les attributs {caption=...} des fences n'en ont pas besoin, et",
            "l'activer change le parsing des articles existants.",
        )


# ----------------------------------------------------------------------------
# 6. Discipline du theme et du systeme de design
# ----------------------------------------------------------------------------


def check_theme_untouched() -> None:
    section("Theme et design system")
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "themes/"],
            cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ""
    if out:
        say(
            ERR,
            "le submodule du theme est modifie",
            out.splitlines()[0][:70],
            "ne jamais editer themes/ : surcharger dans layouts/ ou assets/.",
        )
    else:
        say(OK, "submodule du theme intact")

    inline = []
    for f in template_files():
        text = read(f)
        for m in re.finditer(r'style="', text):
            inline.append(f"{f.relative_to(ROOT)}:{text[: m.start()].count(chr(10)) + 1}")
    if inline:
        say(
            WARN,
            f"{len(inline)} attribut(s) style= en dur dans les templates",
            ", ".join(inline[:4]),
            "le site a un systeme de tokens : preferer une classe.",
        )
    else:
        say(OK, "aucun style inline dans les templates")


# ----------------------------------------------------------------------------
# 7. Coherence robots.txt, sitemap et taxonomies
# ----------------------------------------------------------------------------


RX_TAXO_LINK = re.compile(
    r'href="[^"]*/(tags|categories)/|GetTerms\s+"(tags|categories)"'
)


def check_indexing_coherence(config: dict) -> None:
    section("Indexation")

    disabled = {str(k).lower() for k in (config.get("disableKinds") or [])}
    taxo_off = {"taxonomy", "term"} <= disabled

    robots = ROOT / "static" / "robots.txt"
    text = read(robots) if robots.exists() else ""
    disallowed = re.findall(r"^Disallow:\s*(\S+)", text, flags=re.M)
    taxo_blocked = [d for d in disallowed if d.rstrip("/") in ("/tags", "/categories")]

    # Les templates qui pointent encore vers une page de taxonomie.
    linkers = []
    for f in template_files():
        hit = RX_TAXO_LINK.search(read(f))
        if hit:
            linkers.append(f"{str(f.relative_to(ROOT)).replace(chr(92), '/')} ({hit.group(0)[:28]})")

    if taxo_off:
        if linkers:
            say(
                ERR,
                "les pages de taxonomie sont desactivees mais encore liees",
                linkers[0],
                "disableKinds supprime les pages : ces liens pointent vers des 404.",
                "lire les tags depuis .Params.tags et ne pas en faire des liens.",
                *linkers[1:3],
            )
        else:
            say(OK, "taxonomies desactivees et plus aucun lien vers elles")
        if taxo_blocked:
            say(
                WARN,
                "robots.txt bloque encore des taxonomies qui n'existent plus",
                ", ".join(taxo_blocked),
                "regle morte, a retirer pour ne pas laisser croire a une protection.",
            )
        return

    if not taxo_blocked:
        say(OK, "robots.txt ne bloque pas les taxonomies")
    elif linkers:
        say(
            WARN,
            "taxonomies bloquees dans robots.txt mais liees depuis les templates",
            ", ".join(taxo_blocked),
            "un Disallow empeche Google de LIRE un eventuel noindex : une page",
            "bloquee mais liee peut finir indexee en URL seule. Deux sorties :",
            "retirer le Disallow et poser un noindex, ou cesser de generer et de",
            "lier ces pages (disableKinds = ['taxonomy', 'term']).",
        )
    else:
        say(OK, "taxonomies bloquees et non liees")


# ----------------------------------------------------------------------------
# 8. Build sans avertissement
# ----------------------------------------------------------------------------


def check_build_clean() -> None:
    section("Build")
    try:
        proc = subprocess.run(
            ["hugo", "--renderToMemory", "--gc", "--enableGitInfo"],
            cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        say(NOTE, "build local impossible", str(exc)[:70])
        return

    noisy = [
        l for l in (proc.stdout + proc.stderr).splitlines()
        if re.search(r"\b(WARN|ERROR|deprecated)\b", l, flags=re.I)
    ]
    if proc.returncode != 0:
        say(ERR, "le build echoue", (proc.stderr or proc.stdout).strip().splitlines()[-1][:90])
    elif noisy:
        say(
            ERR,
            f"{len(noisy)} avertissement(s) au build",
            "",
            *[l.strip()[:88] for l in noisy[:4]],
        )
        say(NOTE, "la CI utilise --panicOnWarning", "ces avertissements y bloqueraient le deploiement")
    else:
        say(OK, "build sans avertissement")


# ----------------------------------------------------------------------------


def selftest() -> int:
    """Prouve que les deux detecteurs cles mordent reellement.

    Un controle qui ne se declenche jamais ne vaut rien, et c'est invisible tant
    que le projet est sain. Ces fixtures reproduisent les deux bugs reellement
    rencontres sur ban.ga.
    """
    print("hugo_doctor --selftest\n")
    failures = 0

    # Fixture 1 : la configuration telle qu'elle etait avant correction, ou huit
    # drapeaux PaperMod etaient captures par [params.schema].
    params_casses = {
        "author": "BANGA Romaric",
        "schema": {
            "publisherType": "Person",
            "showShareButtons": True,
            "showCodeCopyButtons": True,
        },
    }
    refs = {"showsharebuttons": {"layouts/posts/single.html"}}
    found = find_misplaced_params(params_casses, refs)
    if len(found) == 1 and found[0][0] == "showsharebuttons":
        print("  ok    placement : le drapeau capture par params.schema est detecte")
    else:
        print(f"  ECHEC placement : attendu 1 detection, obtenu {found}")
        failures += 1

    # Contre-exemple : la meme cle, bien placee, ne doit rien declencher.
    params_sains = {"author": "x", "showShareButtons": True, "schema": {"publisherType": "Person"}}
    if not find_misplaced_params(params_sains, refs):
        print("  ok    placement : aucun faux positif quand la cle est a la racine")
    else:
        print("  ECHEC placement : faux positif sur une configuration saine")
        failures += 1

    # Fixture 2 : partialCached sans cle de variante, le piege du footer PaperMod.
    cas = [
        ('{{ partialCached "footer.html" . }}', True),
        ('{{- partialCached "header.html" . .Page -}}', False),
        ('{{ partialCached "footer.html" . .Layout .Kind }}', False),
        ('{{ partial "footer.html" . }}', False),
    ]
    for source, attendu in cas:
        trouve = bool(RX_PARTIAL_CACHED.search(source))
        if trouve == attendu:
            print(f"  ok    partialCached : {'detecte' if attendu else 'ignore'} -> {source[:46]}")
        else:
            print(f"  ECHEC partialCached : {source}")
            failures += 1

    print(f"\n  {failures} echec(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    global _quiet
    parser = argparse.ArgumentParser(description="Controle de sante du site Hugo.")
    parser.add_argument("--ci", action="store_true",
                        help="saute le build local, deja couvert par l'etape de build")
    parser.add_argument("--quiet", action="store_true",
                        help="n'affiche que les erreurs et les alertes")
    parser.add_argument("--selftest", action="store_true",
                        help="verifie que les detecteurs se declenchent bien")
    args = parser.parse_args(argv)
    _quiet = args.quiet

    if args.selftest:
        return selftest()

    config_path = ROOT / "hugo.toml"
    if not config_path.exists():
        print("hugo.toml introuvable")
        return 1
    with config_path.open("rb") as fh:
        config = tomllib.load(fh)

    print(f"hugo_doctor : {ROOT}")

    check_param_placement(config)
    check_content_frontmatter()
    check_template_apis()
    check_render_hooks()
    check_version_drift()
    check_config_guards(config)
    check_theme_untouched()
    check_indexing_coherence(config)
    if not args.ci:
        check_build_clean()

    print("\n" + "=" * 68)
    print(f"  {_counts[ERR]} erreur(s), {_counts[WARN]} alerte(s)")
    return 1 if _counts[ERR] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
