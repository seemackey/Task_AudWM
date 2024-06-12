%% analyze aud WM data in-cage


%% corr and incorr criteria
Corr = zeros(size(Response));

for i = 1:length(Response)
    if ChoiceFrequency(i)~=CueFrequency(i) && Response(i) ~= 'same'
        Corr(i,1) = 0;
    elseif ChoiceFrequency(i)~=CueFrequency(i) && Response(i) ~= 'diff'
        Corr(i,1) = 1;
    elseif ChoiceFrequency(i)==CueFrequency(i) && Response(i) ~= 'same'
        Corr(i,1) = 1;
    elseif ChoiceFrequency(i)==CueFrequency(i) && Response(i) ~= 'diff'
        Corr(i,1) = 0;
    else
        Corr(i,1) = NaN;
    end
end

%% plot it


% Define the window sizes for moving sum calculation
windowSizes = [10, 20, 50]; % example window sizes

% Calculate and plot moving proportions
figure;
hold on;
colors = ['r', 'g', 'b']; % colors for each plot
for idx = 1:length(windowSizes)
    movSum = movsum(Corr == 1, windowSizes(idx), 'omitnan');
    movProp = movSum / windowSizes(idx);  % Calculate the proportion
    plot(movProp, 'Color', colors(idx), 'LineWidth', 2);
end

legend(strcat('Window Size=', string(windowSizes)));
title('Running Proportion of Correct Trials Over Trials');
xlabel('Trial');
ylabel('Proportion of Correct Trials');
hold off;

