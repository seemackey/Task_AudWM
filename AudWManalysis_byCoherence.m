
function AudWManalysis_byCoherence(path)
%% analyze aud WM data in-cage

% import from excel
opts = delimitedTextImportOptions("NumVariables", 11);
opts.DataLines = [2, Inf];
opts.Delimiter = ",";
opts.VariableNames = ["TrialNumber", "Participant", "Response", "ResponsePeriodOnset", "RT", "Seed", "CueFrequency", "CueFrequencyRange", "ChoiceFrequency", "ChoiceFrequencyRange", "Coherence"];
opts.VariableTypes = ["double", "categorical", "categorical", "double", "double", "double", "double", "double", "double", "double", "double"];
opts.ExtraColumnsRule = "ignore";
opts.EmptyLineRule = "read";
opts = setvaropts(opts, ["Participant", "Response"], "EmptyFieldRule", "auto");

tbl = readtable(path, opts);

TrialNumber = tbl.TrialNumber;
Participant = tbl.Participant;
Response = tbl.Response;
CueFrequency = tbl.CueFrequency;
ChoiceFrequency = tbl.ChoiceFrequency;
Coherence = tbl.Coherence;

if length(TrialNumber)>10
Corr = NaN(size(Response));
for i = 1:length(Response)
    if ChoiceFrequency(i) ~= CueFrequency(i)
        if Response(i) == 'diff'
            Corr(i,1) = 1;
        elseif Response(i) == 'same'
            Corr(i,1) = 0;
        else
            Corr(i,1) = NaN;
        end
    elseif ChoiceFrequency(i) == CueFrequency(i)
        if Response(i) == 'same'
            Corr(i,1) = 1;
        elseif Response(i) == 'diff'
            Corr(i,1) = 0;
        else
            Corr(i,1) = NaN;
        end
    else
        Corr(i,1) = NaN;
    end
end

uniqueCoherence = unique(Coherence);

windowSizes = [10, 20, 50];
colors = ['r', 'g', 'b'];

for c = 1:length(uniqueCoherence)
    currCoh = uniqueCoherence(c);
    cohIdx = Coherence == currCoh;

    CF = CueFrequency(cohIdx);
    CHF = ChoiceFrequency(cohIdx);
    COR = Corr(cohIdx);

    [uniqueComb, ~, groupIndices] = unique([CF, CHF], 'rows');
    numCombinations = size(uniqueComb, 1);

    figure;
    for combIdx = 1:numCombinations
        currCombIndices = groupIndices == combIdx;
        currCorr = COR(currCombIndices);
        subplot(numCombinations, 1, combIdx);
        hold on;
        for idx = 1:length(windowSizes)
            movSum = movsum(currCorr == 1, windowSizes(idx), 'omitnan');
            movProp = movSum / windowSizes(idx);
            plot(movProp, 'Color', colors(idx), 'LineWidth', 2);
        end
        title(['Coherence=' num2str(currCoh) ', Cue=' num2str(uniqueComb(combIdx,1)) ', Choice=' num2str(uniqueComb(combIdx,2))]);
        xlabel('Trial');
        ylabel('P(Correct)');
        hold off;
    end
    sgtitle(['Performance Over Time (Coherence=' num2str(currCoh) ')']);

    [~, baseFileName, ~] = fileparts(path);
    savefig(gcf, [char(baseFileName) '_coh' num2str(currCoh) '.fig']);
    saveas(gcf, [char(baseFileName) '_coh' num2str(currCoh) '.jpg']);
end

else
    disp('OH NO! < 10 trials, prob no data')
end
