# CompressLab — clone fonctionnel BZIP2, LZMA et 7-Zip

Application de bureau Python/Tkinter pour compresser et décompresser des fichiers, afficher la taille initiale, la taille obtenue, la réduction de taille et le temps d'exécution.

## Prérequis
- Python 3.10 ou supérieur
- Tkinter (généralement inclus avec Python)
- Une interface graphique est requise pour l'application ; si tu exécutes depuis un terminal SSH sans bureau, Tkinter échouera avec une erreur de display.
- Pour l'option 7-Zip : installer 7-Zip et rendre `7z` (Windows) ou `7zz` (Linux/macOS) accessible dans le PATH.

## Lancer l'application
Depuis le dossier du projet :

```bash
python main.py
```

Sur certaines installations, il faut utiliser `python3 main.py`.

## Fonctionnalités
- Choix d'un fichier local
- Compression avec BZIP2, LZMA ou 7-Zip
- Décompression avec l'algorithme choisi
- Mesure du temps et calcul de la réduction de taille
- Gestion des erreurs courantes

## Extensions de sortie
- BZIP2 : `.bz2`
- LZMA : `.xz`
- 7-Zip : `.7z`

## Préparer les essais du rapport
Effectuer des tests séparés sur :
1. un fichier texte (`.txt`)
2. un fichier audio (`.mp3` ou `.wav`)
3. une image (`.jpg`, `.png`)
4. une vidéo (`.mp4`)

Pour chaque test, noter l'algorithme, la taille originale, la taille compressée, la réduction de taille et le temps écoulé. Les formats déjà compressés (MP3, JPEG, MP4) peuvent peu diminuer ou même grossir : ce résultat est normal.

Formule :
`Réduction (%) = (1 - taille_compressée / taille_originale) × 100`

## Limites connues
- Le mode BZIP2/LZMA lit le fichier entier en mémoire ; pour les très gros fichiers, une version par blocs serait préférable.
- Le mode 7-Zip dépend d'un exécutable externe.
- Cette application orchestre des implémentations existantes ; elle ne réimplémente pas de zéro les algorithmes internes de BZIP2, LZMA ou 7-Zip.
- Pour éviter toute perte, conserver les fichiers originaux pendant les essais.
