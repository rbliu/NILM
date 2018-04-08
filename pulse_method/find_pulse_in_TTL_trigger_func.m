function [pulse] = find_pulse_in_TTL_trigger_func(ch_Neu, ch_Neu_id,scope,pulse_setting, options)
% function [pulse] = find_pulse_in_TTL_trigger_func(ch_Neu, timeIntNs, numPre_trig, numPost_trig)
% v1.0 - DQH 20160414 SURF
% v1.1 - DQH 20160422
%      - added the plot options
%      - added the trigger hold off time (same as event length)
%      - DQH 20160224 - fix the dimention mis-match bug - line 98-101
% This function is used to manually find neutorn(/BG) pulses in long waveforms
% that are triggered by the DD neutron TTL pulse (up to a few 100 us).
% input:
% ch_Neu (chA or chB): peak high data (only in unit of mA for now)
% ch_Neu_id: which channel - A / B / C / D
% setting at taking data
%   - scope.dt_ns
%   - scope.preTrig_bins
%   - scope.postTrig_bins
%   - scope.VoffsetV (for neutron channel)
% setting for output pusle
%   - pulse_setting.virt_trig: = -15
%   - pulse_setting.numPre_trig: = 14
%   - pulse_setting.numPost_trig: = 40
% options.plot
%   - 1 --> plot
%   - 0 --> no plot (defalut)
%
% output:
%   - pulse.pulse_mV
%   - pulse.TTL_ind
%   - pulse.time_wrt_TTL_trgi (unit us)

if nargin < 5
    options.plot = 0;
end

if nargin < 4
    error('input missing; need four function input variable');
end

switch ch_Neu_id
    case 'A'
        VoffsetV = scope.Voffset_V(1);
        disp('Neutron pulse is collected in Ch A, please make sure it is correct');
    case 'B'
        VoffsetV = scope.Voffset_V(2);
        disp('Neutron pulse is collected in Ch B, please make sure it is correct');
        
    case 'C'
        VoffsetV = scope.Voffset_V(3);
        disp('Neutron pulse is collected in Ch C, please make sure it is correct');
        
    case 'D'
        VoffsetV = scope.Voffset_V(4);
        disp('Neutron pulse is collected in Ch D, please make sure it is correct');
        
    otherwise
        error('please specify correct channel ID');
end

if options.plot
    disp('type in the number index array for events to be plotted (default [1:20]): ')
    plot_evt_id = input('(Example: 1:20) : ');
    if isempty(plot_evt_id)
        plot_evt_id = 1:20;
    elseif isnumeric(plot_evt_id) == 0 || any(mod(plot_evt_id,1))~=0
        error('Please type in a numerical integer array')
        % return(0);
    end
    % disp('*** Plot first 20 events ***');
    disp('*** Turn of ploting when processing data ***')
else
    n_ttl = size(ch_Neu,2);
    plot_evt_id = 1:n_ttl;
end
pulse_id = 0;
evt_length = pulse_setting.numPre_trig + pulse_setting.numPost_trig + 1; % add 1 to add the trigger point
for ii = plot_evt_id
    wf = ch_Neu(:,ii);
    if options.plot % plot
        x_index = 1:length(wf);
        nextcol({'m','r','g','c','k','y'});
        figure;
        plot(x_index, wf,'-b');
        set(gca,'fontsize',18);
        xlabel('sample [4ns]');
        ylabel('pulse at PMT o/p [mV]');
        title(['event: ' num2str(ii)])
        grid on;
        hold on;
    end
    npcut = wf < (pulse_setting.virt_trig + VoffsetV.*1000);
    npcutdiff = diff(npcut);
    start_idx = find(npcutdiff == 1);
    %     stop_idx = find (npcutdiff == -1);
    %     if length(start_idx) ~= length(stop_idx)
    %         stop_idx(end+1) = length(npcutdiff);
    %     end
    if isempty(start_idx)
        continue;
    else
        for kk = 1:length(start_idx)
            if kk == 1
                start_idx1 = start_idx(kk);
            else
                if (start_idx(kk) - start_idx1) < evt_length
                    continue;
                else
                    start_idx1 = start_idx(kk);
                end
            end
            start_idx1 = start_idx1 + 1; % diff removes the first element
            
            pulse_index = (start_idx1-pulse_setting.numPre_trig):(start_idx1+pulse_setting.numPost_trig);
            % pulse_index = pulse_index(inrange(pulse_index,[1,length(wf)]));
            if max(pulse_index) > length(wf)
                continue;
            end
            pulse_id  = pulse_id + 1;
            pulse.pulse_mV(:,pulse_id) = wf(pulse_index);
            if options.plot % plot
                pulse_x = x_index(pulse_index);
                plot(pulse_x,pulse.pulse_mV(:,pulse_id),[nextcol '-']);
                pause(0.5);
            end
            pulse.TTL_ind(pulse_id) = ii;
            pulse.time_wrt_TTL_trgi(pulse_id) = (start_idx1 - scope.preTrig_bins).*scope.dt_ns./10^3; %(us unit)
        end
    end
end
end