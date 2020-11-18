import torch
import torch.nn as nn
import torch.nn.functional as nnf
import drms
import sklearn
import joblib
import pandas as pd
from datetime import datetime
import torchvision.transforms as transforms
from PIL import Image


# load model
class MLPModule(nn.Module):
    def __init__(
            self,
            input_units=20,
            output_units=2,
            hidden_units=10,
            num_hidden=1,
            nonlin=nn.ReLU(),
            output_nonlin=None,
            dropout=0,
            squeeze_output=False,
    ):
        super().__init__()
        self.input_units = input_units
        self.output_units = output_units
        self.hidden_units = hidden_units
        self.num_hidden = num_hidden
        self.nonlin = nonlin
        self.output_nonlin = output_nonlin
        self.dropout = dropout
        self.squeeze_output = squeeze_output

        self.reset_params()

    def init_weights(m):
        if type(m) == nn.Linear:
            torch.nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
            print(m.weight)
            # m.bias.data.fill_(0.01)

    def reset_params(self):
        """(Re)set all parameters."""
        units = [self.input_units]
        units += [self.hidden_units] * self.num_hidden
        units += [self.output_units]

        sequence = []
        for u0, u1 in zip(units, units[1:]):
            sequence.append(nn.Linear(u0, u1, bias=False))
            sequence.append(nn.BatchNorm1d(num_features=u1))
            sequence.append(nn.ReLU())
            sequence.append(nn.Dropout(self.dropout))

        sequence = sequence[:-2]
        if self.output_nonlin:
            sequence.append(self.output_nonlin)

        def init_weights(m):
            if type(m) == nn.Linear:
                torch.nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')

        self.sequential = nn.Sequential(*sequence)
        # self.sequential.apply(init_weights)

    def forward(self, X):  # pylint: disable=arguments-differ
        X = self.sequential(X)
        if self.squeeze_output:
            X = X.squeeze(-1)
        return X


input_features = 18
hidden_units = 100
layers = 1
model = MLPModule(input_units=input_features,
                  hidden_units=hidden_units,
                  num_hidden=layers,
                  dropout=0)

PATH = 'app/model.pt'
model.load_state_dict(torch.load(PATH, map_location='cpu'))
model.eval()


# todo get data
def get_ar_data(HARP, T_REC):
    c = drms.Client()
    # T_REC = '$'
    series_sharp = 'hmi.sharp_cea_720s_nrt'
    ids = ['T_REC', 'NOAA_AR', 'HARPNUM', 'CRVAL1', 'CRVAL2', 'CRLN_OBS',
           'CRLT_OBS', 'LAT_FWT', 'LON_FWT']
    sharps = ['USFLUX', 'SAVNCPP', 'TOTPOT', 'ABSNJZH', 'SHRGT45', 'AREA_ACR',
              'R_VALUE', 'TOTUSJH', 'TOTUSJZ', 'MEANJZH', 'MEANJZD', 'MEANPOT',
              'MEANSHR', 'MEANALP', 'MEANGAM', 'MEANGBZ', 'MEANGBT',
              'MEANGBH']
    try:
        data_sharp = c.query('%s[%d][%s]' % (series_sharp,
                                             HARP,
                                             T_REC,
                                             ),
                             key=ids + sharps)
        input_data = data_sharp.loc[:, sharps]
        meta_data = data_sharp.loc[:, ids]
    except:
        meta_data = []
        input_data = []
    return meta_data, input_data


# todo data -> tensor
def transform_data(input_data):
    # scale data
    # input_data = [-0.6121212, - 0.3551788, - 0.62486351, - 0.29903545, - 0.92962498, - 0.86269526,
    #               -0.49581933, - 0.63202377, - 0.68790552,
    #               0.96618365, - 1.37190815, - 0.82522054, -1.04826298,
    #               0.92327351, - 0.97048022, - 0.18917943, - 0.25369102, - 0.86765544]
    scaler = joblib.load('app/scaler.pkl')
    input_data = scaler.transform(input_data)

    # to tensor
    input_tensor = torch.tensor(input_data).float()

    return input_tensor


# predict
def get_prediction(input_tensor):
    outputs = model(input_tensor)
    outputs = nnf.softmax(outputs, dim=1)
    return outputs[:, 1]
