from flask import Flask, render_template_string, request, send_file
import qrcode
import io
import base64
import urllib.parse

app = Flask(__name__)

# --- CYBERPUNK FRONTEND TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyberpunk QR Code Generator</title>
    <!-- Tailwind CSS v4 CDN -->
    <script src="https://unpkg.com/@tailwindcss/browser@4"></script>
    <style>
        body {
            background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
        }
        .glass-panel {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.25);
        }
        .neon-input:focus {
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 15px rgba(37, 99, 235, 0.6); }
            50% { box-shadow: 0 0 25px rgba(56, 189, 248, 0.9); }
        }
        .pulse-btn {
            animation: pulse-glow 2s infinite;
        }
    </style>
</head>
<body class="min-h-screen text-slate-100 flex items-center justify-center p-4">
    <div class="w-full max-w-xl glass-panel rounded-2xl p-6 md:p-8 shadow-2xl">
        <div class="text-center mb-6">
            <h1 class="text-2xl md:text-3xl font-extrabold tracking-wider text-cyan-400 uppercase">
                ⚡ Cyber QR Generator
            </h1>
            <p class="text-slate-400 text-sm mt-1">Transform any text, link, or data into a sleek QR code instantly</p>
        </div>

        <form method="POST" class="space-y-4">
            <div>
                <label class="block text-xs font-semibold uppercase text-cyan-300 mb-1">Enter Text or URL</label>
                <input type="text" name="data" required value="{{ data if data else '' }}" placeholder="https://example.com or your custom text" 
                       class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-3 text-sm text-slate-200 neon-input outline-none transition">
            </div>

            <button type="submit" class="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 font-bold text-white rounded-lg transition duration-200 pulse-btn cursor-pointer uppercase tracking-wider text-sm">
                🚀 Generate QR Code
            </button>
        </form>

        {% if qr_image %}
        <div class="mt-8 text-center border-t border-slate-700/60 pt-6">
            <div class="inline-block p-4 bg-white rounded-xl shadow-2xl mb-4">
                <img src="data:image/png;base64,{{ qr_image }}" alt="Generated QR Code" class="w-48 h-48 mx-auto object-contain">
            </div>
            <div>
                <a href="/download?data={{ url_encode_data }}" class="inline-block px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold rounded-lg text-sm transition shadow-lg uppercase tracking-wider">
                    📥 Download QR Image
                </a>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    qr_image = None
    data = ""
    if request.method == 'POST':
        data = request.form.get('data', '')
        if data:
            # Generate QR Code using python qrcode library
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to memory buffer
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            
            # Encode to base64 for direct inline rendering
            qr_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    encoded_data = urllib.parse.quote(data) if data else ""
    return render_template_string(HTML_TEMPLATE, qr_image=qr_image, data=data, url_encode_data=encoded_data)

@app.route('/download')
def download():
    data = request.args.get('data', '')
    if not data:
        return "No data provided", 400
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name="cyber_qrcode.png",
        mimetype='image/png'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
