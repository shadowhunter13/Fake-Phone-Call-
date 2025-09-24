from flask import Flask, request, jsonify, render_template_string
from twilio.rest import Client
from threading import Timer
import random
import os
from datetime import datetime

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '+1234567890')
YOUR_PHONE_NUMBER = os.environ.get('YOUR_PHONE_NUMBER', '+1987654321')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

ESCAPE_MESSAGES = [
    "Hi, this is Mom. Can you call me back? It's about dinner tonight.",
    "Hey, it's your boss. We need to discuss that urgent project. Can you call me?",
    "This is Dr. Smith's office. We need to reschedule your appointment.",
    "Hi, this is your landlord. There's an issue with your apartment we need to discuss.",
    "Hey, it's your sister. Emergency with the car. Call me back ASAP!"
]

def make_escape_call(message_text):
    try:
        call = client.calls.create(
            twiml=f'<Response><Say voice="alice">{message_text}</Say><Pause length="3"/><Say voice="alice">Please call me back when you get this.</Say></Response>',
            to=YOUR_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER
        )
        print(f"Escape call initiated! Call SID: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"Error making call: {e}")
        return None

@app.route('/')
def index():
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Social Escape System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .escape-btn {
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                border: none;
                color: white;
                padding: 20px 40px;
                font-size: 24px;
                font-weight: bold;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
                transition: all 0.3s ease;
                width: 100%;
                margin-bottom: 20px;
            }
            .escape-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 15px 40px rgba(255, 107, 107, 0.6);
            }
            .escape-btn:active {
                transform: translateY(0);
            }
            .delay-selector {
                margin: 20px 0;
            }
            .delay-selector select {
                padding: 10px;
                border-radius: 10px;
                border: 2px solid #ddd;
                font-size: 16px;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                display: none;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .emoji {
                font-size: 3em;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🚨</div>
            <h1>ESCAPE</h1>
            <p>Your social emergency exit button</p>
            
            <div class="delay-selector">
                <label for="delay">Call me in:</label>
                <select id="delay">
                    <option value="60">1 minute</option>
                    <option value="120">2 minutes</option>
                    <option value="180">3 minutes</option>
                    <option value="300">5 minutes</option>
                    <option value="30">30 seconds (test)</option>
                </select>
            </div>
            
            <button class="escape-btn" onclick="triggerEscape()">
                🏃‍♂️ GET ME OUT OF HERE!
            </button>
            
            <div id="status" class="status"></div>
        </div>

        <script>
            async function triggerEscape() {
                const delay = document.getElementById('delay').value;
                const status = document.getElementById('status');
                const btn = document.querySelector('.escape-btn');
                
                btn.disabled = true;
                btn.textContent = '🕒 Scheduling escape...';
                
                try {
                    const response = await fetch('/trigger_escape', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            delay: parseInt(delay)
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        status.className = 'status success';
                        status.textContent = `✅ Escape call scheduled! You'll get a call in ${delay} seconds.`;
                        status.style.display = 'block';
                        
                        // Countdown timer
                        let timeLeft = parseInt(delay);
                        btn.textContent = `📞 Call incoming in ${timeLeft}s...`;
                        
                        const countdown = setInterval(() => {
                            timeLeft--;
                            btn.textContent = `📞 Call incoming in ${timeLeft}s...`;
                            
                            if (timeLeft <= 0) {
                                clearInterval(countdown);
                                btn.textContent = '☎️ Your phone should be ringing!';
                                setTimeout(() => {
                                    btn.disabled = false;
                                    btn.textContent = '🏃‍♂️ GET ME OUT OF HERE!';
                                }, 10000);
                            }
                        }, 1000);
                        
                    } else {
                        throw new Error(result.error);
                    }
                } catch (error) {
                    status.className = 'status error';
                    status.textContent = `❌ Error: ${error.message}`;
                    status.style.display = 'block';
                    btn.disabled = false;
                    btn.textContent = '🏃‍♂️ GET ME OUT OF HERE!';
                }
            }
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route('/trigger_escape', methods=['POST'])
def trigger_escape():
    try:
        data = request.json
        delay = data.get('delay', 60)
        
        message = random.choice(ESCAPE_MESSAGES)
        
        timer = Timer(delay, make_escape_call, [message])
        timer.start()
        
        return jsonify({
            'success': True,
            'message': f'Escape call scheduled in {delay} seconds',
            'delay': delay,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'ready', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚨 Social Escape System Starting...")
    print(f"📞 Calls will be made to: {YOUR_PHONE_NUMBER}")
    print(f"📱 From Twilio number: {TWILIO_PHONE_NUMBER}")
    print("🌐 Access your escape button at: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)