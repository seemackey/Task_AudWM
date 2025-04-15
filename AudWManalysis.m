function AudWManalysis(path)
%% analyze aud WM data in-cage

% import from excel
opts = delimitedTextImportOptions("NumVariables", 11);

% Specify range and delimiter
opts.DataLines = [2, Inf];
opts.Delimiter = ",";

% Specify column names and types
opts.VariableNames = ["TrialNumber", "Participant", "Response", "ResponsePeriodOnset", "RT", "Seed", "CueFrequency", "CueFrequencyRange", "ChoiceFrequency", "ChoiceFrequencyRange", "Coherence"];
opts.VariableTypes = ["double", "categorical", "categorical", "double", "double", "double", "double", "double", "double", "double", "double"];

% Specify file level properties
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";

% Specify variable properties
opts = setvaropts(opts, ["Participant", "Response"], "EmptyFieldRule", "auto");

% Import the data
tbl = readtable(path, opts);

%% Convert to output type
TrialNumber = tbl.TrialNumber;
Participant = tbl.Participant;
Response = tbl.Response;
ResponsePeriodOnset = tbl.ResponsePeriodOnset;
RT = tbl.RT;
Seed = tbl.Seed;
CueFrequency = tbl.CueFrequency;
CueFrequencyRange = tbl.CueFrequencyRange;
ChoiceFrequency = tbl.ChoiceFrequency;
ChoiceFrequencyRange = tbl.ChoiceFrequencyRange;
Coherence = tbl.Coherence;

if length(TrialNumber)>10
%% corr and incorr criteria
% Criteria for Correct and Incorrect Responses
Corr = NaN(size(Response));  % Initialize Corr with NaNs for missing data handling

for i = 1:length(Response)
    if ChoiceFrequency(i) ~= CueFrequency(i)
        if Response(i) == 'diff'
            Corr(i,1) = 1;  % Correct
        elseif Response(i) == 'same'
            Corr(i,1) = 0;  % Incorrect
        else
            Corr(i,1) = NaN;  % Handle unexpected responses
        end
    elseif ChoiceFrequency(i) == CueFrequency(i)
        if Response(i) == 'same'
            Corr(i,1) = 1;  % Correct
        elseif Response(i) == 'diff'
            Corr(i,1) = 0;  % Incorrect
        else
            Corr(i,1) = NaN;  % Handle unexpected responses
        end
    else
        Corr(i,1) = NaN;  % This should never occur if data is clean
    end
end

%% Identify unique frequency combinations
% Get unique frequency combinations of CueFrequency and ChoiceFrequency
[uniqueComb, ~, groupIndices] = unique([CueFrequency, ChoiceFrequency], 'rows');

% Number of unique combinations
numCombinations = size(uniqueComb, 1);

%% Plot performance over time with subplots

figure;
% Define the window sizes for moving sum calculation
windowSizes = [10, 20, 50]; % example window sizes

% Loop through each unique frequency combination
for combIdx = 1:numCombinations
    % Get indices for this specific combination of Cue and Choice Frequency
    currCombIndices = groupIndices == combIdx;
    
    % Extract data for this combination
    currCorr = Corr(currCombIndices);  % Extract correct/incorrect data
    disp('% Correct In this condition')
    sum(currCorr,'omitnan')/length(currCorr)*100
    % Create a subplot for this combination
    subplot(numCombinations, 1, combIdx);
    hold on;
    colors = ['r', 'g', 'b']; % colors for each plot
    
    % Loop through each window size and calculate moving sum and proportion
    for idx = 1:length(windowSizes)
        movSum = movsum(currCorr == 1, windowSizes(idx), 'omitnan');
        movProp = movSum / windowSizes(idx);  % Calculate the proportion
        plot(movProp, 'Color', colors(idx), 'LineWidth', 2);
    end
    
    % Set plot title and labels
    title(['Performance Over Time for Cue=', num2str(uniqueComb(combIdx, 1)), ...
           ' and Choice=', num2str(uniqueComb(combIdx, 2))]);
    xlabel('Trial');
    ylabel('Proportion Correct');
    
    % Add legend for different window sizes
    %legend(strcat('Window Size=', string(windowSizes)));
    %legend('show', 'Location', 'northeastoutside');
    hold off;
end

% Adjust figure layout
sgtitle('Performance Over Time by Frequency');

    %% Save the figure as .fig and .jpg
    % Generate a base filename from the path
    [~, baseFileName, ~] = fileparts(path);

    % Save the figure as a MATLAB .fig file
    savefig(gcf, [char(baseFileName) '.fig']);

    % Save the figure as a .jpg image
    saveas(gcf, [char(baseFileName) '.jpg']);
    

else
    disp('OH NO! < 10 trials, prob no data')
end
