clear all,clc
sag_data = load("sag_veri.mat")
sol_data = load("sol_veri.mat")
sag_data = sag_data.eeg_data/1000
sol_data = sol_data.eeg_data/1000
t = linspace(0,140,23040)
figure;
filtreli_sol = filtrele(sol_data(:,4))
plot(t,filtreli_sol)
figure;
filtreli_sag = filtrele(sag_data(:,4))
plot(t,filtreli_sag)