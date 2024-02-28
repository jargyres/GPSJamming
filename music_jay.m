doa_signals = [20 ]*pi/180;               %DOA�s of incoming signals in radians.
power = [1];                                 %Power level of incoming signals
number_elements = 4;                                             %Number of array elements
number_snapshots = 400;                                          %Number of snapshots received
separation_distance = 0.5;                                           %Distance between elements in wavelengths
noise_variance = 0.4;                                     %Noise Variance
number_signals = length(doa_signals);                           %Total number of signals

% Compute steering vectors
steering_vectors = exp(-1i*2*pi*separation_distance*(0:number_elements-1)'*sin([doa_signals(:).']));

% Generating random signal
random_signal = round(rand(number_signals,number_snapshots))*2-1; % BPSK symbols of incoming signals
noise = sqrt(noise_variance/2)*(randn(number_elements,number_snapshots)+1i*randn(number_elements,number_snapshots)); % Random uncorrelated noise
% s = anechoic13';  % Put correct file name here, skip line if you want to use signal defined above. If reading file, make sure it is in matrix format.  
s = MonJan29FourthTest1SourceOnlyRightStraightOnOrientation';
% s = s./sqrt(nansum(abs(s .^2)) / 1024); %Normalizing
s = s./sqrt(sum(abs(s .^2), 'omitnan') / 1024); %Normalizing

received_signals = s'%steering_vectors*diag(sqrt(power))*random_signal+noise; 

%received_signals = steering_vectors*diag(sqrt(power))*random_signal+noise; %Generate data matrix

% Eigen Analysis
covariance_matrix = received_signals*received_signals'/number_snapshots; %Spatial covariance matrix
[eigenvectors ,eigenvalues] = eig(covariance_matrix); %Eigendecomposition of covariance matrix
[eigenvalues,I] = sort(diag(eigenvalues),1,'descend'); % Sortingl eigenvalues largest to smallest
eigenvectors = eigenvectors (:,I); %Sorting eigenvectors
signal_eigenvectors = eigenvectors (:,1:number_signals); % Signal eigenvectors
noise_eigenvectors = eigenvectors(:,number_signals+1:number_elements); %Noise eigenvectors

%Computing MUSIC
angles = (-90:0.1:90); % MUSIC spectrum to be computed
complete_spectrum_response = exp(-1i*2*pi*separation_distance*(0:number_elements-1)'*sin([angles(:).']*pi/180));

for i=1:length(angles)
music_spectrum(i) = (complete_spectrum_response(:,i)'*complete_spectrum_response(:,i))/(complete_spectrum_response(:,i)'*noise_eigenvectors*noise_eigenvectors'*complete_spectrum_response(:,i));
end

figure(1) %%MuSiC spectrum
plot(angles,abs(music_spectrum))
title('MUSIC Spectrum')
xlabel('Angle (degrees)')
