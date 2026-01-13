# Guide de contribution

Merci de votre intérêt pour ce projet ! Voici comment contribuer.

## 🐛 Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](../../issues)
2. Créez une nouvelle issue avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Version Python et dépendances

## 💡 Proposer une amélioration

1. Ouvrez une issue pour discuter de l'idée
2. Attendez la validation avant de coder

## 🔧 Contribuer du code

### Prérequis

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/rfe-antibioprophylaxie.git
cd rfe-antibioprophylaxie

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances dev
pip install -r requirements.txt
```

### Workflow

1. Créez une branche pour votre modification :
   ```bash
   git checkout -b feature/ma-feature
   ```

2. Faites vos modifications

3. Formatez le code :
   ```bash
   black src/ tests/
   ruff check src/ tests/
   ```

4. Lancez les tests :
   ```bash
   pytest tests/ -v
   ```

5. Commitez avec un message clair :
   ```bash
   git commit -m "feat: ajout de la fonctionnalité X"
   ```

6. Poussez et créez une Pull Request

### Convention de commits

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `refactor:` refactoring sans changement fonctionnel
- `test:` ajout/modification de tests
- `chore:` maintenance

## 📋 Checklist PR

- [ ] Code formaté avec Black
- [ ] Pas d'erreurs Ruff
- [ ] Tests passent
- [ ] Documentation mise à jour si nécessaire
- [ ] Commit messages clairs

## ⚠️ Notes importantes

- Les données médicales doivent être vérifiées par un professionnel de santé
- Tout changement de données doit référencer la source officielle SFAR
- Respectez la licence MIT

## 📬 Contact

Pour toute question, ouvrez une issue ou contactez le Groupe Numérique SFAR.
