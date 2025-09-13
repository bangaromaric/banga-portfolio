# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-based portfolio website for BANGA Romaric Tanguy, a Spring Boot developer and Google Developers Group Libreville organizer. The site uses the PaperMod theme as a Git submodule and is configured for deployment on GitHub Pages.

## Build and Development Commands

**Note**: Hugo is not currently installed on this system. You may need to install Hugo first:
```bash
# Install Hugo (varies by system)
# On Ubuntu/Debian: sudo apt install hugo
# On macOS: brew install hugo
# On Windows: choco install hugo
```

Common development commands:
```bash
# Start development server (requires Hugo installation)
hugo server -D

# Build the site for production
hugo

# Update the PaperMod theme submodule
git submodule update --remote themes/PaperMod
```

## Architecture

### Site Structure
- `hugo.toml` - Main configuration file with site settings, menu structure, and GitHub Pages deployment config
- `content/` - Markdown content files organized by page type
  - `_index.md` - Homepage content
  - `about.md` - About page 
  - `projects/` - Project showcase pages
- `themes/PaperMod/` - Git submodule containing the PaperMod theme
- `static/` - Static assets (images, files)
- `layouts/` - Custom layout overrides (if needed)
- `public/` - Generated static site (created by Hugo build)

### Configuration Details
- Site language: French (`languageCode = 'fr'`)
- Deployment: GitHub Pages (`baseURL = 'https://banga.github.io'`)
- Theme: PaperMod (managed as Git submodule)
- Menu structure includes: Accueil, À propos, Projets, Blog, GDG Libreville

### Content Management
- All content is in French
- Projects are stored in `content/projects/` with individual Markdown files
- The site focuses on Spring Boot development expertise and GDG Libreville activities
- Uses Hugo's front matter for page metadata

## Git Submodule Management

The PaperMod theme is managed as a Git submodule. When working with this repository:

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>

# Update submodule to latest version
git submodule update --remote themes/PaperMod

# Initialize submodules if not done during clone
git submodule init
git submodule update
```

## Deployment

The site uses GitHub Actions for automated deployment to GitHub Pages. The workflow (`.github/workflows/hugo.yml`) automatically:
- Triggers on pushes to the `main` branch
- Sets up Hugo with the latest extended version
- Builds the site with `--gc --minify` flags
- Deploys to GitHub Pages

Manual deployment is not needed - simply push changes to the `main` branch and GitHub Actions will handle the build and deployment automatically.