from flask import Flask, render_template, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

# Get all Python scripts in the current directory
def get_available_scripts():
    """Get list of all Python scripts in the current directory"""
    scripts = []
    for file in os.listdir('.'):
        if file.endswith('.py') and file != 'app.py':
            scripts.append(file)
    return sorted(scripts)

@app.route('/')
def index():
    """Main page showing available scripts"""
    scripts = get_available_scripts()
    return render_template('index.html', scripts=scripts)

@app.route('/api/scripts')
def list_scripts():
    """API endpoint to list all available scripts"""
    scripts = get_available_scripts()
    return jsonify({'scripts': scripts})

@app.route('/api/run/<script_name>', methods=['POST'])
def run_script(script_name):
    """API endpoint to run a specific script"""
    scripts = get_available_scripts()
    
    if script_name not in scripts:
        return jsonify({'error': 'Script not found'}), 404
    
    try:
        # Get optional arguments from request
        args = request.json.get('args', []) if request.json else []
        
        # Run the script
        cmd = ['python', script_name] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=os.getcwd()
        )
        
        return jsonify({
            'script': script_name,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script execution timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/info/<script_name>')
def script_info(script_name):
    """Get basic info about a script"""
    scripts = get_available_scripts()
    
    if script_name not in scripts:
        return jsonify({'error': 'Script not found'}), 404
    
    try:
        # Read first few lines to get docstring/comments
        with open(script_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]  # First 20 lines
        
        return jsonify({
            'name': script_name,
            'preview': ''.join(lines),
            'size': os.path.getsize(script_name)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9988, debug=True)
