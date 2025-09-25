#!/usr/bin/env python3
"""
Generador de Pruebas End-to-End del Sistema NeuroFusion
Genera automáticamente pruebas E2E basadas en la configuración del sistema
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import jinja2

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """Caso de prueba E2E"""

    name: str
    description: str
    steps: List[Dict[str, Any]]
    assertions: List[Dict[str, Any]]
    timeout: int
    retries: int
    dependencies: List[str]
    tags: List[str]


@dataclass
class TestTemplate:
    """Plantilla de prueba E2E"""

    name: str
    description: str
    template_content: str
    variables: Dict[str, Any]
    output_file: str


class E2ETestGenerator:
    """Generador de pruebas end-to-end del sistema NeuroFusion"""

    def __init__(self, e2e_dir: str = "e2e"):
        self.e2e_dir = Path(e2e_dir)
        self.test_cases = []
        self.test_templates = {}
        self.generated_tests = []

        # Inicializar directorios
        self._initialize_directories()

        # Cargar plantillas
        self._load_templates()

        # Cargar casos de prueba
        self._load_test_cases()

    def _initialize_directories(self):
        """Inicializa los directorios necesarios"""
        directories = [
            self.e2e_dir / "generated",
            self.e2e_dir / "templates",
            self.e2e_dir / "test_cases",
            self.e2e_dir / "fixtures",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio inicializado: {directory}")

    def _load_templates(self):
        """Carga las plantillas de pruebas"""
        templates_dir = self.e2e_dir / "templates"

        # Plantillas por defecto
        default_templates = {
            "authentication": {
                "name": "Authentication Test Template",
                "description": "Plantilla para pruebas de autenticación",
                "template_content": """
import { test, expect } from '@playwright/test';

test.describe('{{ test_name }}', () => {
  const baseUrl = '{{ base_url }}';
  const apiUrl = '{{ api_url }}';

  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
  });

  {% for step in steps %}
  test('{{ step.name }}', async ({ page }) => {
    {% for action in step.actions %}
    // {{ action.description }}
    {% if action.type == 'click' %}
    await page.click('{{ action.selector }}');
    {% elif action.type == 'fill' %}
    await page.fill('{{ action.selector }}', '{{ action.value }}');
    {% elif action.type == 'navigate' %}
    await page.goto('{{ action.url }}');
    {% elif action.type == 'wait' %}
    await page.waitForSelector('{{ action.selector }}');
    {% endif %}
    {% endfor %}

    {% for assertion in step.assertions %}
    // {{ assertion.description }}
    {% if assertion.type == 'visible' %}
    await expect(page.locator('{{ assertion.selector }}')).toBeVisible();
    {% elif assertion.type == 'text' %}
    await expect(page.locator('{{ assertion.selector }}')).toHaveText('{{ assertion.value }}');
    {% elif assertion.type == 'url' %}
    await expect(page).toHaveURL(/{{ assertion.pattern }}/);
    {% elif assertion.type == 'count' %}
    await expect(page.locator('{{ assertion.selector }}')).toHaveCount({{ assertion.count }});
    {% endif %}
    {% endfor %}
  });
  {% endfor %}
});
""",
                "variables": {
                    "base_url": "http://127.0.0.1:3000",
                    "api_url": "http://127.0.0.1:8000",
                },
                "output_file": "generated/authentication.spec.ts",
            },
            "chat_interaction": {
                "name": "Chat Interaction Test Template",
                "description": "Plantilla para pruebas de interacción con chat",
                "template_content": """
import { test, expect } from '@playwright/test';

test.describe('{{ test_name }}', () => {
  const baseUrl = '{{ base_url }}';

  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
    // Login setup
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', '{{ test_user }}');
    await page.fill('input[name="password"]', '{{ test_password }}');
    await page.click('button[type="submit"]');
  });

  {% for step in steps %}
  test('{{ step.name }}', async ({ page }) => {
    // Navigate to chat
    await page.click('text=Chat IA');
    
    {% for action in step.actions %}
    // {{ action.description }}
    {% if action.type == 'send_message' %}
    await page.fill('textarea[placeholder*="mensaje"]', '{{ action.message }}');
    await page.click('button:has-text("Enviar")');
    {% elif action.type == 'wait_response' %}
    await expect(page.locator('.message-response')).toBeVisible();
    {% elif action.type == 'check_history' %}
    await expect(page.locator('.chat-history')).toContainText('{{ action.expected_text }}');
    {% endif %}
    {% endfor %}

    {% for assertion in step.assertions %}
    // {{ assertion.description }}
    {% if assertion.type == 'response_received' %}
    await expect(page.locator('.message-response')).toBeVisible();
    {% elif assertion.type == 'message_sent' %}
    await expect(page.locator('text={{ assertion.message }}')).toBeVisible();
    {% elif assertion.type == 'error_handled' %}
    await expect(page.locator('.error-message')).toBeVisible();
    {% endif %}
    {% endfor %}
  });
  {% endfor %}
});
""",
                "variables": {
                    "base_url": "http://127.0.0.1:3000",
                    "test_user": "testuser_e2e",
                    "test_password": "testpassword123",
                },
                "output_file": "generated/chat_interaction.spec.ts",
            },
            "training_system": {
                "name": "Training System Test Template",
                "description": "Plantilla para pruebas del sistema de entrenamiento",
                "template_content": """
import { test, expect } from '@playwright/test';

test.describe('{{ test_name }}', () => {
  const baseUrl = '{{ base_url }}';

  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
    // Login setup
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', '{{ test_user }}');
    await page.fill('input[name="password"]', '{{ test_password }}');
    await page.click('button[type="submit"]');
  });

  {% for step in steps %}
  test('{{ step.name }}', async ({ page }) => {
    // Navigate to training
    await page.click('text=Train AI');
    
    {% for action in step.actions %}
    // {{ action.description }}
    {% if action.type == 'start_session' %}
    await page.click('button:has-text("Iniciar Entrenamiento")');
    {% elif action.type == 'answer_question' %}
    await page.fill('input[name="answer"]', '{{ action.answer }}');
    await page.click('button:has-text("Responder")');
    {% elif action.type == 'complete_exercise' %}
    await page.click('button:has-text("Completar")');
    {% endif %}
    {% endfor %}

    {% for assertion in step.assertions %}
    // {{ assertion.description }}
    {% if assertion.type == 'session_started' %}
    await expect(page.locator('.training-session')).toBeVisible();
    {% elif assertion.type == 'progress_updated' %}
    await expect(page.locator('.progress-bar')).toHaveAttribute('value', '{{ assertion.value }}');
    {% elif assertion.type == 'metrics_displayed' %}
    await expect(page.locator('text=Precisión')).toBeVisible();
    await expect(page.locator('text=Velocidad')).toBeVisible();
    {% endif %}
    {% endfor %}
  });
  {% endfor %}
});
""",
                "variables": {
                    "base_url": "http://127.0.0.1:3000",
                    "test_user": "testuser_e2e",
                    "test_password": "testpassword123",
                },
                "output_file": "generated/training_system.spec.ts",
            },
            "vault_system": {
                "name": "Vault System Test Template",
                "description": "Plantilla para pruebas del sistema de caja fuerte",
                "template_content": """
import { test, expect } from '@playwright/test';

test.describe('{{ test_name }}', () => {
  const baseUrl = '{{ base_url }}';

  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
    // Login setup
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', '{{ test_user }}');
    await page.fill('input[name="password"]', '{{ test_password }}');
    await page.click('button[type="submit"]');
  });

  {% for step in steps %}
  test('{{ step.name }}', async ({ page }) => {
    // Navigate to vault
    await page.click('text=Caja Fuerte');
    
    {% for action in step.actions %}
    // {{ action.description }}
    {% if action.type == 'view_statistics' %}
    await page.click('text=Estadísticas');
    {% elif action.type == 'check_balance' %}
    await page.click('text=Balance');
    {% elif action.type == 'view_experience' %}
    await page.click('text=Experiencia');
    {% endif %}
    {% endfor %}

    {% for assertion in step.assertions %}
    // {{ assertion.description }}
    {% if assertion.type == 'balance_displayed' %}
    await expect(page.locator('text=Balance')).toBeVisible();
    {% elif assertion.type == 'experience_shown' %}
    await expect(page.locator('text=Experiencia')).toBeVisible();
    {% elif assertion.type == 'level_displayed' %}
    await expect(page.locator('text=Nivel')).toBeVisible();
    {% elif assertion.type == 'statistics_accurate' %}
    await expect(page.locator('.balance-amount')).toContainText('{{ assertion.expected_amount }}');
    {% endif %}
    {% endfor %}
  });
  {% endfor %}
});
""",
                "variables": {
                    "base_url": "http://127.0.0.1:3000",
                    "test_user": "testuser_e2e",
                    "test_password": "testpassword123",
                },
                "output_file": "generated/vault_system.spec.ts",
            },
            "api_integration": {
                "name": "API Integration Test Template",
                "description": "Plantilla para pruebas de integración con APIs",
                "template_content": """
import { test, expect } from '@playwright/test';

test.describe('{{ test_name }}', () => {
  const baseUrl = '{{ base_url }}';
  const apiUrl = '{{ api_url }}';

  test.beforeEach(async ({ page }) => {
    await page.goto(baseUrl);
  });

  {% for step in steps %}
  test('{{ step.name }}', async ({ page, request }) => {
    {% for action in step.actions %}
    // {{ action.description }}
    {% if action.type == 'api_call' %}
    const response = await request.post('{{ action.endpoint }}', {
      data: {
        {% for key, value in action.data.items() %}
        '{{ key }}': '{{ value }}',
        {% endfor %}
      }
    });
    expect(response.status()).toBe({{ action.expected_status }});
    {% elif action.type == 'ui_action' %}
    await page.click('{{ action.selector }}');
    {% elif action.type == 'form_fill' %}
    await page.fill('{{ action.selector }}', '{{ action.value }}');
    {% endif %}
    {% endfor %}

    {% for assertion in step.assertions %}
    // {{ assertion.description }}
    {% if assertion.type == 'api_response' %}
    const responseData = await response.json();
    expect(responseData).toHaveProperty('{{ assertion.property }}');
    {% elif assertion.type == 'ui_verification' %}
    await expect(page.locator('{{ assertion.selector }}')).toBeVisible();
    {% elif assertion.type == 'status_code' %}
    expect(response.status()).toBe({{ assertion.code }});
    {% endif %}
    {% endfor %}
  });
  {% endfor %}
});
""",
                "variables": {
                    "base_url": "http://127.0.0.1:3000",
                    "api_url": "http://127.0.0.1:8000",
                },
                "output_file": "generated/api_integration.spec.ts",
            },
        }

        # Guardar plantillas por defecto
        for template_name, template_data in default_templates.items():
            template_file = templates_dir / f"{template_name}.json"
            if not template_file.exists():
                with open(template_file, "w") as f:
                    json.dump(template_data, f, indent=2)

        # Cargar plantillas
        for template_file in templates_dir.glob("*.json"):
            with open(template_file, "r") as f:
                template_data = json.load(f)
                self.test_templates[template_file.stem] = TestTemplate(**template_data)

        logger.info(f"Plantillas cargadas: {len(self.test_templates)}")

    def _load_test_cases(self):
        """Carga los casos de prueba"""
        test_cases_dir = self.e2e_dir / "test_cases"

        # Casos de prueba por defecto
        default_test_cases = {
            "user_registration": {
                "name": "User Registration Test",
                "description": "Prueba el registro de nuevos usuarios",
                "steps": [
                    {
                        "name": "Navigate to registration",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "text=Registrarse",
                                "description": "Click en botón de registro",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "visible",
                                "selector": "form[name='registration']",
                                "description": "Formulario de registro visible",
                            }
                        ],
                    },
                    {
                        "name": "Fill registration form",
                        "actions": [
                            {
                                "type": "fill",
                                "selector": "input[name='username']",
                                "value": "newuser",
                                "description": "Llenar nombre de usuario",
                            },
                            {
                                "type": "fill",
                                "selector": "input[name='email']",
                                "value": "newuser@test.com",
                                "description": "Llenar email",
                            },
                            {
                                "type": "fill",
                                "selector": "input[name='password']",
                                "value": "password123",
                                "description": "Llenar contraseña",
                            },
                        ],
                        "assertions": [],
                    },
                    {
                        "name": "Submit registration",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "button[type='submit']",
                                "description": "Enviar formulario",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "url",
                                "pattern": ".*dashboard",
                                "description": "Redirigido al dashboard",
                            },
                            {
                                "type": "visible",
                                "selector": "text=newuser",
                                "description": "Usuario registrado visible",
                            },
                        ],
                    },
                ],
                "assertions": [],
                "timeout": 30000,
                "retries": 2,
                "dependencies": [],
                "tags": ["authentication", "registration"],
            },
            "user_login": {
                "name": "User Login Test",
                "description": "Prueba el login de usuarios",
                "steps": [
                    {
                        "name": "Navigate to login",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "text=Iniciar Sesión",
                                "description": "Click en botón de login",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "visible",
                                "selector": "form[name='login']",
                                "description": "Formulario de login visible",
                            }
                        ],
                    },
                    {
                        "name": "Fill login form",
                        "actions": [
                            {
                                "type": "fill",
                                "selector": "input[name='username']",
                                "value": "testuser_e2e",
                                "description": "Llenar nombre de usuario",
                            },
                            {
                                "type": "fill",
                                "selector": "input[name='password']",
                                "value": "testpassword123",
                                "description": "Llenar contraseña",
                            },
                        ],
                        "assertions": [],
                    },
                    {
                        "name": "Submit login",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "button[type='submit']",
                                "description": "Enviar formulario",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "url",
                                "pattern": ".*dashboard",
                                "description": "Redirigido al dashboard",
                            },
                            {
                                "type": "visible",
                                "selector": "text=testuser_e2e",
                                "description": "Usuario logueado visible",
                            },
                        ],
                    },
                ],
                "assertions": [],
                "timeout": 30000,
                "retries": 2,
                "dependencies": [],
                "tags": ["authentication", "login"],
            },
            "chat_message_send": {
                "name": "Chat Message Send Test",
                "description": "Prueba el envío de mensajes al chat",
                "steps": [
                    {
                        "name": "Navigate to chat",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "text=Chat IA",
                                "description": "Navegar al chat",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "visible",
                                "selector": ".chat-interface",
                                "description": "Interfaz de chat visible",
                            }
                        ],
                    },
                    {
                        "name": "Send message",
                        "actions": [
                            {
                                "type": "send_message",
                                "message": "Hola, ¿cómo estás?",
                                "description": "Enviar mensaje de prueba",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "message_sent",
                                "message": "Hola, ¿cómo estás?",
                                "description": "Mensaje enviado visible",
                            }
                        ],
                    },
                    {
                        "name": "Wait for response",
                        "actions": [
                            {
                                "type": "wait_response",
                                "description": "Esperar respuesta del IA",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "response_received",
                                "description": "Respuesta recibida",
                            }
                        ],
                    },
                ],
                "assertions": [],
                "timeout": 45000,
                "retries": 3,
                "dependencies": ["user_login"],
                "tags": ["chat", "interaction"],
            },
            "training_session_start": {
                "name": "Training Session Start Test",
                "description": "Prueba el inicio de sesiones de entrenamiento",
                "steps": [
                    {
                        "name": "Navigate to training",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "text=Train AI",
                                "description": "Navegar al entrenamiento",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "visible",
                                "selector": ".training-interface",
                                "description": "Interfaz de entrenamiento visible",
                            }
                        ],
                    },
                    {
                        "name": "Start training session",
                        "actions": [
                            {
                                "type": "start_session",
                                "description": "Iniciar sesión de entrenamiento",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "session_started",
                                "description": "Sesión iniciada correctamente",
                            }
                        ],
                    },
                    {
                        "name": "Check training metrics",
                        "actions": [],
                        "assertions": [
                            {
                                "type": "metrics_displayed",
                                "description": "Métricas de entrenamiento visibles",
                            }
                        ],
                    },
                ],
                "assertions": [],
                "timeout": 60000,
                "retries": 2,
                "dependencies": ["user_login"],
                "tags": ["training", "session"],
            },
            "vault_statistics": {
                "name": "Vault Statistics Test",
                "description": "Prueba la visualización de estadísticas del vault",
                "steps": [
                    {
                        "name": "Navigate to vault",
                        "actions": [
                            {
                                "type": "click",
                                "selector": "text=Caja Fuerte",
                                "description": "Navegar al vault",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "visible",
                                "selector": ".vault-interface",
                                "description": "Interfaz del vault visible",
                            }
                        ],
                    },
                    {
                        "name": "View statistics",
                        "actions": [
                            {
                                "type": "view_statistics",
                                "description": "Ver estadísticas",
                            }
                        ],
                        "assertions": [
                            {
                                "type": "balance_displayed",
                                "description": "Balance visible",
                            },
                            {
                                "type": "experience_shown",
                                "description": "Experiencia visible",
                            },
                            {"type": "level_displayed", "description": "Nivel visible"},
                        ],
                    },
                ],
                "assertions": [],
                "timeout": 30000,
                "retries": 2,
                "dependencies": ["user_login"],
                "tags": ["vault", "statistics"],
            },
        }

        # Guardar casos de prueba por defecto
        for case_name, case_data in default_test_cases.items():
            case_file = test_cases_dir / f"{case_name}.json"
            if not case_file.exists():
                with open(case_file, "w") as f:
                    json.dump(case_data, f, indent=2)

        # Cargar casos de prueba
        for case_file in test_cases_dir.glob("*.json"):
            with open(case_file, "r") as f:
                case_data = json.load(f)
                self.test_cases.append(TestCase(**case_data))

        logger.info(f"Casos de prueba cargados: {len(self.test_cases)}")

    def generate_test_from_template(
        self, template_name: str, test_case: TestCase, variables: Dict[str, Any] = None
    ) -> str:
        """Genera una prueba desde una plantilla"""
        if template_name not in self.test_templates:
            raise ValueError(f"Plantilla no encontrada: {template_name}")

        template = self.test_templates[template_name]

        # Combinar variables de la plantilla con las proporcionadas
        template_vars = template.variables.copy()
        if variables:
            template_vars.update(variables)

        # Agregar datos del caso de prueba
        template_vars.update(
            {
                "test_name": test_case.name,
                "test_description": test_case.description,
                "steps": test_case.steps,
                "timeout": test_case.timeout,
                "retries": test_case.retries,
            }
        )

        # Renderizar plantilla
        jinja_env = jinja2.Environment(autoescape=True)
        template_obj = jinja_env.from_string(template.template_content)
        generated_test = template_obj.render(**template_vars)

        return generated_test

    def generate_all_tests(self) -> List[str]:
        """Genera todas las pruebas basadas en los casos de prueba"""
        generated_files = []

        logger.info("Generando todas las pruebas E2E")

        # Agrupar casos de prueba por tipo
        test_groups = {}
        for test_case in self.test_cases:
            for tag in test_case.tags:
                if tag not in test_groups:
                    test_groups[tag] = []
                test_groups[tag].append(test_case)

        # Generar pruebas por grupo
        for group_name, test_cases in test_groups.items():
            if group_name in self.test_templates:
                try:
                    # Generar contenido de la prueba
                    test_content = self._generate_group_test(group_name, test_cases)

                    # Guardar archivo generado
                    output_file = self.e2e_dir / "generated" / f"{group_name}.spec.ts"
                    with open(output_file, "w") as f:
                        f.write(test_content)

                    generated_files.append(str(output_file))
                    logger.info(f"Prueba generada: {output_file}")

                except Exception as e:
                    logger.error(f"Error generando prueba para grupo {group_name}: {e}")

        self.generated_tests = generated_files
        return generated_files

    def _generate_group_test(self, group_name: str, test_cases: List[TestCase]) -> str:
        """Genera una prueba para un grupo de casos de prueba"""
        template = self.test_templates[group_name]

        # Preparar variables para la plantilla
        template_vars = template.variables.copy()
        template_vars.update(
            {"test_name": f"{group_name.replace('_', ' ').title()} Tests", "steps": []}
        )

        # Combinar todos los pasos de los casos de prueba
        all_steps = []
        for test_case in test_cases:
            all_steps.extend(test_case.steps)

        template_vars["steps"] = all_steps

        # Renderizar plantilla
        jinja_env = jinja2.Environment(autoescape=True)
        template_obj = jinja_env.from_string(template.template_content)
        generated_test = template_obj.render(**template_vars)

        return generated_test

    def generate_custom_test(
        self,
        test_name: str,
        description: str,
        steps: List[Dict],
        template_name: str = "api_integration",
        variables: Dict[str, Any] = None,
    ) -> str:
        """Genera una prueba personalizada"""
        # Crear caso de prueba temporal
        test_case = TestCase(
            name=test_name,
            description=description,
            steps=steps,
            assertions=[],
            timeout=30000,
            retries=2,
            dependencies=[],
            tags=[template_name],
        )

        # Generar prueba
        test_content = self.generate_test_from_template(
            template_name, test_case, variables
        )

        # Guardar archivo
        output_file = (
            self.e2e_dir
            / "generated"
            / f"{test_name.lower().replace(' ', '_')}.spec.ts"
        )
        with open(output_file, "w") as f:
            f.write(test_content)

        logger.info(f"Prueba personalizada generada: {output_file}")
        return str(output_file)

    def generate_playwright_config(self) -> str:
        """Genera la configuración de Playwright"""
        config_content = """
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  use: {
    baseURL: 'http://127.0.0.1:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  reporter: [
    ['html'],
    ['json', { outputFile: 'e2e/reports/test-results.json' }],
    ['junit', { outputFile: 'e2e/reports/test-results.xml' }]
  ],
  outputDir: 'e2e/reports/',
  globalSetup: require.resolve('./e2e/utils/global-setup.ts'),
  globalTeardown: require.resolve('./e2e/utils/global-teardown.ts'),
});
"""

        config_file = self.e2e_dir / "playwright.config.ts"
        with open(config_file, "w") as f:
            f.write(config_content)

        logger.info(f"Configuración de Playwright generada: {config_file}")
        return str(config_file)

    def generate_global_setup(self) -> str:
        """Genera el archivo de configuración global"""
        setup_content = """
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Setup global test data
  await page.goto('http://127.0.0.1:3000');
  
  // Create test user if needed
  try {
    await page.click('text=Registrarse');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="email"]', 'test_e2e@example.com');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Wait for registration to complete
    await page.waitForURL(/.*dashboard/);
  } catch (error) {
    // User might already exist
    console.log('Test user setup completed');
  }
  
  await browser.close();
}

export default globalSetup;
"""

        setup_file = self.e2e_dir / "utils" / "global-setup.ts"
        setup_file.parent.mkdir(exist_ok=True)

        with open(setup_file, "w") as f:
            f.write(setup_content)

        logger.info(f"Global setup generado: {setup_file}")
        return str(setup_file)

    def generate_global_teardown(self) -> str:
        """Genera el archivo de limpieza global"""
        teardown_content = """
import { chromium, FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Cleanup test data if needed
  try {
    await page.goto('http://127.0.0.1:3000');
    await page.click('text=Iniciar Sesión');
    await page.fill('input[name="username"]', 'testuser_e2e');
    await page.fill('input[name="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Cleanup test data
    // Add cleanup logic here if needed
  } catch (error) {
    console.log('Global teardown completed');
  }
  
  await browser.close();
}

export default globalTeardown;
"""

        teardown_file = self.e2e_dir / "utils" / "global-teardown.ts"
        teardown_file.parent.mkdir(exist_ok=True)

        with open(teardown_file, "w") as f:
            f.write(teardown_content)

        logger.info(f"Global teardown generado: {teardown_file}")
        return str(teardown_file)

    def generate_package_json(self) -> str:
        """Genera el package.json para las pruebas E2E"""
        package_content = {
            "name": "neurofusion-e2e-tests",
            "version": "1.0.0",
            "description": "End-to-End tests for NeuroFusion system",
            "scripts": {
                "test": "playwright test",
                "test:headed": "playwright test --headed",
                "test:ui": "playwright test --ui",
                "test:debug": "playwright test --debug",
                "test:report": "playwright show-report",
                "install-browsers": "playwright install",
                "generate-tests": "python e2e_test_generator.py",
            },
            "devDependencies": {
                "@playwright/test": "^1.40.0",
                "@types/node": "^18.0.0",
                "typescript": "^4.9.0",
            },
            "engines": {"node": ">=16.0.0"},
        }

        package_file = self.e2e_dir / "package.json"
        with open(package_file, "w") as f:
            json.dump(package_content, f, indent=2)

        logger.info(f"Package.json generado: {package_file}")
        return str(package_file)

    def get_generation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la generación de pruebas"""
        return {
            "total_test_cases": len(self.test_cases),
            "total_templates": len(self.test_templates),
            "generated_tests": len(self.generated_tests),
            "generated_files": self.generated_tests,
            "templates_available": list(self.test_templates.keys()),
            "test_cases_by_tag": self._group_test_cases_by_tag(),
        }

    def _group_test_cases_by_tag(self) -> Dict[str, int]:
        """Agrupa casos de prueba por etiqueta"""
        tag_counts = {}
        for test_case in self.test_cases:
            for tag in test_case.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts


# Instancia global del generador E2E
e2e_test_generator = E2ETestGenerator()


def get_e2e_test_generator() -> E2ETestGenerator:
    """Obtiene la instancia global del generador de pruebas E2E"""
    return e2e_test_generator


if __name__ == "__main__":
    # Ejemplo de uso
    generator = E2ETestGenerator()

    # Generar todas las pruebas
    generated_files = generator.generate_all_tests()
    print(f"Pruebas generadas: {len(generated_files)}")

    # Generar configuración
    generator.generate_playwright_config()
    generator.generate_global_setup()
    generator.generate_global_teardown()
    generator.generate_package_json()

    # Mostrar resumen
    summary = generator.get_generation_summary()
    print(f"Resumen de generación: {summary}")
