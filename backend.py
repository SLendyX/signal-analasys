from flask import Flask, request, jsonify
from flask_cors import CORS
import matlab.engine
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/analyze', methods=['POST'])
def analyze_signal():
    # Start MATLAB engine
    eng = matlab.engine.start_matlab()
    eng.addpath('./', nargout=0)

    # Get signal data from request
    signal_data = request.json.get('signal', '')
    fs = 1000

    

    # Validate signal data and fs
    if not signal_data:
        return jsonify({'error': 'No signal data provided.'}), 400
    if not isinstance(fs, (int, float)) or fs <= 0:
        return jsonify({'error': 'Invalid sampling frequency provided.'}), 400

    try:
        # Define parameters in MATLAB workspace
        L = 1000  # Default number of samples
        T = 1 / fs
        t = [i * T for i in range(L)]
        eng.workspace['t'] = matlab.double(t)  # Pass 't' as a numeric vector

        # Evaluate the signal
        eng.workspace['custom_signal'] = eng.eval(signal_data)

        # Run the MATLAB script
        eng.eval('run("fourier_analysis.m")', nargout=0)

        

        # Retrieve results
        time_domain = eng.workspace['time_domain']
        magnitude_spectrum = eng.workspace['magnitude_spectrum']
        phase_spectrum = eng.workspace['phase_spectrum']

        # print(time_domain)

        # results = {
        #     "time_domain": {
        #         "time": np.double(time_domain['time']).tolist(),
        #     }
        # }
        results = {
            "time_domain": {
                "time": np.double(time_domain['time']).tolist(),
                "signal": np.double(time_domain['signal']).tolist(),
            },
            "magnitude_spectrum": {
                "frequencies": np.double(magnitude_spectrum['frequencies']).tolist(),
                "magnitudes": np.double(magnitude_spectrum['magnitudes']).tolist(),
            },
            "phase_spectrum": {
                "frequencies": np.double(phase_spectrum['frequencies']).tolist(),
                "phases": np.double(phase_spectrum['phases']).tolist(),
            },
        }
        print(results)

        eng.quit()
        return jsonify(results)

    except Exception as e:
        eng.quit()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)