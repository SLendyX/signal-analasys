from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sympy import symbols, lambdify, pi, sin, cos
from scipy.signal import butter, filtfilt #added

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/analyze', methods=['POST'])
def analyze_signal():
    # Get signal data from request
    signal_expression = request.json.get('signal', 'sin(2*pi*50*t)')
    fs = int(request.json.get('fs', 1000))  # Default to 1000 Hz if not provided

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
        L = int(request.json.get('samples', 1000))  # Default number of samples
        T = 1 / fs  # Sampling period
        time_values = np.linspace(0, (L - 1) * T, L)

        # Convert symbolic expression to a numerical function
        signal_func = lambdify(t, signal_expr, modules=["numpy"])
        signal = signal_func(time_values)

        ### Simulate non-ideal conditions ###
        harmonic_frequencies = [int(numeric_string) for numeric_string in request.json.get('noise', [2 * 50, 3 * 50])]
        harmonic_amplitudes = [np.random.random() for i in range(len(harmonic_frequencies))]

        noise_amplitude = 0.2

      # Add harmonics
        for hf, ha in zip(harmonic_frequencies, harmonic_amplitudes):
            signal += ha * np.sin(2 * np.pi * hf * time_values)

        # Add white noise
        signal += noise_amplitude * np.random.normal(0, 1, len(time_values))


        ### Apply filtering ###
        # Design a low-pass filter to remove the harmonic distortion
        cutoff = float(request.json.get('cutoff', 70))  # Cutoff frequency in Hz
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(4, normal_cutoff, btype='low', analog=False)
        filtered_signal = filtfilt(b, a, signal)

        # Perform Fourier Transform
        Y = np.fft.fft(signal)  # FFT of noisy signal
        Y_filtered = np.fft.fft(filtered_signal)  # FFT of filtered signal
        P2 = np.abs(Y) / L
        P1 = P2[:L // 2 + 1]
        P1[1:-1] *= 2
        P2_filtered = np.abs(Y_filtered) / L
        P1_filtered = P2_filtered[:L // 2 + 1]
        P1_filtered[1:-1] *= 2

        # Frequency vector
        f = fs * np.arange(0, L // 2 + 1) / L
  # Compute phase spectrum
        phase = np.angle(Y[:L // 2 + 1])  # Phase spectrum of noisy signal
        phase_filtered = np.angle(Y_filtered[:L // 2 + 1])  # Phase spectrum of filtered signal

        # Prepare results
        results = {
            "time_domain": {
                "time": time_values.tolist(),
                "noisy_signal": signal.tolist(),
                "filtered_signal": filtered_signal.tolist(),
            },
            "magnitude_spectrum": {
                "frequencies": f.tolist(),
                "original_magnitudes": P1.tolist(),
                "filtered_magnitudes": P1_filtered.tolist(),
            },
            "phase_spectrum": {
                "frequencies": f.tolist(),
                "original_phases": phase.tolist(),
                "filtered_phases": phase_filtered.tolist(),
            }
        }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
