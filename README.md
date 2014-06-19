codecBENCH
==========

## An open source video codec benchmarking tool ##

codecBENCH is a video codec comparison tool. It allows you to analize how one video codec performs against another.

You start by defining what stuff you want to analyize. For example, let's compare how x264 performs with its different presets 'medium', 'slow' and 'placebo'. For this we will create a JSON configuration file like the following:

```javascript
// we'll keep this on a file called x264bench.json
{
  "keeprecon" : false,
  "frame_count" : 300,
  "runs" : [
  {
    "seq" : ["foremancif"],
    "codec" : ["x264"],
    "bitrate" : [250,400,600,800,1000],
    "preset" : ["medium","slow","placebo"]
  }
  ]
}
```

Notice the 'runs' section. It specifies to use the x264 codec and a range of bitrates from 250kbps to 1000kbps on the foremancif sequence. Also, the range of presets of interest is defined.

Now you run this with codecbench:
```
codecbench -i x264bench.json
```

Here some magic happens. 

```
loading x264bench.json
expanded to 15 runs
running bitrate_250__codec_x264__preset_medium__seq_foremancif__ 0/15
running bitrate_400__codec_x264__preset_medium__seq_foremancif__ 1/15
running bitrate_600__codec_x264__preset_medium__seq_foremancif__ 2/15
...
```

codecBENCH figures out all possible combinations of this configuration and actually encodes the sequence in every one settings. Every settings is a 'run'. This can take a while, but a subdirectory 'runs' is created in where your config file is and the resulting bitstream and video metrics information is written there for later. 

You don't have to worry about configuring the codecs at all. codecBENCH is modular, and the codecs are provided to you (there are some installed by default) as 'codec packs'. Codec packs have all its needed to interact with codecBENCH and you can just invoke them on the configuration file with their nickname, in the example above 'x264'. You just need to drop the codec pack in the 'codecpacks' folder for this to work.

Sequences are similar. You can drop prepared yuv sequences on the sequences directory and use them with their nickname. All the details about formats, framesizes and frame rates are handled automatically.

## Now, give me some data ##
Even when after running all the runs you end with bitstreams and metrics information this is not terribly useful per se. codecBENCH can then generate reports on that compiled data. For the example above you could get the following:

TODO
