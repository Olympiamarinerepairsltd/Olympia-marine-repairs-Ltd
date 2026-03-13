# Olympia Marine Repairs LTD — Website (Static)

Στατικό website (HTML/CSS/JS) με δίγλωσση υποστήριξη (EL/EN) και έτοιμο για GitHub Pages.

## Δομή
- `index.html` — Κεντρική
- `about.html` — Ποιοι είμαστε
- `services.html` — Υπηρεσίες
- `contact.html` — Επικοινωνία
- `styles.css` — Στυλ
- `i18n.js` — Μεταφράσεις / language switch
- `assets/` — λογότυπο & icons

## Τοπική προεπισκόπηση
Απλά άνοιξε το `index.html` στον browser **ή** τρέξε έναν μικρό server:
```bash
python -m http.server 8000
```
και πήγαινε στο: http://localhost:8000

## Deploy σε GitHub Pages (χωρίς build)
1. Δημιούργησε νέο repo στο GitHub (π.χ. `olympia-marine-repairs`).
2. Ανέβασε/κάνε push όλα τα αρχεία αυτού του φακέλου στο root του repo.
3. GitHub → **Settings → Pages**
   - Source: **Deploy from a branch**
   - Branch: `main` / folder: `/ (root)`
4. Θα πάρεις URL τύπου: `https://<username>.github.io/<repo>/`

## Σημείωση
Η φόρμα στο `contact.html` είναι demo (εμφανίζει μήνυμα). Αν θέλεις πραγματική αποστολή email, μπορεί να συνδεθεί σε υπηρεσία τύπου Formspree/Netlify Forms ή με δικό σου backend.
