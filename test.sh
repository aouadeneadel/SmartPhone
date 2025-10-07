# Initialisez git dans votre dossier projet
cd /chemin/vers/votre/projet
git init

# Ajoutez tous vos fichiers
git add .

# Faites votre premier commit
git commit -m "Premier commit"

# Liez votre dépôt local à GitHub
git remote add origin https://github.com/votre-username/nom-du-repo.git

# Poussez votre code
git branch -M main
git push -u origin main
