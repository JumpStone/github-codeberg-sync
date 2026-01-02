import os
import requests
from dotenv import load_dotenv

# Lade die Variablen aus der .env Datei
load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
CODEBERG_TOKEN = os.getenv('CODEBERG_TOKEN')
GITHUB_ORG = os.getenv('GITHUB_ORG')
CODEBERG_ORG = os.getenv('CODEBERG_ORG')


def sync_all_repos():
    # 1. Alle Repos von GitHub abrufen
    gh_url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos?per_page=100"
    gh_headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    try:
        repos_response = requests.get(gh_url, headers=gh_headers)
        repos_response.raise_for_status()
        repos = repos_response.json()
    except Exception as e:
        print(f"Fehler beim Abrufen der GitHub Repos: {e}")
        return

    # 2. Codeberg Organisations-ID herausfinden
    cb_headers = {
        'Authorization': f'token {CODEBERG_TOKEN}',
        'Content-Type': 'application/json'
    }

    try:
        org_info = requests.get(
            f"https://codeberg.org/api/v1/orgs/{CODEBERG_ORG}", headers=cb_headers).json()
        org_id = org_info['id']
    except Exception as e:
        print(
            f"Fehler: Konnte Codeberg Orga-ID nicht finden. Existiert die Orga '{CODEBERG_ORG}'? {e}")
        return

    # 3. Mirror-Befehl für jedes Repo senden
    for repo in repos:
        name = repo['name']
        clone_url = repo['clone_url']

        data = {
            "clone_addr": clone_url,
            "mirror": True,         # WICHTIG: Das aktiviert den Dauer-Sync
            "repo_name": name,
            "uid": org_id,
            "service": "github",
            "auth_token": GITHUB_TOKEN  # Damit Codeberg auch private Repos ziehen darf
        }

        response = requests.post(
            "https://codeberg.org/api/v1/repos/migrate", json=data, headers=cb_headers)

        if response.status_code == 201:
            print(f"✅ Mirror erstellt: {name}")
        elif response.status_code == 409:
            print(f"ℹ️ Bereits vorhanden: {name}")
        else:
            print(f"❌ Fehler bei {name}: {response.text}")


if __name__ == "__main__":
    sync_all_repos()
