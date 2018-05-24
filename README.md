CODECbench
==========

## An open source video codec benchmarking tool ##
![he](docs/images/cabs_logo.png)

CODECbench is a video codec comparison tool. It allows you to analyze how one video codec performs against another, or with itself using different settings

You start by defining what stuff you want to analyze. For example, let's compare how x265 performs with its different presets 'medium' and 'placebo'. For this we will create a JSON configuration like the following:

```javascript
// we'll keep this on a file called x265bench.json
{
  "keeprecon" : false,
  "frame_count" : 300,
  "runs" : [
  {
        "seq" : ["foremancif"],
        "codec" : ["x265"],
        "bitrate_range" : [100,1000,50],
        "preset" : ["placebo","medium"]
  }
  ]
}
```

Notice the 'runs' section. It specifies to use the x265 codec and a range of bitrates from 100kbps to 1000kbps on 50kbps steps using the foremancif sequence. The range of presets of interest is defined.

Run this with codecbench:
```
codecbench -i x265bench.json
```

Here some magic happens. 

```
This is codecbench 0.4.9 [Alberto Vigata 2014] starting up on darwin-x86_64
added sequence cif/foreman.yuv [foremancif 352x288 420P 300F 25/1 fps]
loading x265bench.json
expanded bitrate list to: [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950]
expanded to 36 runs
running bitrate_100__codec_x265__preset_placebo__seq_foremancif__ 0/36
running bitrate_150__codec_x265__preset_placebo__seq_foremancif__ 1/36
running bitrate_200__codec_x265__preset_placebo__seq_foremancif__ 2/36
...
```

CODECbench figures out all possible combinations of this configuration and actually encodes the sequence in every one setting. Every settings is a 'run'. This can take a while, but a subdirectory 'runs' is created in where your config file is and the resulting bitstream and video metrics information is written there for later. 

You don't have to worry about configuring the codecs at all. CODECbench is modular, and the codecs are provided to you (there are some installed by default) as 'codec packs'. Codec packs have all its needed to interact with CODECbench and you can just invoke them on the configuration file with their nickname, in the example above 'x265'. You just need to drop the codec pack in the 'codecpacks' folder for this to work.

Sequences are similar. You can drop prepared yuv sequences on the sequences directory and use them with their nickname. All the details about formats, frame sizes and frame rates are handled automatically.

## Optimal Bitrate Resolution Switching ##
CODECbench can calculate what is the optimal bitrate at which to switch resolutions to keep subjective video quality constant.  In order to calculate the bitrate switching points an absolute metric like 'ssim' must be used. 
```javascript
{
    ...
    "reports" : {
        ...
        "reports": [
        {
            "ref" : 0.95,
            "metric" : "ssim",
            "minqual": [0.8, 0.9, 0.95] #minimum quality required. Scalar values are acceptable too
        }
    ]
}
```
Adding a `minqual` parameter to the ssim report will force the optimal bitrate resolution switching calculation. The parameter is either a scalar or a list of values. Each value corresponds to the minimum quality desired at any moment during the operation of the encoder. There's a sample report configuration provided on `/sampleruns/multires_x264_bench.json` The result report looks like this:
```
Example result:

Bitrate switch for 1920x1080@0.8 at 597542.7994113566 bps. 1280x720 qual at br is 0.8585469369729225
Bitrate switch for 1280x720@0.8 at 326301.5568897185 bps. 640x480 qual at br is 0.8677659265273029
Bitrate switch for 640x480@0.8 at 155525.33386919688 bps. 320x240 qual at br is 0.8413981228251971
Minimum bitrate for 320x240@0.8 at 66207.81197178511 bps.

Bitrate switch for 1920x1080@0.9 at 1658351.3268310914 bps. 1280x720 qual at br is 0.9324741017417775
Bitrate switch for 1280x720@0.9 at 989156.8165966908 bps. 640x480 qual at br is 0.9428834337863248
Bitrate switch for 640x480@0.9 at 485318.3305768017 bps. 320x240 qual at br is 0.9349399124018616
Minimum bitrate for 320x240@0.9 at 280510.36393845885 bps.

Bitrate switch for 1920x1080@0.95 at 3857779.601799102 bps. 1280x720 qual at br is 0.9628820330960579
Bitrate switch for 1280x720@0.95 at 2493719.9488699837 bps. 640x480 qual at br is 0.9737948824384565
Bitrate switch for 640x480@0.95 at 1163040.4454250892 bps. 320x240 qual at br is 0.9714908213551666
Minimum bitrate for 320x240@0.95 at 659464.021887705 bps.


# for minimum quality of SSIM 0.95 encoder needs to be operated on
# 659kbps - 1163kbps  at 320x240
# 1163kbps - 2493kbps at 640x480
# 2493kbps - 3857kbps     at 1280x720
# 3857kbps and above  at 1920x1080
 
```


## Reporting ##
CODECbench wouldn't be very useful if it didn't give you information about the actual performance of the codec under test. Even after running all the runs you end with bitstreams and metrics information this is not terribly useful per se. CODECbench can then generate reports on that compiled data. To get reports add a report section to the configuration file:

```javascript
{
    "sequence_dirs": ["../seq"],
    "codec_dirs" : ["../codecs"],
    "keeprecon" : false,
    "frame_count" : 300,
    "runs" : [
    {
        "seq" : ["foremancif"],
        "codec" : ["x265"],
        "bitrate_range" : [100,1000,50],
        "preset" : ["placebo","medium"]
    }
    ],
    "reports" : {
        "defaults" : {
            "res" : "640x480",
            "fontsize" : 8,
            "format" : "svg"
        },
        "reports": [
        {
            "ref" : 0.95,
            "metric" : "ssim"
        },
        {
        "ref" : 40,
        "metric" : "psnr"
        }
    ]
} 
}
```
This will produce the following SSIM report on the reports folder. The 'ref' marker on the reports array can be used for CODECbench to calculate the bitrate savings at a specific quality point. In the example we are using 0.95 for SSIM point at which the placebo configuration gives 26% bitrate savings.

![he](docs/images/ssim_report.png)


The configuration file also adds a PSNR report with a reference of 40. This is the result:
![he](docs/images/psnr_report.png)

Using PSNR gives us also 27% bitrate savings for a value of 40dB, not bad. We can do better though in our analysis. CODECbench can also automatically calculate the [CABSscore](http://codecbench.nelalabs.com/cabs) for this configuration. [Visit this page to learn more about the CABSscore](http://codecbench.nelalabs.com/cabs) . To get a CABSscore, we need to define a bitrate of interest so we'll go for a range between 400 and 1000 kbps for foreman CIF. Add a 'bitrate_range' parameter in the config file and also set the report to show the 'cabs_area' like this:
```javascript
 ...
     "reports" : {
         "defaults" : {
              "res" : "640x480",
              "fontsize" : 8,
              "format" : "svg",
              "bitrate_range": [400,1000],
              "cabs_area" : true
          },
          "reports": [
          {
...
```

This results in the following:

![he](docs/images/cabs_report.png)

The green area is the CABS area. Its the area between 400 and 1000 kbps from the reference curve (medium preset) and the bitrate savings for every point. The average bitrate savings in all this point is unsurprisingly 27% so our previous measurement at just 40dB was quite close to the real CABSscore.

## Codec Packs ##
A codec pack extends CODECbench to support a particular codec. From a user point of view they are just folders with files you can drop in into the 'codecpacks' folder. When you run CODECbench it should automatically detect it and be ready for use. Like sequences, codec packs are identified with a nickname. For example 'x264', 'x265' or 'libvpx'. You use their nickname to refer to them in configuration files.
### Writing your own codec pack ###
In its essense a codec pack is the binaries that form part of the encoder and a bit of python glue to interact with CODECbench. On startup CODECbench looks for a 'codec.py' file inside the folders of the 'codecpacks' directory. If present file is loaded and used for interaction with the codecpack. Take a look at the provided codec packs if you want to make your own, it should be relatively simple.
### Provided codec packs ###
Some codec packs are provided as default:
#### x264 ####
You use this codec pack adding:
* **codec** parameter with value 'x264'
* **preset** parameter with one of the x264 command line presets (ultrafast,fast,medium,slow,placebo ...)
* **bitrate** this is the sweep parameter that generates streams of different size

#### x265 ####
You use this codec pack adding:
* **codec** parameter with value 'x265'
* **preset** parameter with one of the x265 command line presets (ultrafast,fast,medium,slow,placebo ...)
* **bitrate** this is the sweep parameter that generates streams of different size

#### libvpx ####
You use this codec pack adding:
* **codec** parameter with value 'libvpx'
* **libvpx_codec** parameter telling the specific codec to use inside libvpx 'vp8' or 'vp9'
* **cpu** parameter mapped to command line. 0 for slow, 1 for faster, ... 16 for realtime
* **bitrate** this is the sweep parameter that generates streams of different size

## Configuration options ##
Here are a few of the configuration options you can use. The format of specification is like the following:  
```property : [values: (default)]{optional|required}```  
### Run options ###

* ```keeprecon      : [true|false (false)]{optional}```  
If true directs the codec pack to not delete the temporary yuv reconstructed sequences  

* ```frame_count   : [int (seq_frame_count)]{optional}```  
limits the number of frames to be encoded to the int number specified

* ```ignore    :[true|false (false)]{optional}```  
makes the configuration parser to ignore this particular configuration. It is sometimes useful while working on a setup to disable a particular set of configurations in the file. Setting "ignore":true, will achieve the effect of ignoring the selected configuration temporarily.

* ```clobber   : [true|false (false)]{optional}```  
deletes the destination directory of the run. Use this if you are having problems with specific runs and you want to start from fresh. For example:   
```javascript  
{
        "seq" : ["foreman4k","coastguard4k","cactus4k","mobile4k","suzie4k"],
        "codec" : ["x264"],
        "bitrate_range" : [1000,5000,250],
        "preset" : ["medium"],
        "ignore" : true,
        "clobber" : true
}
```   
Given ```ignore``` is set to true this configuration section will be ignored until you remove the parameter or set it to false. If set to false, it will also clobber the existing directory before doing every run.
###Reporting options###
The reports section has a defaults section that gets inherited by all others section. 

* ```res      : [int X int (1600x1200)]{optional}```  
The resolution of the report graphics

* ```fontsize      : [int (12)]{optional}```  
Size in points of font in report graphics

* ```format      : [pdf|svg|png (svg)]{optional}```  
The graphic format in which the graphics get produced

* ```cabs_area    : [true|false ]{optional}```  
Produces the cabs_area plot between two RD curves. 

* ```cabs_bitref_range    : [JSON_OBJECT ]{optional}```  
Dictonary that specifies the bitrate ranges where the CABSscore calculation is valid per squence. For example:
```javascript
...
            "cabs_bitref_range" : {
                "foreman4k" : [2500,4000],
                "coastguard4k" :[1000,4000], 
                "suzie4k" : [2500,4000],
                "cactus4k" : [3000,5000],
                "mobile4k" : [2500,4000]
            }
...
```
Defines the ```bitref_range``` per sequence

* ```metric    : [ssim|psnr ]{optional}```  
Metric to be used for the report

* ```seqref    : [JSON_OBJECT ]{optional}```  
If defined, defines the points of reference for every metric that will be used to calculate bitrate savings on graphics. Also, this is used to automatically calculate CABSscore using this point of reference to figure out the worst performing RD curve to which other curves CABSscore will be calculated against. An example:
```javascript
...
            "metric" : "ssim",
            "seqref" : {
                "foreman4k" : 0.99,
                "coastguard4k" : 0.94,
                "suzie4k" : 0.994,
                "cactus4k" : 0.991,
                "mobile4k" : 0.990

            }
...
```
This defines the points of reference for SSIM metric for every sequence.



## Requirements ##
* **python3** was used to write CODECbench so you'll require a python3 install
* **matplotlib, scipy and numpy** are required if you want to generate reports
* **a codec pack for your native platform**, codec packs run natively and usually come with binaries to be run on most common platforms. A codec pack won't run if it doesn't provide native binaries for your platform

## About me ##
My name is Alberto Vigata and I love all things video engineering related. I've been working on them profesionally for a while. You can [check my personal profile on Linked In](https://www.linkedin.com/in/vigata)

