clear all;

%read results file
data = csvread('~/Documents/work/ARC/tesla_valve/tesla_valve_mod_csv.csv',1,0);

%plot driving temp and UR temp, and resulting flow
figure('DefaultAxesFontSize',14);
yyaxis left;
plot(data(:,1), data(:,4)-273, data(:,1), data(:,end-2)-273);
xlabel('time (s)'); ylabel('temperature (C)'); grid on;
yyaxis right;
plot(data(:,1), data(:,7));
ylabel('mass flow (kg/s)');
legend('driving temperature', 'upper reservoir', 'mass flow');

%plot pressures
figure('DefaultAxesFontSize',14);
plot(data(:,1), data(:,2), data(:,1), data(:,3), data(:,1), data(:,8));
xlabel('time'); ylabel('pressure (Pa)'); grid on;
legend('upper reservoir', 'gas reservoir', 'inner arc tube');

%plot liquid levels
figure('DefaultAxesFontSize',14);
plot(data(:,1), data(:,end-5), data(:,1), data(:,end-11));
xlabel('time (s)'); ylabel('liquid level (m)'); grid on;
legend('upper reservoir', 'outer arc tube');

% %plot inner arc tube temperature
% figure;
% [X,Y] = meshgrid(data(:,1), [0:0.75/120:0.75 0.75:1.75/30:2.5 2.5:0.5/30:3]);
% surf(X,Y,data(:,9+183:9+183+182)'-273, 'EdgeColor', 'none'); %zlim([500 520]);
% xlabel('time (s)'); ylabel('inner arc tube position (m)'); zlabel('temperature (C)');
% 
% %plot inner arc tube pressure
% figure;
% [X,Y] = meshgrid(data(2:end,1), [0:0.75/120:0.75 0.75:1.75/30:2.5 2.5:0.5/30:3]);
% surf(X,Y,data(2:end,9:9+182)'-273, 'EdgeColor', 'none');
% xlabel('time (s)'); ylabel('inner arc tube position (m)'); zlabel('pressure (Pa)');