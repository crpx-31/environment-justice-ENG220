%% DATA PREPROCESSING FOR CALENVIROSCREEN 4.0
% This script loads the raw CalEnviroScreen CSV data, cleans it by
% selecting only the necessary columns and removing missing values, and
% then saves the clean data as a MATLAB file (.mat) for future use.

% --- 1. Load the Raw Data ---
% 'readtable' imports the specified CSV file into a table variable.
disp('Loading raw data from calenviroscreen40resultsdatadictionary_F_2021.xlsx...');
rawData = readtable('calenviroscreen40resultsdatadictionary_F_2021.xlsx');

% --- 2. Inspect the Actual Column Names ---
% This step is crucial for debugging. It prints the exact variable names
% MATLAB created from the CSV headers, which might be different from
% what's in the file (e.g., "CES 4.0 Score" becomes "CES4_0Score").
disp('Displaying the actual variable names in the table:');
disp(rawData.Properties.VariableNames);

% --- 3. Select Relevant Columns for the Project ---
% We create a new, smaller table containing only the columns we need.
% This makes our analysis faster and our code easier to read.
% Note: The names in this list must EXACTLY match the output from step 2.
disp('Selecting relevant columns for analysis...');
columnsToKeep = {
    'CensusTract', 'CaliforniaCounty', 'TotalPopulation', ...
    'CES4_0Score', 'CES4_0Percentile', 'PM2_5', ...
    'Poverty', 'Asthma', 'Latitude', 'Longitude'
};
cleanData = rawData(:, columnsToKeep);

% --- 4. Handle Missing Values ---
% The 'rmmissing' function removes any row that contains a missing value
% (NaN) in any of the selected columns, ensuring our calculations are accurate.
disp('Removing rows with missing data...');
cleanData = rmmissing(cleanData);

% --- 5. Save the Clean Data ---
% We save our final 'cleanData' table to a .mat file. This is a highly
% efficient MATLAB format that is much faster to load in the future than

% reprocessing the CSV every time.
disp('Saving clean data to clean_data.mat...');
save('clean_data.mat', 'cleanData');

disp('---');
disp('Data preprocessing complete! The clean_data.mat file has been created.');