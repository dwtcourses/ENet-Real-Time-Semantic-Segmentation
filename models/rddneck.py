###################################################
# Copyright (c) 2019                              #
# Authors: @iArunava <iarunavaofficial@gmail.com> #
#          @AvivSham <mista2311@gmail.com>        #
#                                                 #
# License: BSD License 3.0                        #
#                                                 #
# The Code in this file is distributed for free   #
# usage and modification with proper linkage back #
# to this repository.                             #
###################################################

class RDDNeck(nn.Module):
    def __init__(self, h, w, dilate, in_channels, out_channels, down_flag, p=0.1):
        
        super().__init__()
        
        # Define class variables
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.h = h
        self.w = w
        self.dilate = dilate
        self.down_flag = down_flag

        if down_flag:
            self.stride = 2
        else:
            self.stride = 1
          
        
        self.maxpool = nn.MaxPool2d(kernel_size = 2,
                                      stride = 2,
                                      padding = 0, return_indices=True)
        

        
        self.dropout = nn.Dropout2d(p=p)
        
        self.conv1 = nn.Conv2d(in_channels = self.in_channels,
                               out_channels = self.out_channels,
                               kernel_size = 1,
                               stride = 1,
                               padding = 0,
                               bias = False,
                               dilation = 1)
        
        self.prelu1 = nn.PReLU()
        
        self.conv2 = nn.Conv2d(in_channels = self.out_channels,
                                  out_channels = self.out_channels,
                                  kernel_size = 3,
                                  stride = self.stride,
                                  padding = self.dilate,
                                  bias = True,
                                  dilation = self.dilate)
        
        self.prelu2 = nn.PReLU()
        
        self.conv3 = nn.Conv2d(in_channels = self.out_channels,
                                  out_channels = self.out_channels,
                                  kernel_size = 1,
                                  stride = 1,
                                  padding = 0,
                                  bias = False,
                                  dilation = 1)
        
        self.prelu3 = nn.PReLU()
        
        self.batchnorm = nn.BatchNorm2d(self.out_channels)
        
    def forward(self, x):
        
        bs = x.size()[0]
        x_copy = x.clone()
        
        # Side Branch
        x = self.conv1(x)
        x = self.batchnorm(x)
        x = self.prelu1(x)
        
        x = self.conv2(x)
        x = self.batchnorm(x)
        x = self.prelu2(x)
        
        x = self.conv3(x)
        x = self.batchnorm(x)
                
        x = self.dropout(x)
        
        # Main Branch
        
        if self.down_flag:
            x_copy, indices = self.maxpool(x_copy)
          
        if self.in_channels != self.out_channels:
            out_shape = self.out_channels - self.in_channels
            extras = torch.zeros((bs, out_shape, x.shape[2], x.shape[3]))
            if torch.cuda.is_available:
                extras = extras.cuda()
            x_copy = torch.cat((x_copy, extras), dim = 1)
        
        # Sum of main and side branches
        x = x + x_copy
        x = self.prelu3(x)
        
        if self.down_flag:
            return x, indices
        else:
            return x