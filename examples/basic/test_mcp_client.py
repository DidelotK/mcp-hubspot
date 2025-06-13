#!/usr/bin/env python3
"""
Script d'exemple pour tester le serveur MCP HubSpot.

Ce script démontre comment utiliser un client MCP pour se connecter
au serveur HubSpot et récupérer des contacts.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour importer mcp
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ Erreur: Le package 'mcp' n'est pas installé.")
    print("Installez-le avec: pip install mcp")
    sys.exit(1)


async def test_list_contacts(session, limit=5):
    """Test de récupération des contacts."""
    print("\n🧪 Test 1: Récupération des contacts...")
    try:
        result = await session.call_tool(
            "list_hubspot_contacts", arguments={"limit": limit}
        )

        if result.content:
            print("✅ Contacts récupérés avec succès:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
        else:
            print("⚠️ Aucun contenu retourné")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des contacts: {e}")
        return False
    return True


async def test_search_contacts(session, limit=3, search_term="test"):
    """Test de recherche de contacts avec filtre."""
    print("\n🧪 Test 2: Recherche de contacts avec filtre...")
    try:
        result = await session.call_tool(
            "list_hubspot_contacts",
            arguments={"limit": limit, "filters": {"search": search_term}},
        )

        if result.content:
            print("✅ Recherche effectuée avec succès:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
        else:
            print("⚠️ Aucun résultat trouvé pour la recherche")

    except Exception as e:
        print(f"❌ Erreur lors de la recherche: {e}")
        return False
    return True


async def test_list_companies(session, limit=3):
    """Test de récupération des entreprises."""
    print("\n🧪 Test 3: Récupération des entreprises...")
    try:
        result = await session.call_tool(
            "list_hubspot_companies", arguments={"limit": limit}
        )

        if result.content:
            print("✅ Entreprises récupérées avec succès:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
        else:
            print("⚠️ Aucune entreprise trouvée")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des entreprises: {e}")
        return False
    return True


async def test_list_deals(session, limit=3):
    """Test de récupération des transactions."""
    print("\n🧪 Test 4: Récupération des transactions...")
    try:
        result = await session.call_tool(
            "list_hubspot_deals", arguments={"limit": limit}
        )

        if result.content:
            print("✅ Transactions récupérées avec succès:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
        else:
            print("⚠️ Aucune transaction trouvée")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des transactions: {e}")
        return False
    return True


async def test_list_engagements(session, limit=3):
    """Test retrieval of engagements."""
    print("\n🧪 Test 5: Récupération des engagements...")
    try:
        result = await session.call_tool(
            "list_hubspot_engagements",
            arguments={"limit": limit},
        )

        if result.content:
            print("✅ Engagements récupérés avec succès:")
            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)
        else:
            print("⚠️ Aucun engagement trouvé")

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des engagements: {e}")
        return False
    return True


async def test_hubspot_mcp_server():
    """Test du serveur MCP HubSpot en récupérant les contacts."""

    # Vérifier que la clé API HubSpot est définie
    hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
    if not hubspot_api_key:
        print(
            "❌ Erreur: La variable d'environnement HUBSPOT_API_KEY n'est pas définie."
        )
        print("Définissez-la avec: export HUBSPOT_API_KEY='votre_cle_api'")
        return False

    print("🚀 Démarrage du test du serveur MCP HubSpot...")
    print(f"🔑 Clé API HubSpot: {hubspot_api_key[:10]}...")

    # Chemin vers le serveur MCP
    server_script_path = Path(__file__).parent.parent.parent / "main.py"

    # Configuration du serveur
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script_path), "--mode", "stdio"],
        env={"HUBSPOT_API_KEY": hubspot_api_key},
    )

    try:
        # Connexion au serveur MCP
        print("🔌 Connexion au serveur MCP...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:

                # Initialiser la session
                print("🤝 Initialisation de la session MCP...")
                await session.initialize()

                # Lister les outils disponibles
                print("📋 Récupération de la liste des outils...")
                tools = await session.list_tools()

                print(f"✅ {len(tools.tools)} outils disponibles:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Exécuter les tests
                success = True
                success &= await test_list_contacts(session)
                success &= await test_search_contacts(session)
                success &= await test_list_companies(session)
                success &= await test_list_deals(session)
                success &= await test_list_engagements(session)

                if success:
                    print("\n🎉 Tests terminés avec succès!")
                return success

    except Exception as e:
        print(f"❌ Erreur de connexion au serveur MCP: {e}")
        print("Vérifiez que:")
        print("- Le serveur MCP est accessible")
        print("- La clé API HubSpot est valide")
        print("- Les dépendances sont installées")
        return False


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("🧪 TEST DU SERVEUR MCP HUBSPOT")
    print("=" * 60)

    # Vérifier les prérequis
    if not os.getenv("HUBSPOT_API_KEY"):
        print("\n❌ Configuration manquante!")
        print("Définissez votre clé API HubSpot:")
        print("export HUBSPOT_API_KEY='votre_cle_api_hubspot'")
        sys.exit(1)

    # Lancer les tests
    try:
        success = asyncio.run(test_hubspot_mcp_server())
        if success:
            print("\n✅ Tous les tests ont réussi!")
            sys.exit(0)
        else:
            print("\n❌ Certains tests ont échoué.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
