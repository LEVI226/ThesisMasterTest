# Diarisation — vérification du 16 septembre 2026

## Conclusion

La configuration Hugging Face était présente. Le blocage reproduit était une incompatibilité de dépendances, pas la preuve d'une absence de configuration. Après correction, pyannote et Whisper exécutent ensemble une inférence réelle sur GPU dans l'environnement du projet. Cela ne valide pas encore la précision de la diarisation.

## Causes et corrections

1. Le chargement de pyannote importait NeMo / OneLogger et échouait sur la signature `save_checkpoint` de Lightning 2.6. Versions alignées : lightning et pytorch-lightning 2.4.0.
2. CTranslate2 4.7.1 fournissait une DLL cuDNN 9.10, incompatible en processus partagé avec les DLL cuDNN 9.1 de PyTorch 2.6+cu124. Le crash natif `Could not load symbol cudnnGetLibConfig` a été reproduit. CTranslate2 4.6.0, qui fournit cuDNN 9.1, a passé le même test. Sous Windows, setuptools 80.9.0 conserve `pkg_resources` requis par cette version.
3. Le chemin fichier transmettait un nom de fichier au décodeur pyannote indisponible et supposait une ancienne sortie. Il transmet maintenant une onde mono à 16 kHz décodée par librosa et accepte la sortie `speaker_diarization` de pyannote 4 ainsi que l'ancienne annotation.

Les versions sont inscrites dans pyproject.toml et uv.lock. Aucun jeton n'a été changé ou reproduit ici.

## Vérifications

- `tests_final.log` : 68 tests réussis, 5 avertissements. Deux nouveaux cas couvrent la conversion du fichier stéréo 8 kHz et les deux formats de sortie.
- `application_final.log` : script `check_application.py` terminé avec code 0 dans la vraie `.venv`, sans les dossiers de dépendances expérimentales.
- `application_after.json` : Whisper tiny, CUDA, float16, RTX 4060 Laptop ; diarisation chargée ; sur un extrait de 25 secondes du fichier simulé `meeting_fr_clean_2spk.wav`, les segments portent SPEAKER_00 et SPEAKER_01.
- La méthode live a traité 10 secondes avec les vrais modèles et renvoyé du texte avec SPEAKER_00. Seul le transport WebSocket est simulé. Le navigateur et la capture microphone ne sont pas couverts.
- `lock_final.log` : résolution et écriture du verrou réussies.

## Limites qui restent à traiter

- Dans backend/main.py, le live prend le dernier locuteur de la fenêtre de contexte de 10 secondes et l'attribue à tout le bloc de texte. Cela ne fournit pas une attribution précise lors d'un changement à l'intérieur du bloc.
- Les identifiants de locuteurs doivent être vérifiés et stabilisés entre fenêtres : une étiquette locale ne garantit pas une identité constante pendant toute une réunion.
- Le fichier attribue un seul locuteur à chaque segment Whisper par recouvrement ; un segment qui traverse un changement de personne n'est pas découpé à ce changement.
- Les étiquettes de référence A/B des réunions simulées existantes ne constituent pas une annotation fiable des identités vocales. Deux étiquettes produites ne prouvent pas deux personnes correctement reconnues. Aucun DER ni taux de précision n'est établi par ces tests.
- TorchCodec émet encore un avertissement ; le chemin testé utilise les ondes décodées et fonctionne. Les overrides existants torch/torchaudio 2.6 restent inférieurs aux dépendances déclarées de pyannote 4 (>=2.8). Le fonctionnement a été observé ici, mais l'environnement n'est pas entièrement conforme aux métadonnées des paquets. Le conflit wandb/opentelemetry préexistant est également hors de cette réparation.

## Test manuel utile pour la soutenance

Enregistrer deux personnes réelles pendant 1 à 2 minutes avec tours de parole connus : A seul, B seul, alternance rapide, une interruption, puis une même personne changeant de langue. Conserver l'audio et annoter les débuts/fins de parole et l'identité réelle indépendamment de la sortie du système. Comparer ensuite les frontières, les identités et leur stabilité, et calculer le DER avec une convention explicite pour les silences, le chevauchement et la tolérance temporelle.

Formulation défendable aujourd'hui : « La diarisation pyannote est intégrée et son exécution a été vérifiée avec Whisper sur GPU. La précision des attributions et leur stabilité en continu restent à valider sur un enregistrement annoté. »
