% ------------------------------------------------------------------------------- 
% --
% -- JEOL Ltd.
% -- 1-2 Musashino 3-Chome
% -- Akishima Tokyo 196-8558 Japan 
% -- Copyright 2023 
% -- 
% Licensed under the Apache License, Version 2.0 (the "License");
% you may not use this file except in compliance with the License.
% You may obtain a copy of the License at
% 
%      http://www.apache.org/licenses/LICENSE-2.0
% 
%  Unless required by applicable law or agreed to in writing, software
% distributed under the License is distributed on an "AS IS" BASIS,
% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
% See the License for the specific language governing permissions and
% limitations under the License.
%  --++--------------------------------------------------------------------------- 
% -- 
% -- ModuleName : invertspec.m
% -- ModuleType : Example external command script for JASON 
% -- Purpose : External data processing in JASON 
% -- Date : February 2023 
% -- Author : Iain J. Day
% -- Language : MATLAB
% -- 
% --##---------------------------------------------------------------------------

function invertspec(filename)
% INVERTSPEC    Invert a JASON spectrum point-by-point
%   INVERTSPEC(filename) inverts a spectrum in the JASON .jjh5 
%       file given by filename
%
%   Can be called from the JASON external command processing item as:
%     Cmd:       matlab
%     Arguments: -nojvm -batch "invertspec('$TMPFILE')"
% 
%   (Double quotes should be omited on macOS)

dataset = '/JasonDocument/DataPoints/';

disp(['Opening dataset: ', filename])
dsetre = h5read(filename, strcat(dataset, '/0'));
dsetim = h5read(filename, strcat(dataset, '/1'));

disp(['dataset size: ', num2str(length(dsetre))])

h5write(filename, strcat(dataset, '/0'), -dsetre);
h5write(filename, strcat(dataset, '/1'), -dsetim);
disp('dataset changed')

end
