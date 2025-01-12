from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sympy import symbols, lambdify, pi, sin, cos

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/analyze', methods=['POST'])
def analyze_signal():
    # Get signal data from request
    signal_expression = request.json.get('signal', '')
    fs = request.json.get('sampling_frequency', 1000)  # Default to 1000 Hz if not provided

    # Validate signal expression and fs
    if not signal_expression:
        return jsonify({'error': 'No signal expression provided.'}), 400
    if not isinstance(fs, (int, float)) or fs <= 0:
        return jsonify({'error': 'Invalid sampling frequency provided.'}), 400

    try:
        # Define the time variable and parse the signal expression
        t = symbols('t')
        signal_expr = eval(signal_expression, {"t": t, "pi": pi, "sin": sin, "cos": cos})

        # Generate time vector
        L = 1000  # Default number of samples
        T = 1 / fs  # Sampling period
        time_values = np.linspace(0, (L - 1) * T, L)

        # Convert symbolic expression to a numerical function
        signal_func = lambdify(t, signal_expr, modules=["numpy"])
        signal = signal_func(time_values)

        # Perform Fourier Transform
        Y = np.fft.fft(signal)  # Compute FFT
        P2 = np.abs(Y) / L      # Two-sided spectrum
        P1 = P2[:L // 2 + 1]    # Single-sided spectrum
        P1[1:-1] *= 2           # Scale magnitudes

        # Frequency vector
        f = fs * np.arange(0, L // 2 + 1) / L

        # Compute phase spectrum
        phase = np.angle(Y[:L // 2 + 1])

        # Prepare results
        results = {
            "time_domain": {
                "time": time_values.tolist(),
                "signal": signal.tolist(),
            },
            "magnitude_spectrum": {
                "frequencies": f.tolist(),
                "magnitudes": P1.tolist(),
            },
            "phase_spectrum": {
                "frequencies": f.tolist(),
                "phases": phase.tolist(),
            },
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
