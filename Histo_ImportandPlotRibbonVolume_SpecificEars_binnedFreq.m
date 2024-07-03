% cochlear histology analysis
% this script analyzes synaptic ribbon volume data from an idiosyncratic
% spreadsheet
% chase m 2024
% optionally, you can directly import RibbonVolume.mat and skip the
% spreadsheet

%% Import the data from an excel sheet. 
clear;

% Load the Excel file
filename = 'C:\Users\cmackey\Documents\CochlearHistology\IHCRibbonVolData.xlsx';  % Update with your file path
[~, sheets] = xlsfinfo(filename);

% Initialize storage for data
data = struct();

% Read data from each sheet and organize it
for i = 1:length(sheets)
    sheet = sheets{i};
    % Ensure sheet name is treated as a string
    sheetNameStr = string(sheet);

    % Debugging: display the current sheet name
    disp(['Processing sheet: ' sheetNameStr]);

    % Read the first row to get headers
    headers = readcell(filename, 'Sheet', sheet, 'Range', '1:1');

    % Read the rest of the data
    sheetData = readtable(filename, 'Sheet', sheet, 'Range', '2:10000'); % Adjust range as needed
    
    % Extract frequency place and ribbon volumes
    freqPlace = headers;
    ribbonVolumes = table2array(sheetData);

    % Append different voxels within the same case
    uniqueFreqs = unique(string(freqPlace));
    caseData = struct();
    for j = 1:length(uniqueFreqs)
        freq = uniqueFreqs{j};
        % Use strcmp to find matching frequency place headers
        voxelData = ribbonVolumes(:, strcmp(freqPlace, freq));
        validFreqName = matlab.lang.makeValidName(freq);
        
        % Initialize a cell array to handle variable-length data
        voxelDataClean = cell(1, size(voxelData, 2));
        
        % Clean the voxel data by removing NaNs
        for appendcount = 1:size(voxelData, 2)
            cleanedData = voxelData(~isnan(voxelData(:, appendcount)), appendcount);
            voxelDataClean{appendcount} = cleanedData;
        end
        
        % Append cleaned voxel data for this frequency place
        for appendcount = 1:length(voxelDataClean)
            if isfield(caseData, validFreqName)
                caseData.(validFreqName) = [caseData.(validFreqName); voxelDataClean{appendcount}];
            else
                caseData.(validFreqName) = voxelDataClean{appendcount};
            end
        end
    end

    % Create a valid field name for the sheet
    validSheetName = matlab.lang.makeValidName(sheetNameStr);

    % Store the data in the structure
    data.(validSheetName) = caseData;
end

%% Group the data
% Define the groups
M_long = [108, 109, 110, 114, 124, 125];
F_long = [119, 120, 122, 123];
M_short = [26, 28, 117, 118, 121];
control = [103, 104, 111, 112, 113];

% Define the new specific ears group
specific_ears = {'x108R', 'x110L', 'x114R', 'x125L', 'x125R', 'x119R', 'x120R'};

groupNames = {'M_long', 'F_long', 'M_short', 'control', 'specific_ears'};
groups = {M_long, F_long, M_short, control, specific_ears}; % Ensure groups are defined

groupedData = struct();

% Group the original groups
for k = 1:length(groupNames) - 1 % Skip the new specific ears group for now
    group = groupNames{k};
    groupCases = groups{k}; % Get the case IDs for the current group
    groupedData.(group) = struct();

    for caseID = groupCases
        caseIDStr = ['x' num2str(caseID)];
        groupedData.(group).(caseIDStr) = struct();
        
        % Check both L and R versions of the case
        for suffix = ["L", "R"]
            caseName = ['x' num2str(caseID) suffix];
            caseName = join(caseName);
            validCaseName = matlab.lang.makeValidName(caseName);
            if isfield(data, validCaseName)
                groupedData.(group).(caseIDStr).(suffix) = data.(validCaseName);
            end
        end
    end
end

% Group the new specific ears group
groupedData.specific_ears = struct();
for i = 1:length(specific_ears)
    ear = specific_ears{i};
    validEarName = matlab.lang.makeValidName(ear);
    if isfield(data, validEarName)
        groupedData.specific_ears.(validEarName) = data.(validEarName);
    end
end

% Data are now grouped.

%% Analyze the grouped data by frequency bins

% Frequency bins
freqBins = {'low', 'mid', 'high'};
binRanges = [0, 2; 2, 8; 8, Inf];

% Initialize a struct to store mean volumes
meanVolumes = struct();
binData = struct();

% Loop through each group
for k = 1:length(groupNames)
    group = groupNames{k};
    groupCases = groups{k}; % Get the case IDs for the current group
    binData.(group) = struct();
    
    % Initialize bins
    for bin = freqBins
        binData.(group).(bin{1}) = [];
    end

    % Collect data from each case in the group
    if strcmp(group, 'specific_ears')
        for ear = specific_ears
            earName = ear{1};
            validEarName = matlab.lang.makeValidName(earName);
            if isfield(groupedData.specific_ears, validEarName)
                caseData = groupedData.specific_ears.(validEarName);
                
                % Collect volume data for each frequency place
                freqNames = fieldnames(caseData);
                for j = 1:length(freqNames)
                    freq = freqNames{j};
                    freqValue = str2double(strrep(freq(2:end), '_', '.'));

                    for b = 1:length(freqBins)
                        if freqValue > binRanges(b, 1) && freqValue <= binRanges(b, 2)
                            binData.(group).(freqBins{b}) = [binData.(group).(freqBins{b}); caseData.(freq)];
                        end
                    end
                end
            end
        end
    else
        for caseID = groupCases
            caseIDStr = ['x' num2str(caseID)];
            
            % Check both L and R versions of the case
            for suffix = ["L", "R"]
                if isfield(groupedData.(group), caseIDStr) && isfield(groupedData.(group).(caseIDStr), suffix)
                    caseData = groupedData.(group).(caseIDStr).(suffix);

                    % Collect volume data for each frequency place
                    freqNames = fieldnames(caseData);
                    for j = 1:length(freqNames)
                        freq = freqNames{j};
                        freqValue = str2double(strrep(freq(2:end), '_', '.'));

                        for b = 1:length(freqBins)
                            if freqValue > binRanges(b, 1) && freqValue <= binRanges(b, 2)
                                binData.(group).(freqBins{b}) = [binData.(group).(freqBins{b}); caseData.(freq)];
                            end
                        end
                    end
                end
            end
        end
    end

    %  Metrics for each frequency bin
    for b = 1:length(freqBins)
        bin = freqBins{b};
        tmpdata = binData.(group).(bin);
        meanVolumes.(group).(bin) = mean(tmpdata, 'omitnan');
        VolumesSD.(group).(bin) = std(tmpdata, 'omitnan');
        VolumeIQR.(group).(bin) = iqr(tmpdata);
        VolumeSkew.(group).(bin) = skewness(tmpdata);
        VolumeRange.(group).(bin) = range(tmpdata);
        VolumeTailVar.(group).(bin) = var(tmpdata(floor(0.9*length(tmpdata)):end));
    end
end

%% PLOTTING
% Plot the mean volumes
figure;
subplot(1,4,1)
hold on;
colors = lines(length(groupNames));

for k = 1:length(groupNames)
    group = groupNames{k};
    binNames = freqBins;
    
    % Convert bin names to numeric values
    bins = 1:length(binNames);
    volumes = cellfun(@(x) meanVolumes.(group).(x), binNames);
    sds = cellfun(@(x) VolumesSD.(group).(x), binNames);
    
    % Sort by bin
    [bins, sortIdx] = sort(bins);
    volumes = volumes(sortIdx);
    
    plot(bins, volumes, '-o', 'Color', colors(k, :), 'DisplayName', group);
    % errorbar(bins, volumes, sds)
end

xlabel('Frequency Bin');
xticks(1:3);
xticklabels({'Low', 'Mid', 'High'});
ylabel('Mean Ribbon Volume');
legend('Location', 'best');
title('Mean Ribbon Volume by Frequency Bin');

% Plot the IQR of volumes
subplot(1,4,2)
hold on;
for k = 1:length(groupNames)
    group = groupNames{k};
    binNames = freqBins;
    
    % Convert bin names to numeric values
    bins = 1:length(binNames);
    volumes = cellfun(@(x) VolumeIQR.(group).(x), binNames);

    % Sort by bin
    [bins, sortIdx] = sort(bins);
    volumes = volumes(sortIdx);
    
    plot(bins, volumes, '-o', 'Color', colors(k, :), 'DisplayName', group);
end

xlabel('Frequency Bin');
xticks(1:3);
xticklabels({'Low', 'Mid', 'High'});
ylabel('Ribbon Volume IQR');
legend('Location', 'best');
title('Interquartile Range by Frequency Bin');

% Plot the skewness of volumes
subplot(1,4,3)
hold on;
for k = 1:length(groupNames)
    group = groupNames{k};
    binNames = freqBins;
    
    % Convert bin names to numeric values
    bins = 1:length(binNames);
    volumes = cellfun(@(x) VolumeSkew.(group).(x), binNames);

    % Sort by bin
    [bins, sortIdx] = sort(bins);
    volumes = volumes(sortIdx);
    
    plot(bins, volumes, '-o', 'Color', colors(k, :), 'DisplayName', group);
end

xlabel('Frequency Bin');
xticks(1:3);
xticklabels({'Low', 'Mid', 'High'});
ylabel('Skewness');
legend('Location', 'best');
title('Ribbon Volume Skewness by Frequency Bin');

% Plot the range of volumes
subplot(1,4,4)
hold on;
for k = 1:length(groupNames)
    group = groupNames{k};
    binNames = freqBins;
    
    % Convert bin names to numeric values
    bins = 1:length(binNames);
    volumes = cellfun(@(x) VolumeRange.(group).(x), binNames);

    % Sort by bin
    [bins, sortIdx] = sort(bins);
    volumes = volumes(sortIdx);
    
    plot(bins, volumes, '-o', 'Color', colors(k, :), 'DisplayName', group);
end

xlabel('Frequency Bin');
xticks(1:3);
xticklabels({'Low', 'Mid', 'High'});
ylabel('Range');
legend('Location', 'best');
title('Range by Frequency Bin');
print('RibbonVolSummaryBins', '-djpeg', '-r300'); % Save as JPEG with 300 dpi resolution

