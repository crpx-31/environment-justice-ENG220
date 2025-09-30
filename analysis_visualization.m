%% ANALYSIS AND VISUALIZATION OF CALENVIROSCREEN DATA
% This script loads the clean data created by the preprocessing script.
% It then performs analysis to identify key trends and creates plots
% to visually represent the findings.

% --- 1. Load the Clean Data ---
% We load the 'cleanData' table from the .mat file. This is much faster
% than re-reading the CSV.
disp('Loading clean_data.mat...');
load('clean_data.mat');

% --- 2. Perform Core Analysis ---

% Task A: Identify the most impacted communities
% We sort the table by the 'CES4_0Percentile' column in descending
% order to find the communities with the highest scores.
disp('Finding the top 10 most impacted communities...');
topCommunities = sortrows(cleanData, 'CES4_0Percentile', 'descend');

% Display the top 10 rows of this sorted table in the Command Window.
disp('--- Top 10 Most Impacted Communities ---');
head(topCommunities, 10);

% Task B: Calculate a key statistic
% We'll find the correlation between poverty and PM2.5 pollution to see
% if there is a statistical link between them.
disp('Calculating correlation between Poverty and PM2.5...');
% 'corrcoef' returns a matrix; the value at (1,2) is the correlation coefficient.
correlationMatrix = corrcoef(cleanData.Poverty, cleanData.PM2_5);
povertyPollutionCorr = correlationMatrix(1, 2);
fprintf('The correlation coefficient between Poverty and PM2.5 is: %0.4f\n', povertyPollutionCorr);


% --- 3. Create Visualizations ---
% Each 'figure' command creates a new pop-up window for a plot.

disp('Generating visualizations...');

% Visualization #1: Histogram of Overall Scores
% This plot shows the distribution of the main environmental justice scores.
figure;
histogram(cleanData.CES4_0Score);
title('Distribution of Environmental Justice Scores in California');
xlabel('CalEnroScreen 4.0 Score');
ylabel('Number of Communities');
grid on;

% Visualization #2: Scatter Plot to Show Correlation
% This plot visually represents the relationship we calculated above.
figure;
scatter(cleanData.Poverty, cleanData.PM2_5, 15, 'filled', 'MarkerFaceAlpha', 0.4);
title('Poverty vs. PM2.5 Air Pollution in California');
xlabel('Poverty Rate (%) in Community');
ylabel('PM2.5 Concentration');
grid on;

% Visualization #3: Geographic Map of Hotspots
% This geoscatter plot maps every community by its latitude and longitude,
% with the color representing its environmental justice score.
figure;
geoscatter(cleanData.Latitude, cleanData.Longitude, 20, cleanData.CES4_0Score, 'filled');
geobasemap streets-light; % Adds a light-colored map background
title('Environmental Justice Score Hotspots Across California');
colorbar; % Adds the color legend to interpret the scores
caxis([0 100]); % Sets the color axis limits for better contrast

disp('---');
disp('Analysis and visualization complete! Check the pop-up plot windows.');
