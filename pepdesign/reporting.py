"""
Reporting module.
Generates interactive HTML reports with 3D visualization.
"""
import os
import pandas as pd
from typing import List, Dict, Any

from pepdesign.utils import load_csv, load_json

def generate_html_report(
    ranked_csv: str,
    output_html: str,
    top_n: int = 5
) -> None:
    """
    Generate an interactive HTML report for the top ranked designs.
    
    Args:
        ranked_csv: Path to ranked.csv
        output_html: Path to write output HTML
        top_n: Number of top designs to visualize
    """
    print(f"[Reporting] Generating HTML report for top {top_n} designs...")
    
    df = load_csv(ranked_csv)
    
    # Filter for passing sequences
    df_passed = df[df['passes_filters'] == True]
    
    if len(df_passed) == 0:
        print("  Warning: No sequences passed filters. Report will be empty.")
        return
        
    top_designs = df_passed.head(top_n)
    
    # Start HTML construction
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>PepDesign Report</title>
        <!-- Load jQuery FIRST -->
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <!-- Then load 3Dmol.js -->
        <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
        <style>
            body {{ font-family: sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .design-card {{ border: 1px solid #ddd; margin-bottom: 20px; padding: 15px; border-radius: 4px; display: flex; }}
            .viewer {{ width: 500px; height: 400px; position: relative; border: 1px solid #eee; margin-right: 20px; }}
            .details {{ flex: 1; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #eee; }}
            th {{ background-color: #f9f9f9; }}
            .badge {{ padding: 4px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }}
            .badge-success {{ background-color: #d4edda; color: #155724; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PepDesign Results Report</h1>
            <p>Generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
            
            <h2>Top {len(top_designs)} Candidates</h2>
    """
    
    for i, row in top_designs.iterrows():
        design_id = row['design_id']
        pdb_path = row['pdb_path']
        
        # Resolve PDB path relative to ranked.csv directory
        # ranked.csv is in: examples/mdm2_p53/output_v2/ranking/ranked.csv
        # pdb_path in CSV is: output_v2\backbones\backbone_X.pdb
        # So we need to go up 2 levels: ranking/ -> output_v2/ -> mdm2_p53/
        if not os.path.isabs(pdb_path):
            ranked_dir = os.path.dirname(os.path.abspath(ranked_csv))
            example_dir = os.path.dirname(os.path.dirname(ranked_dir))  # Go up 2 levels
            pdb_path = os.path.join(example_dir, pdb_path)
            pdb_path = os.path.normpath(pdb_path)  # Normalize path separators
        
        # Read PDB content for embedding
        pdb_content = ""
        try:
            with open(pdb_path, 'r') as f:
                pdb_content = f.read()
        except Exception as e:
            print(f"  Warning: Could not read PDB {pdb_path}: {e}")
            continue
            
        # Escape backticks for JS template literal
        pdb_content_js = pdb_content.replace('`', '\\`')
        
        html_content += f"""
        <div class="design-card">
            <div id="viewer_{i}" class="viewer"></div>
            <div class="details">
                <h3>#{row['rank']} - {design_id}</h3>
                <table>
                    <tr><th>Sequence</th><td style="font-family: monospace; font-size: 1.1em;">{row['peptide_seq']}</td></tr>
                    <tr><th>Composite Score</th><td>{row['composite_score']:.3f}</td></tr>
                    <tr><th>Net Charge</th><td>{row['net_charge']:.2f}</td></tr>
                    <tr><th>Hydrophobicity</th><td>{row['hydrophobic_fraction']:.2f}</td></tr>
                    <tr><th>MPNN Score</th><td>{row.get('mpnn_log_prob', row.get('score', 'N/A'))}</td></tr>
                </table>
            </div>
        </div>
        <script>
            $(function() {{
                let element = $('#viewer_{i}');
                let config = {{ backgroundColor: 'white' }};
                let viewer = $3Dmol.createViewer(element, config);
                viewer.addModel(`{pdb_content_js}`, "pdb");
                viewer.setStyle({{chain: 'A'}}, {{cartoon: {{color: 'lightgray'}}}});
                viewer.setStyle({{chain: 'B'}}, {{stick: {{colorscheme: 'greenCarbon'}}}});
                viewer.zoomTo();
                viewer.render();
            }});
        </script>
        """
        
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(output_html, 'w') as f:
        f.write(html_content)
        
    print(f"[Reporting] Wrote HTML report to {output_html}")
