import subprocess
import json
import os
from datetime import datetime


class SecurityAuditor:
    def __init__(self, base_url):
        self.base_url = base_url
        self.results_dir = "security_audit_results"
        os.makedirs(self.results_dir, exist_ok=True)

    def run_zap_scan(self):
        """Ejecutar escaneo de seguridad con OWASP ZAP"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.results_dir, f"zap_scan_{timestamp}.json")

        zap_command = [
            "zap-cli",
            "quick-scan",
            "--self-contained",
            "--output-format",
            "json",
            "--output-file",
            output_file,
            self.base_url,
        ]

        try:
            subprocess.run(zap_command, check=True)
            print(f"Escaneo ZAP completado. Resultados en {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"Error en escaneo ZAP: {e}")
            return None

    def run_nikto_scan(self):
        """Ejecutar escaneo de vulnerabilidades con Nikto"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.results_dir, f"nikto_scan_{timestamp}.json")

        nikto_command = [
            "nikto",
            "-h",
            self.base_url,
            "-output",
            output_file,
            "-Format",
            "json",
        ]

        try:
            subprocess.run(nikto_command, check=True)
            print(f"Escaneo Nikto completado. Resultados en {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"Error en escaneo Nikto: {e}")
            return None

    def analyze_results(self, zap_results, nikto_results):
        """Analizar resultados de escaneos"""
        vulnerabilities = {"zap_vulnerabilities": [], "nikto_vulnerabilities": []}

        if zap_results and os.path.exists(zap_results):
            with open(zap_results, "r") as f:
                zap_data = json.load(f)
                vulnerabilities["zap_vulnerabilities"] = zap_data.get("site", [])

        if nikto_results and os.path.exists(nikto_results):
            with open(nikto_results, "r") as f:
                nikto_data = json.load(f)
                vulnerabilities["nikto_vulnerabilities"] = nikto_data.get(
                    "vulnerabilities", []
                )

        return vulnerabilities

    def generate_report(self, vulnerabilities):
        """Generar informe de seguridad"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            self.results_dir, f"security_report_{timestamp}.json"
        )

        with open(report_file, "w") as f:
            json.dump(vulnerabilities, f, indent=2)

        print(f"Informe de seguridad generado en {report_file}")
        return report_file


def main():
    base_url = os.getenv("SECURITY_AUDIT_URL", "http://localhost:8000")
    auditor = SecurityAuditor(base_url)

    zap_results = auditor.run_zap_scan()
    nikto_results = auditor.run_nikto_scan()

    vulnerabilities = auditor.analyze_results(zap_results, nikto_results)
    report = auditor.generate_report(vulnerabilities)


if __name__ == "__main__":
    main()
