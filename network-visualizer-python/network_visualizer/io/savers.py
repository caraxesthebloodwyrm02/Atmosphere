import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def save_json_report(data, output_file):
    """Save analysis data to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)


def save_html_report(data, output_file):
    """Render and save an HTML report from analysis data."""
    template_dir = Path(__file__).parent.parent / 'templates'
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('report.html.j2')

    # Separate metrics from general statistics for the template
    report_data = {
        'statistics': data.get('statistics', {}),
        'metrics': {k: v for k, v in data.items() if k != 'statistics'}
    }

    html_content = template.render(report_data)

    with open(output_file, 'w') as f:
        f.write(html_content)
