#!/usr/bin/env python3
import os
import sys
import json
import requests
from typing import Dict, Any


def generate_slack_message(ci_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generar mensaje de Slack personalizado basado en datos de CI
    """
    # Estado del workflow
    status = ci_data.get("status", "unknown").lower()

    # Definir color del mensaje según el estado
    color_map = {
        "success": "#36a64f",  # Verde para éxito
        "failure": "#ff0000",  # Rojo para fallo
        "cancelled": "#808080",  # Gris para cancelado
    }

    # Información del repositorio y commit
    repo = ci_data.get("repository", "Shaili-AI")
    commit_sha = ci_data.get("sha", "N/A")[:7]
    commit_url = ci_data.get("commit_url", "")
    branch = ci_data.get("branch", "main")
    workflow_name = ci_data.get("workflow_name", "CI Workflow")

    # Construir mensaje
    message_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Workflow:* {workflow_name}\n*Repositorio:* {repo}\n*Rama:* {branch}",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Estado:* {'✅ Éxito' if status == 'success' else '❌ Fallo'}\n*Commit:* <{commit_url}|{commit_sha}>",
            },
        },
    ]

    # Agregar detalles de rendimiento si están disponibles
    try:
        with open("performance_report.json", "r") as f:
            perf_report = json.load(f)

            perf_text = "*Resumen de Rendimiento:*\n"
            for component, metrics in perf_report.get("components", {}).items():
                if "error" in metrics:
                    perf_text += f"• {component}: ❌ ERROR\n"
                else:
                    perf_text += (
                        f"• {component}:\n"
                        f"  - Tiempo: {metrics['execution_time']:.4f}s\n"
                        f"  - Memoria pico: {metrics['memory_peak']} bytes\n"
                    )

            message_blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": perf_text}}
            )
    except FileNotFoundError:
        pass

    # Mensaje completo de Slack
    slack_message = {
        "blocks": message_blocks,
        "attachments": [
            {
                "color": color_map.get(status, "#808080"),
                "fields": [{"title": "Estado", "value": status.upper(), "short": True}],
            }
        ],
    }

    return slack_message


def send_slack_message(webhook_url: str, message: Dict[str, Any]):
    """
    Enviar mensaje a Slack
    """
    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        print("Mensaje enviado exitosamente a Slack")
    except requests.RequestException as e:
        print(f"Error al enviar mensaje a Slack: {e}")
        sys.exit(1)


def main():
    """
    Punto de entrada principal
    """
    # Obtener variables de entorno de GitHub Actions
    ci_data = {
        "status": os.environ.get("CI_STATUS", "unknown"),
        "repository": os.environ.get("GITHUB_REPOSITORY", "Shaili-AI"),
        "sha": os.environ.get("GITHUB_SHA", "N/A"),
        "branch": os.environ.get("GITHUB_REF", "refs/heads/main").replace(
            "refs/heads/", ""
        ),
        "commit_url": f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'Shaili-AI')}/commit/{os.environ.get('GITHUB_SHA', '')}",
        "workflow_name": os.environ.get("GITHUB_WORKFLOW", "CI Workflow"),
    }

    # URL del webhook de Slack (pasado como argumento o variable de entorno)
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("Error: No se proporcionó URL de webhook de Slack")
        sys.exit(1)

    # Generar y enviar mensaje
    slack_message = generate_slack_message(ci_data)
    send_slack_message(webhook_url, slack_message)


if __name__ == "__main__":
    main()
