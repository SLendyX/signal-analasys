% Fourier Signal Analysis Program

% Clear workspace and command window


% Load variables from workspace
Fs = 1000;   % Sampling frequency in Hz           
T = 1/Fs;               % Sampling period in seconds
L = 1000;               % Length of the signal (number of samples)

signal = evalin('base', 'custom_signal'); % Signal from workspace

% Perform Fourier Transform
Y = fft(signal);        % Compute the Fast Fourier Transform (FFT)
P2 = double(abs(Y))/L;          % Two-sided spectrum
P1 = P2(1:L/2+1);       % Single-sided spectrum
P1(2:end-1) = 2*P1(2:end-1);

% Frequency domain vector
f = Fs*(0:(L/2))/L;

% Store results in the workspace for retrieval
assignin('base', 'time_domain', struct('time', t, 'signal', signal));
assignin('base', 'magnitude_spectrum', struct('frequencies', f, 'magnitudes', P1));
assignin('base', 'phase_spectrum', struct('frequencies', f, 'phases', angle(Y(1:L/2+1))));
